"""The producer-side secret scan (:mod:`fedcourtsai.secretscan`).

These lock the properties that make the gate trustworthy: real credential
shapes (and the live token in any cheap encoding) are caught, the ledger's
ordinary content — citations, docket numbers, digests, run ids, URLs, legal
prose — passes clean, misconfiguration fails closed, and no rendered output
ever contains the matched text.

The same shapes serve capture-time redaction one layer earlier, so its truth
table lives here too: every credential format is rewritten to a marker, and
the content a retrieval log legitimately carries survives untouched.
"""

from __future__ import annotations

import base64
import random
import struct
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.collect import PathChange, parse_name_status
from fedcourtsai.secretscan import (
    _MAX_SEGMENT,
    Finding,
    redact_credentials,
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


# --- capture-time redaction: what the harness rewrites before it commits ---


# Synthetic stand-ins, never real credentials. The Fernet blob carries the
# shape a codex cell logs when a token rides in a tool-call payload: the v1
# version+timestamp header, then base64url ciphertext to ~487 chars, unpadded.
# Seeded rather than patterned, so it has a real token's entropy and the gate
# would genuinely withhold a run over it.
_FERNET = "gAAAAAB" + base64.urlsafe_b64encode(
    random.Random(20260804).randbytes(360)
).decode().rstrip("=")
_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFnZW50In0"
    ".dBjftJeZ4CVP7mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)
_OPAQUE = base64.urlsafe_b64encode(bytes(range(7, 71))).decode().rstrip("=")


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        (_FERNET, "fernet-token"),
        (f'{{"message": "{_FERNET}"}}', "fernet-token"),
        # No left anchor: a token pasted into the middle of a longer run in
        # the same alphabet is still a token, and the prefix still finds it.
        ("session-" + _FERNET, "fernet-token"),
        (_JWT, "jwt"),
        ("sk-ant-api03-" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7", "model-provider-key"),
        ("sk-proj-" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7", "model-provider-key"),
        ("sk-" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7", "model-provider-key"),
        ("ghp_" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7bC0eF2hiJ5k", "github-token"),
        ("gho_" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7bC0eF2hiJ5k", "github-token"),
        ("ghs_" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7bC0eF2hiJ5k", "github-token"),
        ("github_pat_" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7bC", "github-token"),
        ("AIza" + "SyD3fG6hJ9kL2mN5pQ8rS1tU4vW7xY0zA", "google-key"),
        ("ya29." + "a0AfH6SMBx3dE6gH9jK2mN5pQ8sT1vW4yZ7", "google-key"),
        ("AKIA" + "IOSFODNN7EXAMPLE", "aws-key-id"),
        ("ASIA" + "IOSFODNN7EXAMPLE", "aws-key-id"),
        (_OPAQUE, "opaque"),
    ],
)
def test_credential_shapes_are_redacted(text: str, rule: str) -> None:
    redacted = redact_credentials(f"searched for {text} in the docket")
    assert f"[redacted:{rule}]" in redacted
    assert text not in redacted


# A dotted `<public-id>.<secret>` credential — the shape config-service and
# vault tokens take, and the one that a value class stopping at `.` would
# redact only the front half of.
_DOTTED = "aaaa1111bbbb2222.cccc3333dddd4444"


@pytest.mark.parametrize(
    ("text", "secret"),
    [
        (f"Authorization: Bearer {_OPAQUE}", _OPAQUE),
        (f'{{"headers": {{"Authorization": "Bearer {_OPAQUE}"}}}}', _OPAQUE),
        (f'{{"api_key": "{_TOKEN}"}}', _TOKEN),
        (f"x-api-key={_TOKEN}", _TOKEN),
        (f"password: {_TOKEN}", _TOKEN),
        (f"password: {_DOTTED}", _DOTTED),
        (f'{{"proxy-authorization": "Basic {_TOKEN}"}}', _TOKEN),
    ],
)
def test_credential_headers_and_assignments_are_redacted(text: str, secret: str) -> None:
    redacted = redact_credentials(text)
    assert "[redacted:credential]" in redacted
    # No usable fragment of the value may survive. A rule that redacted only
    # part of a dotted credential would leave the secret half behind *and*
    # rewrite the line past what the collect scan would have flagged.
    for start in range(0, len(secret) - 12):
        assert secret[start : start + 12] not in redacted


def test_a_message_payload_loses_only_the_token_span() -> None:
    # The shape capture-time redaction exists to survive: a delegated-agent
    # `send_message` payload is exactly the evidence the leakage grading reads,
    # so the credential-shaped *span* goes and the instruction around it stays
    # legible. A rule that ate the containing value instead would leave the
    # audit trail unrecoverable.
    prose = (
        "Review the cell's flags.json and report whether the delegated "
        "reviewer read outside its own prediction path."
    )
    redacted = redact_credentials(f'{{"message": "{prose} {_FERNET}"}}')
    assert redacted == f'{{"message": "{prose} [redacted:fernet-token]"}}'
    assert _FERNET not in redacted


# A long run in the base64url alphabet that carries the Fernet header without
# any of a token's entropy. Synthetic and periodic rather than drawn from a
# captured payload: it stands for the class the confirmation exists to spare —
# agent-authored text long enough, and in the right alphabet, to be convicted
# by a six-character prefix alone — not for any particular observed payload.
_PATTERNED_RUN = "gAAAAAB" + "Xy7qL2m9Vt4Rz8Wc" * 30

# The same class in the shape it actually turns up in: a readable identifier
# run, where `_` carries the word breaks that would otherwise end the match.
_IDENTIFIER_RUN = (
    "gAAAAAB-report_whether_the_delegated_reviewer_read_outside_its_own_cell"
    "-listing_under_the_committed_predictions_tree_evaluations_entry_four"
)


def test_a_low_entropy_run_carrying_the_fernet_prefix_survives() -> None:
    # Left whole, not partly rewritten: the prefix says where a token *could*
    # start, and the entropy discriminator — the same one the opaque rule and
    # the scan use — says this run is not one.
    assert redact_credentials(_PATTERNED_RUN) == _PATTERNED_RUN
    # And withdrawing the rewrite costs the gate nothing *here*, because the
    # scan reads the identical run on the identical threshold and finds
    # nothing either. Where that symmetry would have cost something — a real
    # token diluted below the bar — the windowed score keeps the redaction;
    # see the test below.
    assert _scan(_PATTERNED_RUN) == []
    assert _scan(f'{{"message": "{_PATTERNED_RUN}"}}') == []
    assert redact_credentials(_IDENTIFIER_RUN) == _IDENTIFIER_RUN
    assert _scan(_IDENTIFIER_RUN) == []


@pytest.mark.parametrize(
    "diluted",
    [
        # Filler after the token, in the same separator-free alphabet.
        _FERNET[:140] + "_standing_doctrine" * 16,
        _FERNET[:140] + "Aa1_" * 200,
        # And before it — worse, because the greedy match starts at the *first*
        # header and swallows the real token, so the genuine occurrence inside
        # the span is never offered to the rule a second time.
        "gAAAAA" + "Aa1_" * 300 + _FERNET[:140],
        "gAAAAA" + "_standing_doctrine" * 40 + _FERNET[:140],
    ],
    ids=["words-after", "padding-after", "padding-before", "words-before"],
)
def test_a_token_diluted_with_low_entropy_filler_is_still_redacted(diluted: str) -> None:
    # The evasion a whole-span-average confirmation opens: the match is greedy
    # over an alphabet with no separator, so an agent can pad a real token
    # until the span's mean entropy falls under the bar. The scan cannot
    # backstop this one — it scores the same maximal run on the same
    # threshold — so redaction is the only layer, and it has to hold.
    assert _scan(diluted) == [], "the scan is blind here; redaction is the only layer"
    redacted = redact_credentials(f'{{"message": "{diluted}"}}')
    assert "[redacted:fernet-token]" in redacted
    assert _FERNET[:60] not in redacted


def _fernet_token(plaintext_bytes: int, rng: random.Random) -> str:
    """A synthetic token in the real Fernet v1 layout — never a real credential.

    Version byte, 64-bit timestamp, IV, whole cipher blocks, 32-byte HMAC. The
    shortest such token is 100 base64url characters.
    """
    body = (
        b"\x80"
        + struct.pack(">Q", 1786000000)
        + rng.randbytes(16)
        + rng.randbytes(((plaintext_bytes // 16) + 1) * 16)
        + rng.randbytes(32)
    )
    return base64.urlsafe_b64encode(body).decode().rstrip("=")


def test_real_fernet_tokens_are_redacted_at_every_plaintext_size() -> None:
    # The confirmation may not cost the rule its actual job. At minimum token
    # length one 64-char window is a large enough fraction of the whole that
    # sampling variance starts to bite; scoring the whole run alongside the
    # windows, at a quarter-window stride, is what holds this case.
    rng = random.Random(20260814)
    for plaintext in (1, 16, 32, 256, 1024):
        for _ in range(200):
            token = _fernet_token(plaintext, rng)
            assert token.startswith("gAAAAA")
            assert redact_credentials(token) == "[redacted:fernet-token]"


def test_a_token_straddling_the_match_ceiling_is_still_redacted() -> None:
    # The seam between the repeat ceiling and the decline path: a header
    # landing in the last window-width of a ceiling-bounded match is consumed
    # with that match — `re.sub` resumes past it — so the token behind it is
    # never offered to the rule a second time, and the padded run blinds the
    # opaque rule and the scan alike. Confirming over the maximal alphabet run
    # rather than over the truncated match is what sees it.
    #
    # Swept across the band rather than probed at one offset: the failure is
    # alignment-dependent, so a single point would pass by luck.
    token = _fernet_token(32, random.Random(20260815))
    for offset in range(_MAX_SEGMENT - 60, _MAX_SEGMENT + 7):
        filler = "Aa1_" * ((offset - 6) // 4) + "A" * ((offset - 6) % 4)
        text = "gAAAAA" + filler + token
        assert text.index(token) == offset, "fixture must place the header where intended"
        assert _scan(text) == [], "the scan is blind here too; redaction is the only layer"
        assert token[:60] not in redact_credentials(text)


def test_redaction_never_leaves_a_run_the_scan_would_have_withheld() -> None:
    # The property that makes rewriting-instead-of-withholding safe: whatever
    # redaction touches, what it leaves behind is clean by the gate's own
    # detectors — a partial redaction that silenced a finding would be worse
    # than no redaction at all.
    for text in (
        f'{{"message": "{_FERNET}"}}',
        f"Authorization: Bearer {_OPAQUE}",
        f"password: {_DOTTED}",
        f"api_key = {_TOKEN}",
        "ghp_" + "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7bC0eF2hiJ5k",
        "AKIA" + "IOSFODNN7EXAMPLE",
    ):
        assert _scan(text) != [], "fixture must be something the gate would catch"
        assert _scan(redact_credentials(text)) == []


@pytest.mark.parametrize(
    "text",
    [
        # Docket prose, at the length a real query slice runs to.
        "The petition for a writ of certiorari to the United States Court of "
        + "Appeals for the Ninth Circuit presents the question whether the "
        + "court of appeals correctly held that respondents lacked standing.",
        "Docket 22-1078; consolidated with 1:22-cv-01234 (D.D.C.); see 570 U.S. 205 (2013).",
        "params_digest: 9f86d081884c7d65",
        "sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "evt-petition-disposition",
        "https://www.courtlistener.com/api/rest/v4/search/"
        + "?q=cited_by%3A12345&type=o&order_by=dateFiled%20desc&court=scotus",
        "https://www.supremecourt.gov/DocketPDF/25/25-962/401003/"
        + "20260316144707617_25-962acPresidentProTemporeOfTheState.pdf",
        "/home/runner/work/fedcourtsai/fedcourtsai/data/cases/scotus/24-1234/events/"
        + "evt-petition-disposition/predictions/claude-baseline/20260710T120000Z/"
        + "08bfc68e-3166-4d04-a5d6-90dacf06c4d4/prediction.json",
        "run_id: 20260716T123618Z",
        "token: COURTLISTENER_API_TOKEN is configured for the MCP server",
        "Trump-v-United-States-Petition-For-Writ-Of-Certiorari-Granted-In-Part-2026",
        "mcp__courtlistener__search",
        # `bearer` and `basic` are ordinary English next to a 16-char run, so
        # the rule anchors on a credential keyword rather than on the scheme.
        "the bearer of the note assumed basic responsibilities1 under the order",
    ],
)
def test_legitimate_capture_content_survives_redaction(text: str) -> None:
    assert redact_credentials(text) == text


def test_redaction_is_idempotent() -> None:
    once = redact_credentials(f'{{"message": "{_FERNET}"}}')
    assert redact_credentials(once) == once


def test_redaction_terminates_on_a_hostile_payload() -> None:
    # Every variable run in the patterns is repeat-bounded, because the text
    # redaction reads is agent-influenced and arrives uncapped: an unbounded
    # `{n,}` either side of a required literal backtracks quadratically, which
    # is a hung capture step and a lost cell rather than a slow one. The
    # fernet rule adds a second way to spend forever — its confirmation reads
    # the whole alphabet run each match sits in, so a payload made of nothing
    # but headers would rescore the same run once per header if the verdict
    # were not remembered across the pass.
    started = time.monotonic()
    redact_credentials("-eyJ" * 50_000)
    redact_credentials("gAAAAA" * 50_000)
    assert time.monotonic() - started < 10


def _transcript_line() -> str:
    """One execution-log line shaped like real engine output: prose plus the
    server-generated ids whose entropy the generic heuristic convicts."""
    rng = random.Random(20260814)
    ident = "".join(
        rng.choice("ABCDEFGHJKMNPQRSTVWXYZabcdefghjkmnpqrstvwxyz0123456789") for _ in range(40)
    )
    return (
        '{"type":"assistant","message":{"id":"msg_' + ident + '",'
        '"content":[{"type":"tool_use","id":"toolu_01' + ident[:22] + '",'
        '"name":"Write","input":{"file_path":"/tmp/qp-labels.jsonl"}}]}}'
    )


def test_cli_transcript_file_skips_only_the_entropy_heuristic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # As an --extra-file the transcript's own ids convict it; as a
    # --transcript-file the same bytes pass, because the generic entropy
    # heuristic is the one detector its format guarantees to trip.
    changes = _write_tree(tmp_path, "clean artifact.\n")
    transcript = tmp_path / "claude-execution-output.json"
    transcript.write_text(_transcript_line() + "\n")
    monkeypatch.chdir(tmp_path)
    as_extra = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--extra-file",
            str(transcript),
        ],
    )
    assert as_extra.exit_code == 1
    assert "high-entropy" in as_extra.output
    as_transcript = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--transcript-file",
            str(transcript),
        ],
    )
    assert as_transcript.exit_code == 0


def test_cli_transcript_file_still_catches_a_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The detectors that can actually name a secret in a transcript all still
    # run: the known-token containment and the structured credential shapes.
    changes = _write_tree(tmp_path, "clean artifact.\n")
    secret = "sk-ant-" + "x1Yz" * 12
    transcript = tmp_path / "claude-execution-output.json"
    transcript.write_text(_transcript_line() + "\n" + f'{{"leak":"{secret}"}}\n')
    monkeypatch.setenv("LIVE_SECRET_SOURCE", secret)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--known-secret-env",
            "LIVE_SECRET_SOURCE",
            "--transcript-file",
            str(transcript),
        ],
    )
    assert result.exit_code == 1
    assert "known-token" in result.output


def test_cli_missing_transcript_file_fails_closed(
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
            "--transcript-file",
            str(tmp_path / "never-written.json"),
        ],
    )
    assert result.exit_code == 2
    assert "transcript file" in result.output


def test_transcript_surface_catches_prefixed_keys_without_the_known_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The structured shapes are what carry the transcript surface when no
    # known-secret env var is named: a provider key and a JWT must both
    # convict without containment.
    changes = _write_tree(tmp_path, "clean artifact.\n")
    rng = random.Random(20260814)
    tail = "".join(rng.choice("ABCDEFabcdef0123456789") for _ in range(60))
    transcript = tmp_path / "claude-execution-output.json"
    transcript.write_text(
        f'{{"leak":"sk-ant-api03-{tail}"}}\n'
        + '{"env":"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJydW5uZXIifQ.'
        + tail[:20]
        + '"}\n'
    )
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "scan-diff-for-secrets",
            "--name-status-file",
            str(changes),
            "--transcript-file",
            str(transcript),
        ],
    )
    assert result.exit_code == 1
    assert "model-provider-key" in result.output
    assert "jwt" in result.output
