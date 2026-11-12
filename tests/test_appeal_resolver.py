"""The appeal stage's opener and resolver: what each form reads as, and what it declines."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.pipeline import appeal_resolver as appeal
from fedcourtsai.pipeline.appeal_resolver import AppealOutcome, Disposition, Unresolved

TODAY = date(2026, 11, 11)


def entry(number: int, day: str, text: str) -> dict[str, Any]:
    return {"id": 1000 + number, "entry_number": number, "date_filed": day, "description": text}


@pytest.mark.parametrize(
    ("text", "outcome"),
    [
        ("JUDGMENT, Affirmed. Costs taxed against Appellant. (SB)", AppealOutcome.affirmed),
        ("JUDGMENT, Vacated and Remanded.", AppealOutcome.vacated),
        ("JUDGMENT, Affirmed in part, Reversed in part and Remanded.", AppealOutcome.mixed),
        (
            "OPINION (A, B, C) Because the plaintiff is unlikely to succeed, we VACATE the "
            + "preliminary injunction and REMAND. The motion to seal, Dkt. 28, is GRANTED. "
            + "FILED AND ENTERED JUDGMENT.",
            AppealOutcome.vacated,
        ),
        (
            "FILED MEMORANDUM DISPOSITION (A, B, C) AFFIRMED. FILED AND ENTERED JUDGMENT.",
            AppealOutcome.affirmed,
        ),
        ("MEMORANDUM (A, B, C) AFFIRMED IN PART; REVERSED IN PART; REMANDED.", AppealOutcome.mixed),
        (
            "PER CURIAM JUDGMENT [2194982] filed that the judgment of the District Court be "
            + "affirmed, for the reasons in the accompanying opinion.",
            AppealOutcome.affirmed,
        ),
        (
            "SUMMARY ORDER AND JUDGMENT, affirming the judgment of the district court, by "
            + "ABC, DEF, GHI, FILED.",
            AppealOutcome.affirmed,
        ),
        (
            "OPINION, reversing the judgment of the district court, by ABC, FILED.",
            AppealOutcome.reversed,
        ),
        (
            "ORDER FILED. The stipulated motion for voluntary dismissal is granted. This appeal "
            + "is dismissed. Fed. R. App. P. 42(b).",
            AppealOutcome.no_merits_decision,
        ),
        (
            "ORDER (Clerk) dismissing the appeal for lack of appellate jurisdiction.",
            AppealOutcome.dismissed,
        ),
        ("MEMORANDUM (A, B, C) DISMISSED as moot.", AppealOutcome.dismissed),
        (
            "PER CURIAM JUDGMENT filed that the judgment of the District Court be affirmed in "
            + "part and reversed in part.",
            AppealOutcome.mixed,
        ),
        (
            "ORDER FILED. Joint motion for voluntary dismissal is granted; appeal dismissed. All "
            + "pending motions are denied as moot.",
            AppealOutcome.no_merits_decision,
        ),
    ],
)
def test_a_disposition_form_reads_as_its_outcome(text: str, outcome: AppealOutcome) -> None:
    assert appeal.read_disposition(text) is outcome


@pytest.mark.parametrize(
    "text",
    [
        "PRECEDENTIAL OPINION. Coram: A, B and C, Circuit Judges. Total Pages: 32.",
        "JUDGMENT, FILED.",
        "MANDATE ISSUED. The judgment of this Court, entered 8/4/2026, takes effect this date.",
        "DISTRICT COURT OPINION AND ORDER, dated 06/18/2025, RECEIVED.",
        "ORDER FILED. The motion (Docket Entry No. 14) to stay the district court's order is "
        + "granted.",
        "ORDER FILED. The motion to dismiss the cross-claim below is noted.",
        "CLERK'S ORDER filed vacating the court's order filed October 23, 2026.",
        "ECF FILER: Motion filed by Appellee to dismiss the appeal for lack of jurisdiction.",
        "OPINION (A, B, C) The district court dismissed the complaint and vacated its earlier "
        + "order. Opinion by Judge A.",
        "[VACATED PURSUANT TO ORDER FILED 11/03/2026] -- MEMORANDUM (A, B, C) AFFIRMED.",
        "JUDGMENT, Affirmed. [VACATED by order of 11/3/2026]",
        "OPINION WITHDRAWN. MEMORANDUM (A, B, C) AFFIRMED.",
        "ORDER FILED. Appellant is ordered to show cause within 21 days why this appeal should "
        + "not be dismissed for lack of jurisdiction.",
        "ORDER FILED. Within 21 days appellant shall move for voluntary dismissal of the "
        + "appeal or show cause why the appeal should not be dismissed.",
        "ORDER FILED. The motion to dismiss is denied without prejudice. Appellee's argument "
        + "that the appeal should be dismissed for lack of jurisdiction is referred to the "
        + "merits panel.",
        "ORDER filed denying motion to dismiss case for lack of jurisdiction; the question "
        + "whether the appeal must be dismissed as moot is deferred to the merits panel.",
        "ORDER, dismissing appeal by 05/01/2026 unless Appellant submits Form D, FILED.",
        "ORDER, dated 06/18/2025, by District Judge X, dismissing the case for lack of "
        + "jurisdiction, RECEIVED.",
        "OPINION AND ORDER of the district court, DISMISSING the complaint, RECEIVED.",
        "ORDER FILED. The district court dismissed the case as moot. Appellant's motion for an "
        + "injunction pending appeal is denied.",
        "MEMORANDUM IN SUPPORT OF MOTION TO DISMISS APPEAL FOR LACK OF JURISDICTION filed by "
        + "Appellee Y.",
        "MEMORANDUM in opposition to motion to DISMISS filed by Appellant.",
        "JUDGMENT of the Supreme Court of the United States, received. The judgment of this "
        + "court is VACATED and the case is REMANDED.",
        "ORDER FILED. Rehearing en banc is granted. The panel opinion is VACATED.",
        "ORDER FILED. The appeal in 25-1235 is dismissed pursuant to Fed. R. App. P. 42(b); the "
        + "appeal in 25-1234 remains pending.",
    ],
)
def test_an_entry_that_disposes_of_nothing_reads_as_none(text: str) -> None:
    assert appeal.read_disposition(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "PER CURIAM JUDGMENT [1] filed that the petitions for review be denied.",
        "MEMORANDUM (A, B, C) REVERSED and VACATED.",
        "MEMORANDUM (A, B, C) VACATED IN PART.",
        "ORDER FILED. This appeal is dismissed.",
        "ORDER FILED. Appeal dismissed for failure to prosecute. 9th Cir. R. 42-1.",
        "ORDER FILED. The parties' stipulated dismissal is noted; the appeal is dismissed as moot.",
        "ORDER FILED. Counsel's motion to withdraw is granted. The appeal is dismissed for "
        + "failure to prosecute. 9th Cir. R. 42-1.",
        "ORDER FILED. Appellant's untimely motion for an extension is denied. This appeal is "
        + "dismissed for failure to prosecute.",
        "ORDER FILED. The appeal is dismissed in part for lack of jurisdiction.",
        "ORDER FILED. Appellant X's appeal is dismissed for lack of jurisdiction; appellant "
        + "Y's appeal proceeds.",
        "ORDER FILED. The cross-appeal is voluntarily dismissed; the principal appeal proceeds.",
        "FILED PER CURIAM OPINION (A, B, C) The emergency motion for a stay pending appeal is "
        + "DENIED. The administrative stay entered on March 3 is VACATED.",
        "OPINION filed certifying question to state supreme court. Submission is VACATED.",
        "OPINION, DISSENTING, by Judge X, who would REVERSE, FILED.",
        "OPINION (A, B, C) (en banc) The panel opinion is VACATED. We AFFIRM.",
        "MEMORANDUM (A, B, C) Appellee's motion to DISMISS the appeal is DENIED. AFFIRMED.",
        "FILED MEMORANDUM DISPOSITION (A, B, C) AFFIRMED. Appellant's request that we VACATE "
        + "the award is not properly before us.",
        "FILED OPINION (A, B, C) REVERSED AND REMANDED. Judge A dissents and would AFFIRM.",
        "MEMORANDUM (A, B, C) AFFIRMED. The cross-appeal is DISMISSED as moot.",
        "JUDGMENT, Affirmed; cross-appeal dismissed as moot.",
        "JUDGMENT. Affirmed as to appeal 25-1; dismissed as to 25-2.",
        "MEMORANDUM (A, B, C) We AFFIRM the denial of attorney's fees.",
    ],
)
def test_a_disposition_the_rule_will_not_settle_is_a_reason(text: str) -> None:
    assert isinstance(appeal.read_disposition(text), str)


@pytest.mark.parametrize(
    "text",
    [
        "REPLY BRIEF, on behalf of Appellant X, FILED. Service date 12/08/2025 by ACMS.",
        "ECF FILER: REDACTED ELECTRONIC REPLY BRIEF on behalf of Appellant X.",
        "REPLY BRIEF submitted for filing by Appellant X.",
        "PETITIONER REPLY BRIEF [2173124] filed by X Corp [Service Date: 05/13/2026 ]",
        "Submitted (ECF) Reply Brief for review. Submitted by Appellant X.",
    ],
)
def test_the_appellants_filed_reply_is_read(text: str) -> None:
    assert appeal.is_reply_brief(text)


@pytest.mark.parametrize(
    "text",
    [
        "Appellant's Reply Brief due 04/20/2026.",
        "REPLY BRIEF DUE 04/20/2026.",
        "Reply brief due 21 days after service of answering brief.",
        "Appellant's reply brief extension granted to 5/1.",
        "REPLY BRIEF NOT FILED; time expired.",
        "Reply brief deficiency notice sent to Appellant.",
        "Reply Brief stricken by clerk order.",
        "[STRICKEN] REPLY BRIEF on behalf of Appellant X.",
        "REPLY BRIEF in support of motion for stay pending appeal filed by Appellant.",
        "REPLY BRIEF, on behalf of Appellee Y, FILED.",
        "REPLY BRIEF, on behalf of Amicus Curiae Z, FILED.",
        "PETITIONER SUPPLEMENTAL REPLY BRIEF [1] filed by X Corp",
        "HARD COPY RECEIVED from Appellant X - SEALED Reply Brief. Copies: 7.",
        "ECF FILER: Motion filed by Appellant X to seal Reply Brief.",
        "CLERK ACTION: Reply Brief submitted at DE 56 by Appellant X is filed.",
    ],
)
def test_an_entry_about_a_reply_is_not_the_reply(text: str) -> None:
    assert not appeal.is_reply_brief(text)


def docket() -> list[dict[str, Any]]:
    return [
        entry(1, "2026-01-05", "CIVIL CASE DOCKETED."),
        entry(10, "2026-03-01", "BRIEF, on behalf of Appellant X, FILED."),
        entry(20, "2026-04-01", "BRIEF, on behalf of Appellee Y, FILED."),
        entry(29, "2026-04-10", "ECF FILER: Motion filed by Appellant X to seal Reply Brief."),
        entry(28, "2026-04-12", "Appellant's Reply Brief due 04/20/2026."),
        entry(30, "2026-04-20", "ECF FILER: SEALED PROOF REPLY BRIEF on behalf of Appellant X."),
        entry(40, "2026-09-29", "JUDGMENT, Affirmed. Costs taxed against Appellant."),
        entry(41, "2026-09-30", "PRECEDENTIAL OPINION. Coram: A, B and C. Total Pages: 32."),
    ]


def test_the_event_opens_on_the_reply_brief_and_resolves_on_the_judgment() -> None:
    opening = appeal.read_appeal(docket(), today=TODAY)
    assert opening.is_event
    assert opening.opens_on == date(2026, 4, 20)
    assert opening.reply is not None and opening.reply.entry_number == 30
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.affirmed
    assert opening.resolution.cited.entry_number == 40


def test_a_reading_as_of_a_past_day_sees_no_later_entry() -> None:
    opening = appeal.read_appeal(docket(), today=date(2026, 5, 1))
    assert opening.is_event and opening.resolution is None
    before = appeal.read_appeal(docket(), today=date(2026, 4, 15))
    assert before.opens_on is None
    assert before.waiting_on == "the appellant's reply brief"


def test_an_appeal_disposed_of_before_its_reply_opens_nothing() -> None:
    entries = [
        entry(1, "2026-01-05", "CIVIL CASE DOCKETED."),
        entry(5, "2026-02-01", "ORDER (Clerk) dismissing the appeal pursuant to FRAP 42(b)."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.ruled_first and not opening.is_event and opening.waiting_on is None
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.no_merits_decision


def test_a_cross_appeal_opens_nothing() -> None:
    entries = [*docket()[:5], entry(6, "2026-01-20", "CROSS-APPEAL docketed as 26-1001.")]
    opening = appeal.read_appeal(entries, today=date(2026, 5, 1))
    assert opening.opens_on is None
    assert opening.waiting_on is not None and "cross-appeal" in opening.waiting_on


def test_an_unread_judgment_goes_to_triage_and_cites_its_entry() -> None:
    entries = [*docket()[:6], entry(40, "2026-09-25", "MEMORANDUM (A, B, C) REVERSED and VACATED.")]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert isinstance(opening.resolution, Unresolved)
    assert [c.entry_number for c in opening.resolution.candidates] == [40]


def test_a_later_readable_judgment_wins_over_an_earlier_unread_one() -> None:
    entries = [
        *docket()[:6],
        entry(39, "2026-09-25", "ORDER FILED. This appeal is dismissed."),
        entry(40, "2026-09-29", "JUDGMENT, Affirmed."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.affirmed
    assert opening.resolution.cited.entry_number == 40


def test_an_order_to_show_cause_does_not_hide_the_judgment() -> None:
    entries = [
        entry(
            3,
            "2026-01-10",
            "ORDER FILED. Appellant is ordered to show cause why this appeal "
            + "should not be dismissed for lack of jurisdiction.",
        ),
        *docket()[1:6],
        entry(40, "2026-09-29", "JUDGMENT, Reversed."),
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.is_event
    assert isinstance(opening.resolution, Disposition)
    assert opening.resolution.outcome is AppealOutcome.reversed


def test_an_unread_entry_before_the_reply_does_not_close_the_event() -> None:
    entries = [
        entry(3, "2026-01-10", "ORDER FILED. This appeal is dismissed."),
        *docket()[1:6],
    ]
    opening = appeal.read_appeal(entries, today=TODAY)
    assert opening.is_event and not opening.ruled_first
    assert isinstance(opening.resolution, Unresolved)


def _watchlist() -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Training on works."},
            "cases": [
                {
                    "name": "A v. B",
                    "court": "cand",
                    "docket_id": 1,
                    "docket_number": "3:25-cv-00001",
                    "category": "copyright",
                    "why": "Training.",
                    "developers": ["Developer"],
                    "added": "2026-10-30",
                    "related": [
                        {
                            "court": "ca9",
                            "docket_id": 2,
                            "docket_number": "26-1",
                            "relation": "appeal",
                        },
                        {
                            "court": "ca9",
                            "docket_id": 3,
                            "docket_number": "26-2",
                            "relation": "appeal",
                        },
                        {
                            "court": "cadc",
                            "docket_id": 4,
                            "docket_number": "26-3",
                            "relation": "companion",
                        },
                    ],
                }
            ],
        }
    )


def test_the_survey_reads_listed_appeals_only_and_counts_them() -> None:
    watchlist = _watchlist()
    stored = {"ca9/2": docket()}
    result = appeal.survey(watchlist, stored.get, today=TODAY)
    assert [row.docket for row in result.appeals] == ["ca9/2", "ca9/3"]
    assert result.counts() == {
        "listed": 2,
        "stored": 1,
        "events": 1,
        "ruled_first": 0,
        "waiting": 0,
        "events_resolved": 1,
        "events_triage": 0,
        "events_open": 0,
    }
    assert len(appeal.summary_lines(result)) == 3


def test_appeal_events_command_surveys_the_stored_appeals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    (config / "ai-watchlist.yaml").write_text(
        json.dumps(_watchlist().model_dump(mode="json")), encoding="utf-8"
    )
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_snapshot(conn, "ca9/2", date(2026, 11, 1), {"docket_entries": docket()})
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")

    result = CliRunner().invoke(app, ["appeal-events", "--today", "2026-11-11"])

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["counts"]["events_resolved"] == 1
    assert [row["stored"] for row in report["appeals"]] == [True, False]
    assert report["appeals"][0]["outcome"] == "affirmed"
    assert "appeal-events (appeal-resolver-v1" in result.stderr
