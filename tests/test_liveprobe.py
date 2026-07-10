"""The #523 reachability probe: classification, aggregation, and polite fetch."""

from __future__ import annotations

import httpx

from fedcourtsai.pipeline import liveprobe
from fedcourtsai.pipeline.liveprobe import (
    RecordProbe,
    classify_record,
    probe_terms,
    render_markdown,
    summarize_term,
)

# A trimmed real record shape (OT2024 24-1, fetched 2026-07-10): proceedings
# entries with document Links, plus the denial order in plain proceedings text.
_DECIDED_PETITION = {
    "CaseNumber": "24-1 ",
    "bCapitalCase": False,
    "sJsonCaseType": "Paid",
    "sJsonTerm": "2024",
    "DocketedDate": "July 3, 2024",
    "LowerCourt": "United States Court of Appeals for the Ninth Circuit",
    "PetitionerTitle": "In Re Petitioner",
    "ProceedingsandOrder": [
        {
            "Date": "Nov 15 2023",
            "Text": "Petition for a writ of certiorari filed.",
            "Links": [
                {"Description": "Petition", "DocumentUrl": "https://example/petition.pdf"},
                {"Description": "Appendix", "DocumentUrl": "https://example/appendix.pdf"},
            ],
        },
        {"Date": "Aug 1 2024", "Text": "DISTRIBUTED for Conference of 9/30/2024."},
        {"Date": "Oct 7 2024", "Text": "Petition DENIED."},
    ],
}


def test_classify_record_reads_links_and_disposition() -> None:
    probe = classify_record(24, 1, _DECIDED_PETITION)
    assert probe.status == "ok"
    assert probe.case_type == "Paid"
    assert probe.has_lower_court is True
    assert probe.proceedings == 3
    assert probe.entries_with_links == 1
    assert probe.documents == 2
    # The plain-text denial order matches recoverability's cert-order signals —
    # the fact that makes ingest-time resolution (#523) viable on this channel.
    assert probe.disposition_label == "cert denied"
    assert "ProceedingsandOrder" in probe.keys


def test_classify_record_finds_questions_presented_either_shape() -> None:
    top_level = {**_DECIDED_PETITION, "QPLink": "https://example/qp.pdf"}
    assert classify_record(24, 2, top_level).has_questions_presented is True
    entry_level = {
        **_DECIDED_PETITION,
        "ProceedingsandOrder": [
            {
                "Date": "Nov 15 2023",
                "Text": "Petition filed.",
                "Links": [{"Description": "Questions Presented", "DocumentUrl": "x"}],
            }
        ],
    }
    assert classify_record(24, 3, entry_level).has_questions_presented is True
    assert classify_record(24, 1, _DECIDED_PETITION).has_questions_presented is False


def test_classify_record_non_object_payload_is_missing_not_a_crash() -> None:
    probe = classify_record(19, 5, ["unexpected", "array"])
    assert probe.status == "missing"
    assert probe.detail is not None and "non-object" in probe.detail


def test_summarize_term_splits_common_and_variable_keys() -> None:
    a = classify_record(24, 1, _DECIDED_PETITION)
    b = classify_record(24, 2, {**_DECIDED_PETITION, "QPLink": "https://example/qp.pdf"})
    missing = RecordProbe(term=24, number=6000, status="missing", http_status=404)
    term = summarize_term(24, [a, b, missing])
    assert (term.sampled, term.available, term.missing, term.errors) == (3, 2, 1, 0)
    assert "CaseNumber" in term.common_keys
    assert term.variable_keys == ["QPLink"]
    assert term.with_disposition_signal == 2
    assert term.disposition_labels == {"cert denied": 2}
    assert term.documents == 4


def test_summarize_term_with_nothing_available() -> None:
    records = [RecordProbe(term=15, number=n, status="missing", http_status=404) for n in (1, 100)]
    term = summarize_term(15, records)
    assert term.available == 0
    assert term.common_keys == [] and term.variable_keys == []


def test_render_markdown_orders_terms_newest_first() -> None:
    newer = summarize_term(24, [classify_record(24, 1, _DECIDED_PETITION)])
    older = summarize_term(17, [RecordProbe(term=17, number=1, status="missing")])
    table = render_markdown([older, newer])
    lines = table.splitlines()
    assert lines[2].startswith("| 24 ") and lines[3].startswith("| 17 ")
    assert "1/1" in lines[2] and "0/1" in lines[3]


def test_probe_terms_throttles_retries_and_classifies() -> None:
    """One mocked sweep: an ok record, a 404, and a 500 that recovers on retry."""
    calls: list[str] = []
    flaky_state = {"seen": False}

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert request.headers["User-Agent"] == liveprobe.BROWSER_USER_AGENT
        if request.url.path.endswith("24-1.json"):
            return httpx.Response(200, json=_DECIDED_PETITION)
        if request.url.path.endswith("24-100.json"):
            if not flaky_state["seen"]:
                flaky_state["seen"] = True
                return httpx.Response(500)
            return httpx.Response(200, json=_DECIDED_PETITION)
        return httpx.Response(404)

    sleeps: list[float] = []
    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": liveprobe.BROWSER_USER_AGENT},
    )
    summaries, records = probe_terms(
        [24], [1, 100, 6000], throttle_seconds=1.0, client=client, sleep=sleeps.append
    )
    assert [r.status for r in records] == ["ok", "ok", "missing"]
    assert summaries[0].available == 2 and summaries[0].missing == 1
    # Politeness: a throttle sleep between requests (not before the first) plus
    # the one retry backoff for the 500.
    assert sleeps.count(1.0) == 2
    assert liveprobe._RETRY_PAUSE_SECONDS in sleeps
    assert len(calls) == 4  # 3 numbers + 1 retry
