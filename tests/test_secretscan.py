"""The producer-side secret scan (:mod:`fedcourtsai.secretscan`).

These lock the properties that make the gate trustworthy: real credential
shapes (and the live token in any cheap encoding) are caught, the ledger's
ordinary content — citations, docket numbers, digests, run ids, URLs, legal
prose — passes clean, misconfiguration fails closed, and no rendered output
ever contains the matched text.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.collect import PathChange, parse_name_status
from fedcourtsai.secretscan import (
    Finding,
    render_issue_comment,
    render_warnings,
    scan_changes,
    scan_lines,
    secret_variants,
)

runner = CliRunner()

# A fake live credential: 28 chars (not a multiple of 3) so its base64 forms
# genuinely carry padding, which the unpadded-needle variants must still catch.
_TOKEN = "c4f4e8a1b2d3TESTtoken0099zZq"

# The real protected token's shape: 40 lowercase hex.
_HEX_TOKEN = "89f3a1c07d5e4b2a6f8091c3d5e7f90a1b2c3d4e"


def _scan(line: str, known: tuple[str, ...] = ()) -> list[str]:
    return [f.rule for f in scan_lines("data/x/reasoning.md", [line], known)]


# --- detectors: real-shaped fakes are caught ---


def test_aws_key_ids_detected() -> None:
    assert _scan("saw AKIAIOSFODNN7EXAMPLE in env") == ["aws-key-id"]
    assert _scan("ASIAIOSFODNN7EXAMPLE") == ["aws-key-id"]


def test_aws_session_token_detected() -> None:
    blob = "IQoJ" + "b3JpZ2luX2VjEJr" * 8
    assert "aws-session-token" in _scan(blob)


def test_pem_private_key_detected() -> None:
    assert _scan("-----BEGIN RSA PRIVATE KEY-----") == ["pem-private-key"]
    assert _scan("-----BEGIN PRIVATE KEY-----") == ["pem-private-key"]


def test_github_tokens_detected() -> None:
    assert _scan("ghp_" + "A1b2C3d4" * 5) == ["github-token"]
    assert _scan("github_pat_" + "A1b2C3d4" * 4) == ["github-token"]


def test_keyword_assignment_detected() -> None:
    assert "keyword-assignment" in _scan('api_key = "x9v2K4n8Q1r5T7w0"')
    assert "keyword-assignment" in _scan("token: x9v2K4n8Q1r5T7w0abc")


def test_high_entropy_blob_detected_by_design() -> None:
    # An agent pasting an opaque blob into free text is exactly what should
    # withhold the branch, even when no other rule names it.
    blob = base64.b64encode(bytes(range(7, 47))).decode()
    assert "high-entropy" in _scan(f"observed value {blob} in output")


# --- known-token containment, all encodings ---


@pytest.mark.parametrize("variant", secret_variants(_TOKEN))
def test_known_token_containment_catches_each_encoding(variant: str) -> None:
    assert "known-token" in _scan(f"the value is {variant} apparently", known=(_TOKEN,))


def test_known_token_variants_cover_the_cheap_encodings() -> None:
    encoded = _TOKEN.encode()
    variants = secret_variants(_TOKEN)
    assert _TOKEN in variants
    assert base64.b64encode(encoded).decode().rstrip("=") in variants
    assert base64.urlsafe_b64encode(encoded).decode().rstrip("=") in variants
    assert encoded.hex() in variants
    assert encoded.hex().upper() in variants


def test_padded_base64_still_matches_the_unpadded_needle() -> None:
    padded = base64.b64encode(_TOKEN.encode()).decode()
    assert padded.endswith("=")  # the fixture genuinely exercises padding
    assert "known-token" in _scan(f"blob: {padded}", known=(_TOKEN,))


def test_uppercase_hex_of_a_hex_shaped_token_is_caught() -> None:
    # The protected token is itself lowercase hex; its uppercase-hex form has
    # only two character classes, so containment — not entropy — must catch it.
    shouted = _HEX_TOKEN.encode().hex().upper()
    assert "known-token" in _scan(f"value {shouted}", known=(_HEX_TOKEN,))
    assert "known-token" in _scan(f"value {_HEX_TOKEN.upper()}", known=(_HEX_TOKEN.upper(),))


# --- domain negatives: the ledger's normal content passes clean ---


@pytest.mark.parametrize(
    "line",
    [
        "See 570 U.S. 205 (2013) and 599 U.S. 1 (2023).",
        "Docket 22-1078; consolidated with 1:22-cv-01234 (D.D.C.).",
        "https://www.courtlistener.com/opinion/4801990/mata-v-avianca-inc/",
        "https://www.supremecourt.gov/DocketPDF/25/25-962/401003/"
        + "20260316144707617_25-962acPresidentProTemporeOfTheState.pdf",
        # The two highest-entropy readable strings in a real predict run's
        # files (0.802 normalized) — the calibration's upper bound.
        "https://www.supremecourt.gov/DocketPDF/25/25-918/399221/"
        + "20260522140121672_COService_RespMotExpedite.pdf",
        "https://www.supremecourt.gov/DocketPDF/25/25-1019/402118/"
        + "20260601120539217_E-Filing_Proof_of_Service.pdf",
        "fetched the BIO from https://www.supremecourt.gov/DocketPDF/25/25-944/"
        + "398765/20260601120000000_RobinhoodBriefInOppositionToPetition.pdf",
        "params_digest: 9f86d081884c7d65",
        "sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "id: 08bfc68e-3166-4d04-a5d6-90dacf06c4d4",
        "run_id: 20260716T123618Z",
        "token: COURTLISTENER_API_TOKEN is configured for the MCP server",
        "The petition for certiorari presents the question whether the court "
        + "of appeals correctly held that respondents lacked standing.",
        "the CVSG brief recommended a grant limited to the first question presented",
    ],
)
def test_ordinary_ledger_content_not_flagged(line: str) -> None:
    assert _scan(line, known=(_TOKEN,)) == []


# --- redaction: rendered output never carries the matched text ---


def test_rendered_output_never_contains_the_secret() -> None:
    findings = scan_lines("data/x/reasoning.md", [f"leak: {_TOKEN}"], (_TOKEN,))
    assert findings
    rendered = "\n".join(
        [
            *render_warnings(findings),
            render_issue_comment(findings, "https://example.invalid/run/1"),
        ]
    )
    assert _TOKEN not in rendered
    assert "known-token" in rendered  # the rule and location are what surface


def test_issue_comment_empty_when_clean() -> None:
    assert render_issue_comment([], "https://example.invalid/run/1") == ""


def test_findings_carry_location_not_text() -> None:
    finding = scan_lines("data/x/flags.json", ["ok", f"x {_TOKEN}"], (_TOKEN,))[0]
    assert finding == Finding(path="data/x/flags.json", rule="known-token", line=2)


def test_comment_table_sanitizes_paths_and_caps_rows() -> None:
    hostile = Finding(path="data/x/`](http://evil)|.md", rule="pem-private-key", line=1)
    many = [hostile] + [
        Finding(path=f"data/x/{i}.md", rule="pem-private-key", line=i) for i in range(40)
    ]
    comment = render_issue_comment(many, "https://example.invalid/run/1")
    assert "`](http://evil)" not in comment  # markdown metacharacters neutralized
    assert "data/x/?](http.//evil)?.md".replace("(", "?") not in comment  # sanity: no raw echo
    assert "more finding(s)" in comment
    assert comment.count("pem-private-key") <= 25


# --- scope: every changed data/ file with bytes on disk is scanned ---


def test_scan_changes_reads_every_changed_data_file(tmp_path: Path) -> None:
    # Modified tracked files matter too: a non-addition trips the path jail,
    # but the jail only downgrades to a draft — which is still a push — so a
    # secret in an M file must be caught here, not left to the jail.
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "added.md").write_text(f"leak {_TOKEN}\n")
    (tmp_path / "data" / "modified.md").write_text(f"leak {_TOKEN}\n")
    (tmp_path / "outside.md").write_text(f"leak {_TOKEN}\n")
    changes = parse_name_status(
        "A\tdata/added.md\nM\tdata/modified.md\nD\tdata/deleted.md\nA\toutside.md\n"
    )
    findings = scan_changes(changes, tmp_path, (_TOKEN,))
    assert [f.path for f in findings] == ["data/added.md", "data/modified.md"]


def test_scan_changes_skips_listed_but_missing_files(tmp_path: Path) -> None:
    changes = [PathChange(status="A", path="data/gone.md")]
    assert scan_changes(changes, tmp_path, (_TOKEN,)) == []


# --- the CLI command layer ---


def _write_tree(tmp_path: Path, content: str) -> Path:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "reasoning.md").write_text(content)
    changes = tmp_path / "changes.txt"
    changes.write_text("A\tdata/reasoning.md\n")
    return changes


def test_cli_clean_scan_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    changes = _write_tree(tmp_path, "ordinary reasoning about certiorari.\n")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["scan-diff-for-secrets", "--name-status-file", str(changes)])
    assert result.exit_code == 0
    assert "secret scan OK" in result.output


def test_cli_hit_exits_one_and_writes_redacted_comment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    changes = _write_tree(tmp_path, f"leak {_TOKEN}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FAKE_SECRET_SOURCE", _TOKEN)
    issue_file = tmp_path / "issue.md"
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--known-secret-env",
            "FAKE_SECRET_SOURCE",
            "--issue-comment-file",
            str(issue_file),
            "--run-url",
            "https://example.invalid/run/1",
        ],
    )
    assert result.exit_code == 1
    assert "::warning::secret-scan: known-token" in result.output
    text = issue_file.read_text()
    assert "known-token" in text
    assert _TOKEN not in text
    assert "https://example.invalid/run/1" in text


def test_cli_issue_comment_file_appends_across_invocations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    changes = _write_tree(tmp_path, "-----BEGIN PRIVATE KEY-----\n")
    monkeypatch.chdir(tmp_path)
    issue_file = tmp_path / "issue.md"
    args = [
        "scan-diff-for-secrets",
        "--name-status-file",
        str(changes),
        "--issue-comment-file",
        str(issue_file),
    ]
    assert runner.invoke(app, args).exit_code == 1
    assert runner.invoke(app, args).exit_code == 1
    assert issue_file.read_text().count("pem-private-key") >= 2


def test_cli_unset_known_secret_env_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A renamed/unset workflow secret must not silently degrade the gate to
    # heuristics: the scan fails (distinct exit code) and the collect job
    # withholds, exactly as it would for findings.
    changes = _write_tree(tmp_path, "ordinary reasoning.\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ABSENT_SECRET_SOURCE", raising=False)
    issue_file = tmp_path / "issue.md"
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--known-secret-env",
            "ABSENT_SECRET_SOURCE",
            "--issue-comment-file",
            str(issue_file),
            "--run-url",
            "https://example.invalid/run/1",
        ],
    )
    assert result.exit_code == 2
    assert "::error::secret-scan: $ABSENT_SECRET_SOURCE" in result.output
    # Withholding is never silent on the trigger issue, even with no findings.
    text = issue_file.read_text()
    assert "could not run" in text
    assert "https://example.invalid/run/1" in text


def test_cli_extra_file_is_scanned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    changes = _write_tree(tmp_path, "clean artifact.\n")
    body = tmp_path / "pr-body.md"
    body.write_text("flag roll-up quoting -----BEGIN PRIVATE KEY-----\n")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--extra-file",
            str(body),
        ],
    )
    assert result.exit_code == 1
    assert "pem-private-key" in result.output


def test_cli_missing_extra_file_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    changes = _write_tree(tmp_path, "clean artifact.\n")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--extra-file",
            str(tmp_path / "never-written.md"),
        ],
    )
    assert result.exit_code == 2
    assert "is missing" in result.output


def test_workspace_output_paths_are_not_flagged() -> None:
    # The regression from the first live trip: a cell's shell commands carry
    # its own long output path — slashes, dashes, digits, and the run id's
    # T/Z pushing it past three character classes and (in aggregate) the
    # entropy bar. Judged per segment, a path is just short wordy pieces.
    line = (
        '"query": "date -u +%Y-%m-%dT%H:%M:%SZ; mkdir -p /home/runner/work/'
        "fedcourtsai/fedcourtsai/data/cases/scotus/73280380/events/"
        "evt-petition-disposition/predictions/claude-baseline/"
        '20260716T181711Z; rm -f tmp_stderr1.txt"'
    )
    assert _scan(line, known=(_TOKEN,)) == []


def test_credential_length_segment_inside_a_path_still_flags() -> None:
    blob = base64.b64encode(bytes(range(7, 47))).decode().replace("/", "A")
    assert len(blob) >= 40
    line = f"cat /tmp/cache/{blob}/payload.bin"
    assert "high-entropy" in _scan(line)


def test_base64_up_to_two_slashes_is_still_judged_whole() -> None:
    # Two slashes is the boundary: only runs at three or more read as paths
    # and get the per-segment treatment, so a blob with a couple of incidental
    # slashes is still scored — and caught — as one opaque token.
    blob = base64.b64encode(bytes(range(7, 47))).decode().replace("/", "A")
    seeded = blob[:20] + "/" + blob[20:38] + "/" + blob[38:]
    assert seeded.count("/") == 2
    assert "high-entropy" in _scan(f"observed {seeded} in output")


def test_known_gap_base64_split_by_three_slashes_is_missed() -> None:
    # Pins this layer's dominant, deliberate gap (see _PATHLIKE_SLASHES): a
    # std-base64 secret carrying 3+ incidental slashes is scored per segment,
    # and segments under the 40-char floor go unscored. url-safe base64 has no
    # slashes, and a *known* secret is caught by containment regardless — this
    # test exists so the trade stays visible rather than silently widening.
    blob = base64.b64encode(bytes(range(7, 47))).decode().replace("/", "A")
    slashy = "/".join([blob[:14], blob[14:28], blob[28:42], blob[42:]])
    assert slashy.count("/") == 3
    assert _scan(f"observed {slashy} in output") == []
    # ...but containment still catches it when the value is a known secret.
    assert "known-token" in _scan(f"observed {slashy} in output", known=(slashy,))
