"""The corpus-check lane's decisions (``fedcourtsai.corpus_check``).

Who may ask, what may run, which request is next, and what the comment says —
each tested here without the Actions API, so the workflow only routes on the
answers. The workflow's own shape is pinned in ``test_workflow_corpus_check``.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus_check as cc
from fedcourtsai.cli import app

REPO = "ModelMirrorAI/fedcourtsai"
SHA = "a" * 40
SHA2 = "b" * 40
BASE = "c" * 40


def _pr(
    number: int,
    *,
    body: str | None = "```corpus-check\nuv run fedcourts corpus-info\n```",
    author: str = "modelmirror-agent",
    head_repo: str | None = REPO,
    sha: str = SHA,
    created_at: str = "2026-10-01T00:00:00Z",
    draft: bool | None = False,
    base_ref: str = "staging",
) -> dict[str, Any]:
    pr: dict[str, Any] = {
        "number": number,
        "body": body,
        "user": {"login": author, "type": "User"},
        "head": {"sha": sha, "repo": {"full_name": head_repo} if head_repo else None},
        "base": {"ref": base_ref, "sha": BASE, "repo": {"full_name": REPO}},
        "created_at": created_at,
    }
    if draft is not None:
        pr["draft"] = draft
    return pr


def _comment(body: str, *, login: str = cc.BOT_LOGIN, kind: str = "Bot") -> dict[str, Any]:
    return {"body": body, "user": {"login": login, "type": kind}}


# --- the request block ----------------------------------------------------


def test_a_block_yields_its_one_line() -> None:
    body = "Intro\n\n```corpus-check\n  uv run fedcourts corpus-info  \n```\nmore"
    assert cc.extract_block(body) == "uv run fedcourts corpus-info"


def test_crlf_bodies_and_longer_fences_are_read() -> None:
    body = "x\r\n````corpus-check\r\nuv run fedcourts stats\r\n\r\n````\r\n"
    assert cc.extract_block(body) == "uv run fedcourts stats"


def test_no_block_is_no_request() -> None:
    assert cc.extract_block(None) is None
    assert cc.extract_block("```python\nprint(1)\n```") is None
    # An info string that merely starts with the name is another block.
    assert cc.extract_block("```corpus-checks\nuv run fedcourts x\n```") is None


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        ("```corpus-check\nuv run fedcourts a\n", "never closed"),
        ("```corpus-check\nuv run fedcourts a\nuv run fedcourts b\n```", "2 non-blank"),
        ("```corpus-check\n\n```", "0 non-blank"),
        (
            "```corpus-check\nuv run fedcourts a\n```\n```corpus-check\nuv run fedcourts b\n```",
            "more than one",
        ),
    ],
)
def test_an_unreadable_block_is_refused(body: str, reason: str) -> None:
    with pytest.raises(cc.CommandRefused, match=reason):
        cc.extract_block(body)


def test_a_shorter_fence_inside_does_not_close_the_block() -> None:
    body = "````corpus-check\n```\n````"
    # The inner ``` is the one line, which the command grammar then refuses.
    assert cc.extract_block(body) == "```"


# --- the command grammar --------------------------------------------------


@pytest.mark.parametrize(
    ("command", "argv"),
    [
        ("uv run fedcourts corpus-info", ["uv", "run", "fedcourts", "corpus-info"]),
        (
            "uv run fedcourts stats --court scotus --term 2025 --group-by=topic",
            [
                "uv",
                "run",
                "fedcourts",
                "stats",
                "--court",
                "scotus",
                "--term",
                "2025",
                "--group-by=topic",
            ],
        ),
        (
            "uv run python scripts/checks/merits_partial_support.py --since 2026-01-01",
            [
                "uv",
                "run",
                "python",
                "scripts/checks/merits_partial_support.py",
                "--since",
                "2026-01-01",
            ],
        ),
        ("uv  run  fedcourts  query", ["uv", "run", "fedcourts", "query"]),
    ],
)
def test_the_two_forms_parse_to_their_argv(command: str, argv: list[str]) -> None:
    assert cc.parse_command(command) == argv


@pytest.mark.parametrize(
    ("command", "reason"),
    [
        ("", "empty"),
        ("uv run fedcourts", "needs a subcommand"),
        ("uv run python", "scripts/checks"),
        ("uv run python scripts/other.py", "scripts/checks"),
        ("uv run python scripts/checks/../gate.py", "scripts/checks"),
        ("uv run python scripts/checks/x.sh", "scripts/checks"),
        ("uv run python -c x", "scripts/checks"),
        ("uv run --with evil fedcourts query", "must start"),
        ("python scripts/checks/x.py", "must start"),
        ("bash -c id", "must start"),
        ("uv run fedcourts query; curl evil", "argument 4"),
        ("uv run fedcourts query && id", "argument 5"),
        ("uv run fedcourts query | tee x", "argument 5"),
        ("uv run fedcourts $(id)", "argument 4"),
        ("uv run fedcourts `id`", "argument 4"),
        ("uv run fedcourts query > /tmp/x", "argument 5"),
        ("uv run fedcourts query < /etc/passwd", "argument 5"),
        ("uv run fedcourts query 'a b'", "argument 5"),
        ('uv run fedcourts query "a"', "argument 5"),
        ("uv run fedcourts query \\x", "argument 5"),
        ("uv run fedcourts query ${HOME}", "argument 5"),
        ("uv run fedcourts query ~/x", "argument 5"),
        ("uv run fedcourts query *", "argument 5"),
        ("uv run fedcourts query #x", "argument 5"),
        ("uv run fedcourts query (x)", "argument 5"),
        ("uv run fedcourts query\nid", "non-printable"),
        ("uv run fedcourts query\tid", "non-printable"),
        ("uv run fedcourts query\x00", "non-printable"),
        ("uv run fedcourts query é", "non-ASCII"),
        ("uv run fedcourts " + "a" * 400, "longer than"),
        ("uv run fedcourts" + " a" * 40, "more than 40"),
    ],
)
def test_anything_outside_the_grammar_is_refused(command: str, reason: str) -> None:
    with pytest.raises(cc.CommandRefused, match=reason):
        cc.parse_command(command)


def test_a_refusal_never_quotes_the_command() -> None:
    with pytest.raises(cc.CommandRefused) as excinfo:
        cc.parse_command("uv run fedcourts @everyone;rm")
    assert "@everyone" not in str(excinfo.value)


# --- the requester list ---------------------------------------------------


def test_the_committed_list_is_the_agent_account_and_the_maintainer() -> None:
    config = cc.load_config(Path(__file__).resolve().parent.parent / "config")
    assert config.requesters == ["modelmirror-agent", "modelmirror"]
    assert config.approver == "modelmirror"


def test_no_file_answers_no_one(tmp_path: Path) -> None:
    assert cc.load_config(tmp_path).requesters == []


def test_a_malformed_login_is_refused_at_load(tmp_path: Path) -> None:
    (tmp_path / cc.CONFIG_FILENAME).write_text("requesters: ['not a login']\n")
    with pytest.raises(ValueError, match="not a GitHub login"):
        cc.load_config(tmp_path)


# --- candidates and selection ---------------------------------------------

LISTED = ["modelmirror-agent", "modelmirror"]


def test_only_listed_same_repository_authors_are_candidates() -> None:
    prs = [
        _pr(1),
        _pr(2, author="outsider"),
        _pr(3, head_repo="someone/fork"),
        _pr(4, head_repo=None),
        _pr(5, body="no block here"),
        _pr(6, author="ModelMirror"),  # logins compare case-insensitively
    ]
    requests, passed = cc.candidate_requests(prs, repo=REPO, requesters=LISTED)
    assert [r.pr for r in requests] == [1, 6]
    assert {(p.pr, p.reason) for p in passed} == {
        (2, "author is not on the requester list"),
        (3, "head is not in this repository"),
        (4, "head is not in this repository"),
    }


def test_an_empty_list_passes_everyone_over() -> None:
    requests, passed = cc.candidate_requests([_pr(1)], repo=REPO, requesters=[])
    assert requests == []
    assert [p.pr for p in passed] == [1]


def test_a_listed_author_with_a_bad_command_is_kept_refused() -> None:
    prs = [_pr(1, body="```corpus-check\nrm -rf /\n```"), _pr(2, body="```corpus-check\n")]
    requests, _ = cc.candidate_requests(prs, repo=REPO, requesters=LISTED)
    assert [(r.pr, r.command) for r in requests] == [(1, None), (2, None)]
    assert all(r.refusal for r in requests)


def test_an_unlisted_author_with_a_bad_block_is_passed_over_silently() -> None:
    requests, passed = cc.candidate_requests(
        [_pr(1, author="outsider", body="```corpus-check\n")], repo=REPO, requesters=LISTED
    )
    assert requests == []
    assert passed[0].reason == "author is not on the requester list"


def test_a_draft_is_passed_over_and_an_unread_draft_state_counts_as_one() -> None:
    requests, passed = cc.candidate_requests(
        [_pr(1, draft=True), _pr(2, draft=None), _pr(3)], repo=REPO, requesters=LISTED
    )
    assert [r.pr for r in requests] == [3]
    assert [(p.pr, p.reason) for p in passed] == [
        (1, "draft (or draft state unread)"),
        (2, "draft (or draft state unread)"),
    ]


def test_the_base_sha_is_pinned_with_the_request() -> None:
    requests, _ = cc.candidate_requests([_pr(1)], repo=REPO, requesters=LISTED)
    assert requests[0].base_sha == BASE


def test_an_unreadable_head_sha_is_passed_over() -> None:
    _, passed = cc.candidate_requests([_pr(1, sha="nothex")], repo=REPO, requesters=LISTED)
    assert passed[0].reason == "head SHA unreadable"


def test_candidates_are_oldest_first() -> None:
    prs = [
        _pr(9, created_at="2026-10-03T00:00:00Z"),
        _pr(7, created_at="2026-10-01T00:00:00Z"),
        _pr(8, created_at="2026-10-01T00:00:00Z"),
    ]
    requests, _ = cc.candidate_requests(prs, repo=REPO, requesters=LISTED)
    assert [r.pr for r in requests] == [7, 8, 9]


def test_pages_flatten_to_their_objects() -> None:
    assert [p["number"] for p in cc.flatten_pages([[_pr(1), _pr(2)], [_pr(3)]])] == [1, 2, 3]
    assert [p["number"] for p in cc.flatten_pages([_pr(1)])] == [1]
    assert cc.flatten_pages([]) == []


def test_only_the_bots_marker_for_this_sha_answers_it() -> None:
    marker = cc.result_marker(SHA)
    assert cc.is_answered([_comment(marker + "\nresult")], SHA)
    # The same marker from a person, or from a user wearing the bot's login
    # type, or for another SHA, or not leading the comment, does not count.
    assert not cc.is_answered([_comment(marker, login="modelmirror", kind="User")], SHA)
    assert not cc.is_answered([_comment(marker, kind="User")], SHA)
    assert not cc.is_answered([_comment(marker, login="other-app[bot]")], SHA)
    assert not cc.is_answered([_comment(cc.result_marker(SHA2))], SHA)
    assert not cc.is_answered([_comment("quoting " + marker)], SHA)


def test_selection_skips_answered_heads_and_takes_the_oldest_left() -> None:
    requests, _ = cc.candidate_requests(
        [
            _pr(1, created_at="2026-10-01T00:00:00Z"),
            _pr(2, sha=SHA2, created_at="2026-10-02T00:00:00Z"),
        ],
        repo=REPO,
        requesters=LISTED,
    )
    answered = {1: [_comment(cc.result_marker(SHA))], 2: []}
    chosen = cc.select_request(requests, answered)
    assert chosen is not None
    assert chosen.pr == 2
    # A new push to PR 1 is a new head with no result: it is asked again.
    requests[0] = requests[0].model_copy(update={"sha": "c" * 40})
    chosen = cc.select_request(requests, answered)
    assert chosen is not None
    assert chosen.pr == 1


def test_everything_answered_selects_nothing() -> None:
    requests, _ = cc.candidate_requests([_pr(1)], repo=REPO, requesters=LISTED)
    assert cc.select_request(requests, {1: [_comment(cc.result_marker(SHA))]}) is None


def test_unread_comments_are_an_error_not_unanswered() -> None:
    requests, _ = cc.candidate_requests([_pr(1)], repo=REPO, requesters=LISTED)
    with pytest.raises(KeyError):
        cc.select_request(requests, {})


def test_plan_outputs_are_single_lines(tmp_path: Path) -> None:
    requests, _ = cc.candidate_requests([_pr(3)], repo=REPO, requesters=LISTED)
    outputs = cc.plan_outputs(requests[0])
    assert outputs == {
        "found": "true",
        "pr": "3",
        "sha": SHA,
        "author": "modelmirror-agent",
        "command": "uv run fedcourts corpus-info",
        "refusal": "",
    }
    assert cc.plan_outputs(None) == {"found": "false"}
    out = tmp_path / "out"
    cc.write_outputs(out, outputs)
    assert out.read_text().splitlines()[0] == "found=true"
    with pytest.raises(ValueError, match="single line"):
        cc.write_outputs(out, {"x": "a\nb"})


# --- rendering ------------------------------------------------------------


def test_the_fence_outruns_any_backtick_run() -> None:
    fenced = cc.fence("a ````` b")
    assert fenced.startswith("``````text\n")
    assert fenced.endswith("\n``````")
    assert cc.fence("plain").startswith("```text\n")


def test_mentions_are_broken() -> None:
    assert "@everyone" not in cc.neutralize_mentions("ping @everyone and @org/team")
    assert cc.neutralize_mentions("no at sign") == "no at sign"


def test_clamping_cuts_on_a_character_boundary() -> None:
    text, clamped = cc.clamp_utf8("é" * 10, 5)
    assert clamped
    assert text == "éé"
    assert cc.clamp_utf8("short", 50) == ("short", False)


def test_the_plan_summary_names_what_approval_runs() -> None:
    requests, passed = cc.candidate_requests(
        [
            _pr(4, body="```corpus-check\nuv run fedcourts query --court scotus\n```"),
            _pr(5, author="x"),
        ],
        repo=REPO,
        requesters=LISTED,
    )
    commit = cc.head_commit(
        {
            "author": {"login": "someone-else"},
            "committer": None,
            "commit": {
                "author": {"name": "Someone"},
                "committer": {"name": "Plain `Git` @team"},
                "verification": {"verified": False, "reason": "unsigned"},
            },
        }
    )
    summary = cc.render_plan_summary(
        requests[0],
        passed,
        server_url="https://github.com",
        repo=REPO,
        candidates=1,
        commit=commit,
    )
    assert "**PR #4**" in summary
    assert f"pinned at head `{SHA}`" in summary
    assert "`modelmirror-agent`" in summary
    assert "```text\nuv run fedcourts query --court scotus\n```" in summary
    # The diff is pinned to the SHA, never the PR's moving files page.
    assert f"https://github.com/{REPO}/compare/{BASE}...{SHA}" in summary
    assert "/files" not in summary
    assert "author `someone-else`" in summary
    assert "`Plain 'Git' @\u200bteam (no GitHub account)`" in summary
    assert "signature not verified (`unsigned`)" in summary
    assert "`uv sync --locked`" in summary
    assert "`pyproject.toml`, `uv.lock`" in summary
    assert f"If the PR's head is no longer `{SHA}`, reject" in summary
    assert "- #5: author is not on the requester list" in summary


def test_the_plan_summary_neutralises_the_base_ref() -> None:
    requests, _ = cc.candidate_requests(
        [_pr(4, base_ref="x`@org/team\u202e")], repo=REPO, requesters=LISTED
    )
    summary = cc.render_plan_summary(
        requests[0], [], server_url="https://github.com", repo=REPO, candidates=1
    )
    assert "into `x'@\u200borg/team`" in summary
    assert "\u202e" not in summary


def test_an_unprotected_environment_plans_nothing_and_says_why() -> None:
    summary = cc.render_plan_summary(
        None,
        [],
        server_url="https://github.com",
        repo=REPO,
        candidates=1,
        environment_problems=["no required-reviewer rule names the approver `modelmirror`"],
    )
    assert "Nothing is planned" in summary
    assert "approver" in summary


def test_an_unread_head_commit_is_said_to_be_unread() -> None:
    assert cc.head_commit(None) == cc.HeadCommit()
    requests, _ = cc.candidate_requests([_pr(4)], repo=REPO, requesters=LISTED)
    summary = cc.render_plan_summary(
        requests[0], [], server_url="https://github.com", repo=REPO, candidates=1
    )
    assert "author `(unread)`" in summary
    assert "signature state unread" in summary


def test_bidi_and_zero_width_characters_are_dropped() -> None:
    text = "a\u200bb\u200fc\u202ad\u202ee\u2066f\u2069g\ufeffh"
    assert cc.inline(text) == "abcdefgh"


def test_the_plan_summary_for_a_refusal_and_for_nothing() -> None:
    requests, _ = cc.candidate_requests(
        [_pr(4, body="```corpus-check\nrm x\n```")], repo=REPO, requesters=LISTED
    )
    refused = cc.render_plan_summary(
        requests[0], [], server_url="https://github.com", repo=REPO, candidates=1
    )
    assert "**refused**" in refused
    assert "rm x" not in refused
    nothing = cc.render_plan_summary(
        None, [], server_url="https://github.com", repo=REPO, candidates=2
    )
    assert "No request to answer" in nothing


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def _inputs(**overrides: str) -> cc.PostInputs:
    values = {
        "sha": SHA,
        "command": "uv run fedcourts corpus-info",
        "refusal": "",
        "run_result": "success",
        "exit_code": "0",
        "timed_out": "false",
        "summary_b64": _b64("rows: 42"),
        "vintage_b64": _b64("blob sha256 abc\nfreshness: latest pull 2026-10-14"),
        "run_url": "https://github.com/o/r/actions/runs/1",
    }
    values.update(overrides)
    return cc.PostInputs(**values)


def test_a_comment_leads_with_the_marker_and_names_sha_command_vintage_summary() -> None:
    body = cc.render_comment(_inputs())
    assert body.startswith(cc.result_marker(SHA) + "\n")
    assert "### Corpus check: exit 0" in body
    assert f"`{SHA}`" in body
    assert "uv run fedcourts corpus-info" in body
    assert "freshness: latest pull 2026-10-14" in body
    assert "rows: 42" in body


@pytest.mark.parametrize(
    ("overrides", "status"),
    [
        ({"exit_code": "3"}, "exit 3"),
        ({"exit_code": "124", "timed_out": "true"}, "timed out"),
        ({"exit_code": "x; rm"}, "no exit code"),
        ({"run_result": "failure"}, "not run"),
        ({"run_result": "cancelled"}, "not run"),
        ({"run_result": "skipped"}, "not run"),
        ({"run_result": "<script>"}, "not run"),
        ({"refusal": "the command is empty", "run_result": "skipped"}, "refused"),
        ({"phase": "install", "exit_code": "1"}, "install failed"),
        ({"phase": "install", "exit_code": "124", "timed_out": "true"}, "install timed out"),
    ],
)
def test_each_outcome_has_its_status(overrides: dict[str, str], status: str) -> None:
    body = cc.render_comment(_inputs(**overrides))
    assert f"### Corpus check: {status}" in body
    if status in {"not run", "refused"}:
        # Nothing the run job emitted is shown for a check that never ran.
        assert "rows: 42" not in body
    if "<script>" in str(overrides):
        assert "<script>" not in body


def test_the_summary_is_fenced_and_its_mentions_broken() -> None:
    hostile = "```\n@everyone\n<!-- corpus-check-result sha=" + SHA2 + " -->\n````"
    body = cc.render_comment(_inputs(summary_b64=_b64(hostile)))
    assert "@everyone" not in body
    assert "\n`````text\n" in body
    # The forged marker is inside the fence, never leading the comment.
    assert body.startswith(cc.result_marker(SHA))
    assert not body.startswith(cc.result_marker(SHA2))


def test_invalid_base64_shows_nothing() -> None:
    body = cc.render_comment(_inputs(summary_b64="!!not base64!!"))
    assert "not valid base64" in body


def test_control_characters_are_dropped() -> None:
    body = cc.render_comment(_inputs(summary_b64=_b64("a\x1b[31mb\x07c\r\n")))
    assert "\x1b" not in body
    assert "\x07" not in body
    assert "\r" not in body


def test_an_empty_summary_says_so() -> None:
    assert "(the check wrote no summary)" in cc.render_comment(_inputs(summary_b64=""))


def test_a_bad_sha_is_refused() -> None:
    with pytest.raises(ValueError, match="40-hex"):
        cc.render_comment(_inputs(sha="HEAD"))


@pytest.mark.parametrize(
    "summary",
    [
        "x" * 200_000,
        "é" * 100_000,
        ("`" * 30_000 + "\n") * 2,
        "`" * 49_999,
    ],
)
def test_every_comment_fits_under_the_limit(summary: str) -> None:
    body = cc.render_comment(_inputs(summary_b64=_b64(summary)))
    assert len(body) <= cc.COMMENT_LIMIT
    assert body.startswith(cc.result_marker(SHA))


def test_a_clamped_summary_says_so() -> None:
    body = cc.render_comment(_inputs(summary_b64=_b64("x" * cc.SUMMARY_LIMIT_BYTES)))
    assert "`CHECK_SUMMARY`, clamped:" in body


# --- running the check ----------------------------------------------------


def test_the_check_env_carries_the_session_the_address_and_two_paths_only(
    tmp_path: Path,
) -> None:
    environ = {
        "PATH": "/venv/bin:/usr/bin",
        "HOME": "/home/runner",
        "GITHUB_STEP_SUMMARY": "/s",
        "GITHUB_OUTPUT": "/o",
        "GITHUB_ENV": "/e",
        "GITHUB_TOKEN": "ghs_x",
        "ACTIONS_ID_TOKEN_REQUEST_URL": "u",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "t",
        "ACTIONS_RUNTIME_TOKEN": "r",
        "AWS_ACCESS_KEY_ID": "AKIA",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_SESSION_TOKEN": "session",
        "AWS_REGION": "us-east-1",
        "FEDCOURTS_CORPUS_BASE_URL": "s3://b/p",
    }
    env = cc.check_env(environ, summary_path=tmp_path / "s.md", corpus_root=tmp_path / "corpus")
    assert env == {
        "AWS_ACCESS_KEY_ID": "AKIA",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_SESSION_TOKEN": "session",
        "AWS_REGION": "us-east-1",
        "FEDCOURTS_CORPUS_BASE_URL": "s3://b/p",
        "CHECK_SUMMARY": str(tmp_path / "s.md"),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),
    }


def test_the_account_hop_carries_only_the_named_variables() -> None:
    argv = cc.as_user(
        ["uv", "sync", "--locked"],
        user="corpuscheck",
        workdir=Path("/home/corpuscheck/check"),
        env_names={"CHECK_SUMMARY": "x", "AWS_REGION": "y"},
    )
    assert argv == [
        "sudo",
        "-n",
        "--preserve-env=AWS_REGION,CHECK_SUMMARY",
        "-u",
        "corpuscheck",
        "-H",
        "--",
        "/usr/bin/env",
        "-C",
        "/home/corpuscheck/check",
        "uv",
        "sync",
        "--locked",
    ]


@pytest.mark.parametrize(
    ("user", "workdir", "names", "match"),
    [
        ("root;id", "/w", ["A"], "account"),
        ("Corpus", "/w", ["A"], "account"),
        ("corpuscheck", "relative", ["A"], "absolute"),
        ("corpuscheck", "/w", [], "identifiers"),
        ("corpuscheck", "/w", ["A,B"], "identifiers"),
        ("corpuscheck", "/w", ["lower"], "identifiers"),
    ],
)
def test_the_account_hop_refuses_malformed_inputs(
    user: str, workdir: str, names: list[str], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        cc.as_user(["x"], user=user, workdir=Path(workdir), env_names=names)


def test_the_summary_is_redacted_and_clamped() -> None:
    raw = b"key=AKIAEXAMPLEKEY123 url=s3://bucket/prefix short=abc"
    text, clamped = cc.summary_text(raw, redact=["AKIAEXAMPLEKEY123", "s3://bucket/prefix", "abc"])
    assert text == "key=[redacted] url=[redacted] short=abc"
    assert not clamped
    text, clamped = cc.summary_text(b"y" * (cc.SUMMARY_LIMIT_BYTES + 10))
    assert clamped
    assert len(text) == cc.SUMMARY_LIMIT_BYTES


def _py(code: str) -> list[str]:
    return [sys.executable, "-c", code]


def test_a_check_runs_without_a_shell_and_its_output_stays_in_a_file(tmp_path: Path) -> None:
    out = tmp_path / "out" / "log"
    env = {"PATH": os.environ.get("PATH", ""), "CHECK_SUMMARY": str(tmp_path / "s.md")}
    code = (
        "import os,sys; print('to stdout'); print('to stderr', file=sys.stderr);"
        "open(os.environ['CHECK_SUMMARY'],'w').write('summary $(id) ;');"
        "sys.exit(3)"
    )
    result = cc.run_check(_py(code), cwd=tmp_path, env=env, timeout_seconds=30, output_path=out)
    assert result == cc.CheckResult(exit_code=3, timed_out=False, output_bytes=out.stat().st_size)
    assert "to stdout" in out.read_text()
    assert "to stderr" in out.read_text()
    # No shell expanded anything the check wrote or was given.
    assert (tmp_path / "s.md").read_text() == "summary $(id) ;"


def test_a_check_holds_no_descriptor_but_its_output(tmp_path: Path) -> None:
    code = "import os; print(sorted(int(f) for f in os.listdir('/proc/self/fd')))"
    out = tmp_path / "log"
    cc.run_check(_py(code), cwd=tmp_path, env=dict(os.environ), timeout_seconds=30, output_path=out)
    # stdin (devnull), stdout and stderr (the file), and the listing's own fd.
    assert json.loads(out.read_text().strip()) == [0, 1, 2, 3]


def test_a_check_past_its_timeout_is_killed_with_its_group(tmp_path: Path) -> None:
    marker = tmp_path / "child-alive"
    script = tmp_path / "slow.py"
    script.write_text(
        "import subprocess, sys, time\n"
        + "child = 'import pathlib, sys, time; time.sleep(3); pathlib.Path(sys.argv[1]).touch()'\n"
        + "subprocess.Popen([sys.executable, '-c', child, sys.argv[1]])\n"
        + "time.sleep(60)\n"
    )
    started = time.monotonic()
    result = cc.run_check(
        [sys.executable, str(script), str(marker)],
        cwd=tmp_path,
        env=dict(os.environ),
        timeout_seconds=1,
        output_path=tmp_path / "log",
    )
    assert result.timed_out, (tmp_path / "log").read_text()
    assert result.exit_code == cc.TIMEOUT_EXIT
    assert time.monotonic() - started < 30
    time.sleep(4)
    assert not marker.exists(), "a background child outlived the check"


def test_a_check_that_cannot_start_reports_127(tmp_path: Path) -> None:
    result = cc.run_check(
        ["/nonexistent/uv", "run"],
        cwd=tmp_path,
        env={},
        timeout_seconds=5,
        output_path=tmp_path / "log",
    )
    assert result.exit_code == cc.NOT_FOUND_EXIT
    assert not result.timed_out


def test_a_failed_install_stops_before_the_check(tmp_path: Path) -> None:
    ran = tmp_path / "check-ran"
    phase = cc.run_phases(
        install_argv=_py("import sys; print('install'); sys.exit(2)"),
        check_argv=_py(f"open({str(ran)!r}, 'w')"),
        cwd=tmp_path,
        env=dict(os.environ),
        install_timeout_seconds=30,
        check_timeout_seconds=30,
        output_path=tmp_path / "log",
    )
    assert phase.phase == "install"
    assert phase.result.exit_code == 2
    assert not ran.exists()


def test_each_phase_has_its_own_timeout_and_shares_the_output(tmp_path: Path) -> None:
    phase = cc.run_phases(
        install_argv=_py("print('installed')"),
        check_argv=_py("import time; print('checking', flush=True); time.sleep(30)"),
        cwd=tmp_path,
        env=dict(os.environ),
        install_timeout_seconds=30,
        check_timeout_seconds=1,
        output_path=tmp_path / "log",
    )
    assert phase.phase == "check"
    assert phase.result.timed_out
    assert (tmp_path / "log").read_text().split() == ["installed", "checking"]


def test_run_outputs_encode_the_summary() -> None:
    phase = cc.PhaseResult(phase="check", result=cc.CheckResult(0, False, 0))
    outputs = cc.run_outputs(phase, "line one\nline two")
    assert outputs["phase"] == "check"
    assert outputs["exit_code"] == "0"
    assert outputs["timed_out"] == "false"
    assert base64.b64decode(outputs["summary_b64"]).decode() == "line one\nline two"
    assert "\n" not in outputs["summary_b64"]


# --- the CLI seams --------------------------------------------------------


PROTECTED = {
    "protection_rules": [
        {
            "type": "required_reviewers",
            "reviewers": [{"type": "User", "reviewer": {"login": "modelmirror", "id": 7}}],
        },
        {"type": "branch_policy"},
    ],
    "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True},
}
MAIN_ONLY = {"total_count": 1, "branch_policies": [{"name": "main", "type": "branch"}]}


def _plan_args(tmp_path: Path, prs: Path, comments: Path) -> list[str]:
    return [
        "corpus-check-plan",
        "--prs-file",
        str(prs),
        "--repo",
        REPO,
        "--comments-dir",
        str(comments),
        "--environment-file",
        str(tmp_path / "environment.json"),
        "--branch-policies-file",
        str(tmp_path / "branch-policies.json"),
        "--commits-dir",
        str(tmp_path / "commits"),
        "--github-output",
        str(tmp_path / "gh-output"),
        "--summary-file",
        str(tmp_path / "summary.md"),
    ]


def _plan_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    config = tmp_path / "config"
    config.mkdir()
    (config / cc.CONFIG_FILENAME).write_text(
        "requesters: [modelmirror-agent]\napprover: modelmirror\n"
    )
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    prs = tmp_path / "prs.json"
    prs.write_text(json.dumps([[_pr(1), _pr(2, sha=SHA2, author="outsider")]]))
    comments = tmp_path / "comments"
    comments.mkdir()
    (comments / "1.json").write_text(json.dumps([[]]))
    (tmp_path / "commits").mkdir()
    (tmp_path / "commits" / f"{SHA}.json").write_text(
        json.dumps({"author": {"login": "modelmirror-agent"}, "commit": {}})
    )
    (tmp_path / "environment.json").write_text(json.dumps(PROTECTED))
    (tmp_path / "branch-policies.json").write_text(json.dumps(MAIN_ONLY))
    return prs, comments


def test_the_plan_cli_picks_writes_outputs_and_the_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prs, comments = _plan_fixture(tmp_path, monkeypatch)
    runner = CliRunner()
    listed = runner.invoke(app, ["corpus-check-candidates", "--prs-file", str(prs), "--repo", REPO])
    assert listed.exit_code == 0, listed.output
    assert listed.output.splitlines() == [f"1 {SHA}"]

    result = runner.invoke(app, _plan_args(tmp_path, prs, comments))
    assert result.exit_code == 0, result.output
    assert json.loads(result.output.strip().splitlines()[-1])["pr"] == 1
    assert f"sha={SHA}" in (tmp_path / "gh-output").read_text().splitlines()
    summary = (tmp_path / "summary.md").read_text()
    assert "**PR #1**" in summary
    assert "author `modelmirror-agent`" in summary

    (comments / "1.json").unlink()
    assert runner.invoke(app, _plan_args(tmp_path, prs, comments)).exit_code != 0


@pytest.mark.parametrize(
    ("environment", "policies"),
    [
        (None, MAIN_ONLY),
        ({**PROTECTED, "protection_rules": [{"type": "branch_policy"}]}, MAIN_ONLY),
        (PROTECTED, None),
        (PROTECTED, {"branch_policies": [{"name": "*", "type": "branch"}]}),
    ],
)
def test_the_plan_cli_plans_nothing_while_the_environment_is_unprotected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    environment: dict[str, Any] | None,
    policies: dict[str, Any] | None,
) -> None:
    prs, comments = _plan_fixture(tmp_path, monkeypatch)
    for name, document in (("environment.json", environment), ("branch-policies.json", policies)):
        if document is None:
            (tmp_path / name).unlink()
        else:
            (tmp_path / name).write_text(json.dumps(document))
    result = CliRunner().invoke(app, _plan_args(tmp_path, prs, comments))
    assert result.exit_code == 0, result.output
    assert (tmp_path / "gh-output").read_text().splitlines() == ["found=false"]
    assert "Nothing is planned" in (tmp_path / "summary.md").read_text()


def test_the_exec_cli_refuses_a_command_outside_the_grammar(tmp_path: Path) -> None:
    base = [
        "corpus-check-exec",
        "--user",
        "corpuscheck",
        "--workdir",
        str(tmp_path),
        "--corpus-root",
        str(tmp_path),
        "--output-file",
        str(tmp_path / "log"),
        "--command",
    ]
    result = CliRunner().invoke(app, [*base, "uv run fedcourts query; id"])
    assert result.exit_code == 1
    assert not (tmp_path / "log").exists()
    relative = [*base, "uv run fedcourts corpus-info"]
    relative[relative.index("--workdir") + 1] = "check"
    assert CliRunner().invoke(app, relative).exit_code == 1


def test_the_approver_cli_prints_the_configured_login(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(tmp_path))
    assert CliRunner().invoke(app, ["corpus-check-approver"]).exit_code == 1
    (tmp_path / cc.CONFIG_FILENAME).write_text("approver: modelmirror\n")
    result = CliRunner().invoke(app, ["corpus-check-approver"])
    assert result.output.strip() == "modelmirror"


def test_the_comment_cli_reads_its_inputs_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHECK_SHA", SHA)
    monkeypatch.setenv("CHECK_COMMAND", "uv run fedcourts corpus-info")
    monkeypatch.setenv("RUN_RESULT", "success")
    monkeypatch.setenv("CHECK_EXIT_CODE", "0")
    monkeypatch.setenv("CHECK_PHASE", "check")
    monkeypatch.setenv("CHECK_SUMMARY_B64", _b64("ok"))
    result = CliRunner().invoke(app, ["corpus-check-comment"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith(cc.result_marker(SHA))
    monkeypatch.setenv("CHECK_SHA", "nope")
    assert CliRunner().invoke(app, ["corpus-check-comment"]).exit_code == 1


def test_the_example_check_passes_the_grammar_and_reports_to_its_summary(
    tmp_path: Path,
) -> None:
    script = "scripts/checks/corpus_vintage.py"
    assert cc.parse_command(f"uv run python {script}")
    summary = tmp_path / "summary.md"
    env = {
        **os.environ,
        "CHECK_SUMMARY": str(summary),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "corpus"),
    }
    root = Path(__file__).resolve().parent.parent
    result = cc.run_check(
        [sys.executable, str(root / script)],
        cwd=root,
        env=env,
        timeout_seconds=60,
        output_path=tmp_path / "log",
    )
    assert result.exit_code == 0, (tmp_path / "log").read_text()
    assert "No corpus at" in summary.read_text()
