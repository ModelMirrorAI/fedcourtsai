"""The codex watchdog's off-runner record: find-or-reset, rendering, and the CLI.

The channel exists because every runner-local one dies with the job that gets
cancelled, so the properties worth pinning are the ones that make a *later*
reader trust what is on the issue: this cell's comment is found and reset rather
than duplicated, its body is the renderers' output and nothing else, a healthy
round collapses to one line, and a degraded API costs the record rather than the
arming. All of it runs off ``agent_feedback``'s injectable ``gh`` seam, so no
test here touches the network.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.watchdog_telemetry import (
    _COMMENT_PAGE_SIZE,
    _COMMENT_PAGES,
    LABEL,
    arm_checkin,
    arm_times,
    armed_body,
    checkin_head,
    checkin_marker,
    disarm_checkin,
    disarmed_body,
)

runner = CliRunner()

CELL = {
    "run_id": "20260907T120000Z",
    "court": "scotus",
    "docket": "24-1234",
    "event_id": "evt-cert-2026-01-09",
    "actor": "codex-baseline",
}
MARKER = checkin_marker(**CELL)
NOW = datetime(2026, 9, 7, 12, 0, 0, tzinfo=UTC)


class FakeGh:
    """A :data:`GhRunner` answering the label/issue/comment calls this module makes.

    Comments are held as a list of ``{id, url, body}`` and paged exactly as the
    REST endpoint pages them, so the bounded marker search is exercised rather
    than assumed.
    """

    def __init__(
        self,
        *,
        issues: list[dict[str, int]] | None = None,
        comments: list[str] | None = None,
        planted: list[str] | None = None,
        create_url: str = "https://github.com/o/r/issues/77",
    ) -> None:
        self._issues = issues if issues is not None else []
        # `comments` are App-authored, as everything this module writes is;
        # `planted` are written by an account, which on a public repo is anyone.
        self.comments: list[dict[str, Any]] = [
            {
                "id": 900 + i,
                "url": f"https://api.github.com/c/{900 + i}",
                "body": body,
                "user": {"type": "Bot"},
            }
            for i, body in enumerate(comments or [])
        ]
        self.comments += [
            {
                "id": 800 + i,
                "url": f"https://api.github.com/c/{800 + i}",
                "body": body,
                "user": {"type": "User"},
            }
            for i, body in enumerate(planted or [])
        ]
        self._create_url = create_url
        self._next_id = 1000
        self.since = ""
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        verb = tuple(argv[1:3])
        if verb == ("issue", "list"):
            return json.dumps(self._issues)
        if verb == ("issue", "create"):
            return self._create_url + "\n"
        if argv[1] == "api":
            return self._api(list(argv))
        return ""  # label create

    def _api(self, argv: list[str]) -> str:
        method = argv[argv.index("--method") + 1]
        if method == "GET":
            # The module must bound the listing to the recent end of the issue;
            # without it a page cap searches the end its own comment is never at.
            assert any(a.startswith("since=") for a in argv), "the comment listing is unbounded"
            self.since = next(a.split("=", 1)[1] for a in argv if a.startswith("since="))
            page = next(int(a.split("=")[1]) for a in argv if a.startswith("page="))
            start = (page - 1) * _COMMENT_PAGE_SIZE
            return json.dumps(self.comments[start : start + _COMMENT_PAGE_SIZE])
        body = next(a.split("=", 1)[1] for a in argv if a.startswith("body="))
        if method == "POST":
            self._next_id += 1
            written = {
                "id": self._next_id,
                "url": f"https://api.github.com/c/{self._next_id}",
                "body": body,
                "user": {"type": "Bot"},
            }
            self.comments.append(written)
            return json.dumps(written)
        target = int(argv[2].rsplit("/", 1)[-1])
        existing = next(c for c in self.comments if c["id"] == target)
        existing["body"] = body
        return json.dumps(existing)

    def methods(self) -> list[str]:
        return [c[c.index("--method") + 1] for c in self.calls if c[1] == "api"]

    def created_issue(self) -> bool:
        return any(tuple(c[1:3]) == ("issue", "create") for c in self.calls)


def _arm(gh: FakeGh, **over: object) -> tuple[str, str]:
    return arm_checkin(repo="o/r", **CELL, deadline_s=2400, now=NOW, runner=gh, **over)  # type: ignore[arg-type]


# --- the marker and the head ------------------------------------------------


def test_the_marker_names_the_cell_and_the_run() -> None:
    assert MARKER == (
        "<!-- codex-watchdog: 20260907T120000Z/scotus/24-1234"
        + "/evt-cert-2026-01-09/codex-baseline -->"
    )
    # A second predictor on the same cell is a different record, or two engines'
    # watchdogs would overwrite each other's account.
    assert checkin_marker(**{**CELL, "actor": "codex-alt"}) != MARKER


def test_the_head_opens_with_the_marker_so_a_patched_body_stays_findable() -> None:
    """The watchdog PATCHes the whole body, so it must reproduce this head.

    It receives the head rather than rebuilding the marker in shell — a second
    spelling of the format is a drift that shows up only as a duplicate comment
    months later, which is exactly the failure this channel exists to notice.
    """
    head = checkin_head(**CELL)
    assert head.splitlines()[0] == MARKER
    # The visible line names the cell, so the issue reads without expanding HTML.
    assert "scotus/24-1234" in head.splitlines()[1]


# --- what a body may say ----------------------------------------------------


def test_the_armed_body_is_timestamps_a_deadline_and_a_run_url() -> None:
    armed_at, fire_eta = arm_times(2400, NOW)
    assert (armed_at, fire_eta) == ("2026-09-07T12:00:00Z", "2026-09-07T12:40:00Z")
    body = armed_body(
        checkin_head(**CELL),
        armed_at=armed_at,
        fire_eta=fire_eta,
        deadline_s=2400,
        run_url="https://github.com/o/r/actions/runs/5",
    )
    assert "armed_at=2026-09-07T12:00:00Z deadline_s=2400 fire_eta=2026-09-07T12:40:00Z" in body
    assert body.startswith(MARKER)
    assert "https://github.com/o/r/actions/runs/5" in body


def test_a_healthy_disarm_collapses_the_record_but_keeps_the_arming_time() -> None:
    """A quiet round is one line, so the rounds that fired are not buried.

    The arming time survives the collapse: "armed and stood down" without it
    cannot be matched against the run it belonged to.
    """
    prior = f"{checkin_head(**CELL)}\narmed_at=2026-09-07T12:00:00Z deadline_s=2400\n[t] waiting"
    body = disarmed_body(
        checkin_head(**CELL),
        prior=prior,
        disarmed_at="2026-09-07T12:20:00Z",
        conclusion="success",
        healthy=True,
    )
    assert "waiting" not in body
    assert "armed_at=2026-09-07T12:00:00Z" in body
    assert "disarmed_at=2026-09-07T12:20:00Z conclusion=success" in body


def test_a_disarm_after_a_deadline_keeps_the_live_record() -> None:
    """What the watchdog PATCHed is what a maintainer came for; nothing overwrites it."""
    prior = f"{checkin_head(**CELL)}\narmed_at=X\n[t] FIRED: the engine was still running"
    body = disarmed_body(
        checkin_head(**CELL),
        prior=prior,
        disarmed_at="2026-09-07T12:41:00Z",
        conclusion="failure",
        healthy=False,
    )
    assert "FIRED: the engine was still running" in body
    assert body.endswith("[2026-09-07T12:41:00Z] disarmed: conclusion=failure")


def test_a_disarm_that_finds_no_prior_record_still_writes_one() -> None:
    # The arm's check-in can have failed while the watchdog still fired; a
    # disarm that produced nothing at all would report that as a quiet round.
    body = disarmed_body(
        checkin_head(**CELL), prior="", disarmed_at="T", conclusion="failure", healthy=False
    )
    assert body.startswith(MARKER)
    assert "conclusion=failure" in body


# --- find-or-create, find-or-reset ------------------------------------------


def test_the_first_cell_opens_the_label_the_issue_and_its_comment() -> None:
    gh = FakeGh()
    url, base = _arm(gh)
    assert gh.calls[0][:4] == ["gh", "label", "create", LABEL]  # idempotent, first
    assert gh.created_issue()
    assert gh.methods() == ["GET", "POST"]
    assert url == "https://api.github.com/c/1001"  # the API URL the watchdog PATCHes
    # The base is the *whole* body written, not just its head. The watchdog
    # PATCHes what it has composed, so a base trimmed to the marker would have
    # its first heartbeat erase the arming time, the fire ETA and the run link —
    # which on a run that never comes back is the entire record.
    assert base == gh.comments[0]["body"]
    assert base.startswith(checkin_head(**CELL))
    assert "fire_eta=" in base


def test_an_open_issue_is_reused_rather_than_multiplied() -> None:
    gh = FakeGh(issues=[{"number": 42}])
    _arm(gh)
    assert not gh.created_issue()
    listed = next(c for c in gh.calls if tuple(c[1:3]) == ("issue", "list"))
    assert "--state" in listed and listed[listed.index("--state") + 1] == "open"


def test_re_arming_the_same_cell_resets_its_comment_instead_of_stacking_one() -> None:
    """A re-dispatch of the same run is the same cell, so it is the same row.

    Reset, not append: the previous attempt's heartbeats describe a runner that
    no longer exists, and leaving them above the live ones is how a reader
    mistakes an old wedge for the current one.
    """
    stale = f"{checkin_head(**CELL)}\narmed_at=old\n[t] FIRED: an earlier attempt"
    gh = FakeGh(issues=[{"number": 42}], comments=["someone else's note", stale])
    url, _ = _arm(gh)
    assert gh.methods() == ["GET", "PATCH"]
    assert url == "https://api.github.com/c/901"
    assert "an earlier attempt" not in gh.comments[1]["body"]
    assert "armed_at=2026-09-07T12:00:00Z" in gh.comments[1]["body"]


def test_another_cells_comment_is_never_reset() -> None:
    other = checkin_head(**{**CELL, "docket": "24-9999"})
    gh = FakeGh(issues=[{"number": 42}], comments=[other])
    _arm(gh)
    assert gh.methods() == ["GET", "POST"]
    assert gh.comments[0]["body"] == other


def test_the_marker_search_pages_but_only_so_far() -> None:
    """The issue grows a row per codex cell per round, so the search is bounded.

    Past the bound the arm posts a fresh comment: one duplicate row on a
    re-dispatch is a far cheaper failure than an unbounded per-arm page walk,
    paid on the runner that is already in trouble.
    """
    filler = ["unrelated"] * (_COMMENT_PAGE_SIZE * _COMMENT_PAGES)
    gh = FakeGh(
        issues=[{"number": 42}], comments=[*filler, f"{checkin_head(**CELL)}\narmed_at=old"]
    )
    _arm(gh)
    assert gh.methods() == ["GET"] * _COMMENT_PAGES + ["POST"]


def test_the_search_is_bounded_to_the_recent_end_of_the_issue() -> None:
    """The page cap only means anything against a `since` window.

    The comments endpoint pages oldest-first and takes no direction, so a cap
    applied from page 1 searches the end of a long-lived issue that this cell's
    own comment is never at — the disarm would then miss the row the arm just
    wrote, open a second one, and never collapse the first. The issue would grow
    at twice the rate the cap was meant to bound.
    """
    gh = FakeGh(issues=[{"number": 42}])
    _arm(gh)
    assert gh.since == "2026-08-31T12:00:00Z"  # a week back from the arming


def test_a_marker_someone_else_posted_is_never_the_record() -> None:
    """This repository is public, so the marker alone cannot say whose row it is.

    Every part of a marker is derivable from the issue's visible history and the
    committed ledger, so a stranger can pre-post a future cell's marker.
    Resetting into it would hand the one un-erasable account of a hang to someone
    who keeps the ability to edit it — so an account-authored comment is passed
    over and a fresh one written instead.
    """
    planted = f"{checkin_head(**CELL)}\narmed_at=whenever-they-like"
    gh = FakeGh(issues=[{"number": 42}], planted=[planted])
    _arm(gh)
    assert gh.methods() == ["GET", "POST"]
    assert gh.comments[0]["body"] == planted  # left exactly as they wrote it


def test_a_marker_quoted_below_the_head_is_not_the_record() -> None:
    """A maintainer quoting a record into a triage reply must not become the row."""
    quoted = "### triage\nquoting the record below:\n" + checkin_head(**CELL)
    gh = FakeGh(issues=[{"number": 42}], comments=[quoted])
    _arm(gh)
    assert gh.methods() == ["GET", "POST"]
    assert gh.comments[0]["body"] == quoted


def test_a_short_page_stops_the_search_early() -> None:
    gh = FakeGh(issues=[{"number": 42}], comments=["unrelated"])
    _arm(gh)
    assert gh.methods() == ["GET", "POST"]


def test_disarming_resets_the_comment_the_arming_opened() -> None:
    gh = FakeGh()
    url, _ = _arm(gh)
    disarm_url, _ = disarm_checkin(
        repo="o/r", **CELL, conclusion="success", healthy=True, now=NOW, runner=gh
    )
    assert disarm_url == url  # the same row, closed out in place
    assert "stood down cleanly" in gh.comments[0]["body"]
    # The arming time is recovered from the body the arming actually wrote, so
    # the collapsed line says when the guard went up rather than `unknown`.
    assert "armed_at=2026-09-07T12:00:00Z" in gh.comments[0]["body"]


# --- the CLI wrapper --------------------------------------------------------


def test_the_command_prints_the_url_then_the_base(monkeypatch: pytest.MonkeyPatch) -> None:
    """The URL on the first line, the base on every line after it.

    The arm step splits exactly there — first line into the watchdog's check-in
    URL, the remainder into the body it appends to — so a base of any number of
    lines has to survive the round trip.
    """
    monkeypatch.setattr(cli, "arm_checkin", lambda **_: ("https://api.example/c/1", "H1\nH2\nH3"))
    result = runner.invoke(
        cli.app,
        [
            "watchdog-checkin",
            "--repo",
            "o/r",
            "--run-id",
            CELL["run_id"],
            "--court",
            CELL["court"],
            "--docket",
            CELL["docket"],
            "--event-id",
            CELL["event_id"],
            "--actor",
            CELL["actor"],
            "--deadline-s",
            "2400",
        ],
    )
    assert result.exit_code == 0, result.output
    printed = result.output.splitlines()
    assert printed[0] == "https://api.example/c/1"
    assert "\n".join(printed[1:]) == "H1\nH2\nH3"


def test_the_disarm_flag_routes_to_the_disarm_record(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def fake(**kwargs: object) -> tuple[str, str]:
        seen.update(kwargs)
        return "u", "h"

    monkeypatch.setattr(cli, "disarm_checkin", fake)
    result = runner.invoke(
        cli.app,
        [
            "watchdog-checkin",
            "--disarm",
            "--not-healthy",
            "--repo",
            "o/r",
            "--run-id",
            CELL["run_id"],
            "--court",
            CELL["court"],
            "--docket",
            CELL["docket"],
            "--event-id",
            CELL["event_id"],
            "--actor",
            CELL["actor"],
            "--conclusion",
            "failure",
        ],
    )
    assert result.exit_code == 0, result.output
    assert seen["healthy"] is False
    assert seen["conclusion"] == "failure"


def test_a_degraded_api_costs_the_record_and_not_the_arming(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The kill duty is primary, so this exits zero with a warning and no URL.

    The arm step reads the first printed line as the check-in URL; an empty one
    arms a watchdog that beats nowhere, which is strictly the situation before
    this channel existed. A non-zero exit here would instead abort the arm step
    under `set -e` and leave the wedge unbounded — trading the guard for its
    own reporting.
    """

    monkeypatch.setattr(cli, "arm_checkin", _boom)
    result = runner.invoke(
        cli.app,
        [
            "watchdog-checkin",
            "--repo",
            "o/r",
            "--run-id",
            CELL["run_id"],
            "--court",
            CELL["court"],
            "--docket",
            CELL["docket"],
            "--event-id",
            CELL["event_id"],
            "--actor",
            CELL["actor"],
        ],
    )
    assert result.exit_code == 0
    assert "::warning::" in result.output
    assert "http" not in result.output  # nothing the arm step could read as a URL


def _boom(**_: object) -> tuple[str, str]:
    raise subprocess.CalledProcessError(1, ["gh", "api"])


def test_the_failure_note_stays_off_stdout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The arm step captures stdout into the check-in URL, so stdout must be empty.

    ``CliRunner`` merges the two streams, so this drives the command directly:
    a warning that landed on stdout would be handed to the watchdog as its
    PATCH target, and every check-in would then fail against a nonsense URL.
    """
    monkeypatch.setattr(cli, "arm_checkin", _boom)
    cli.watchdog_checkin_cmd(repo="o/r", **CELL)  # type: ignore[arg-type]
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "::warning::" in captured.err
