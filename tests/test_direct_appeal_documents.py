"""A direct appeal's answer papers: the motion to dismiss or affirm, and the appellant's answer.

On a mandatory-jurisdiction appeal the appellee answers the jurisdictional
statement with a motion and the appellant answers the motion. The selector
reads the motion into the combined opposition row and the appellant's answer
as the cert-stage reply, on a direct-appeal docket only.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from fedcourtsai.pipeline.cert_signals import is_direct_appeal_docket
from fedcourtsai.pipeline.documents import (
    KIND_BRIEF_IN_OPPOSITION,
    KIND_CERT_REPLY,
    KIND_PETITION,
    select_documents,
)

_HOST = "https://www.supremecourt.gov"
_STATEMENT: dict[str, object] = {
    "Date": "Aug 01 2026",
    "Text": "Statement as to jurisdiction filed. (Response due September 4, 2026)",
    "Links": [{"Description": "Jurisdictional Statement", "DocumentUrl": f"{_HOST}/statement.pdf"}],
}
_PETITION: dict[str, object] = {
    "Date": "Aug 01 2026",
    "Text": "Petition for a writ of certiorari filed. (Response due September 4, 2026)",
    "Links": [{"Description": "Petition", "DocumentUrl": f"{_HOST}/petition.pdf"}],
}
_MOTION = "Motion to dismiss or affirm filed by appellees Bobby Singleton, et al."
_NOTED: dict[str, object] = {
    "Date": "Oct 20 2026",
    "Text": "Probable jurisdiction noted.",
    "Links": [],
}


def _entry(date_: str, text: str, url: str, label: str = "Main Document") -> dict[str, object]:
    return {
        "Date": date_,
        "Text": text,
        "Links": [
            {"Description": "Proof of Service", "DocumentUrl": f"{url}.service.pdf"},
            {"Description": label, "DocumentUrl": url},
        ],
    }


def _appeal(*entries: dict[str, object]) -> dict[str, object]:
    return {"ProceedingsandOrder": [_STATEMENT, *entries]}


def _selected(payload: Mapping[str, object]) -> list[tuple[str, str]]:
    return [(ref.kind, ref.url) for ref in select_documents(payload)]


def _kind_of(text: str, *, after_motion: bool = False) -> str | None:
    """The kind one candidate entry on a direct appeal is selected under, or None."""
    before = [_entry("Sep 18 2026", _MOTION, f"{_HOST}/motion.pdf")] if after_motion else []
    payload = _appeal(*before, _entry("Sep 29 2026", text, f"{_HOST}/candidate.pdf"))
    kinds = [kind for kind, url in _selected(payload) if url == f"{_HOST}/candidate.pdf"]
    assert len(kinds) <= 1
    return kinds[0] if kinds else None


@pytest.mark.parametrize(
    "entry_text",
    [
        # Real docket phrasings.
        "Motion to dismiss or affirm filed by appellees Bobby Singleton, et al.",  # 26-117
        "Motion to dismiss filed by appellees Evan Milligan, et al.",  # 26-118
        "Motion to affirm filed by appellees Common Cause, et al.",  # 18-422
        "Motion to affirm or dismiss filed by appellees Ted Cruz For Senate, et al.",  # 21-12
        "Motion to dismiss filed by  State Appellees'.",  # 18-281
        "Motion to affirm filed by intervenors-appellees Alliance for Retired Americans, "
        + "et al.",  # 26-205
        "Motion to affirm filed by appellees Federal Respondents.",  # 26-205
        "Motion to dismiss or affirm and supplemental appendix filed by appellees Eddie "
        + "Rodriguez, et al.",  # 17-586
        "Motion to affirm filed by appellees New York et al. (Government Appellees)."
        + "  (Distributed)",  # 20-366
    ],
)
def test_an_appellees_motion_to_dismiss_or_affirm_joins_the_opposition_row(
    entry_text: str,
) -> None:
    assert _kind_of(entry_text) == KIND_BRIEF_IN_OPPOSITION


@pytest.mark.parametrize(
    "entry_text",
    [
        # An appellant's own motion to dismiss its appeal is not the answer to it.
        "Motion of appellants to dismiss appellee John Doe filed.",
        "Motion to dismiss the appeal filed by appellants Wes Allen, et al.",
        # A ruling on the motion, with and without its filer.
        "Motion to affirm GRANTED.",
        "Motion to dismiss or affirm filed by appellees DENIED.",
        # Side questions.
        "Motion to dismiss the application filed by appellees John Doe, et al.",
        "Motion to expedite consideration of the jurisdictional statement filed by appellants.",
        "Motion for leave to file amicus brief filed by David Trone. (Distributed)",
        "Motion of appellees for leave to intervene and to dismiss filed.",
        # No filer named: nothing says whose motion it is.
        "Motion to dismiss filed.",
        # Not accepted for filing (25-274).
        "Motion of Evan Milligan, et al. to affirm not accepted for filing. (To be corrected "
        + "- October 20, 2025)",
    ],
)
def test_other_motions_on_a_direct_appeal_are_not_the_opposition(entry_text: str) -> None:
    assert _kind_of(entry_text) is None


@pytest.mark.parametrize(
    "entry_text",
    [
        # Real docket phrasings.
        # 26-117
        "Opposition to motion to dismiss or affirm of appellants Wes Allen, et al. filed.",
        "Response to motion to dismiss from appellants Wes Allen, et al. filed.",  # 26-118
        "Opposition to appellees' motions to dismiss or affirm from appellants Virginia House "
        + "of Delegates, et al. filed.  (Distributed)",  # 18-281
        "Brief opposing motion to affirm from appellants Robert A. Rucho, et al. filed."
        + "  (Distributed)",  # 18-422
        "Opposition to motion of appellants Linda Lamone, et al. filed.  (Distributed)",  # 18-726
        "Opposition to motion to affirm or dismiss filed by appellant Federal Election "
        + "Commission.",  # 21-12
        "Opposition to motions to affirm from appellants University of South Florida College "
        + "Republicans, et al. filed.  (Distributed)",  # 26-205
        "Response to the motions to dismiss and affirm from appellants Louis Agre, et al. "
        + "filed.",  # 17-1339
        "Reply of appellant Donald J. Trump, President of the United States, et al. filed.",
    ],
)
def test_the_appellants_answer_to_the_motion_is_the_reply(entry_text: str) -> None:
    assert _kind_of(entry_text, after_motion=True) == KIND_CERT_REPLY
    # Without an appellee's motion above it there is nothing for it to answer.
    assert _kind_of(entry_text) is None


@pytest.mark.parametrize(
    "entry_text",
    [
        # Collateral practice by the appellants (17-333, 20-366).
        "Reply to response in opposition to motion to expedite consideration of the "
        + "jurisdictional statement from appellants filed.",
        "Response to motion for leave to intervene from appellants filed.",
        "Opposition to motion for divided argument of appellants filed.",
        # The appellee's own papers, and an unpartied reply.
        "Response to motion from appellee New York, et al. filed.",
        "Reply in support of motion filed.",
        # An amicus, and the request for a response.
        "Brief amicus curiae of Philip P. Kalodner in opposition to motion to affirm filed.",
        "Response to the motion to dismiss or affirm requested.",
        # A response to the Court rather than to the motion.
        "Response of appellants Wes Allen, et al. to order of the Court filed.",
        "Response of appellants to suggestion of mootness filed.",
        # The appellees' own reply in support of their motion.
        "Reply of appellees Evan Milligan, et al. to opposition of appellants to motion to "
        + "affirm filed.",
    ],
)
def test_collateral_papers_are_not_the_appellants_reply(entry_text: str) -> None:
    assert _kind_of(entry_text, after_motion=True) is None


def test_every_appellees_motion_is_taken_and_the_first_answer() -> None:
    payload = _appeal(
        _entry("Sep 18 2026", "Motion to dismiss filed by State Appellees.", f"{_HOST}/state.pdf"),
        _entry("Sep 18 2026", _MOTION, f"{_HOST}/private.pdf"),
        _entry(
            "Sep 29 2026",
            "Opposition to appellees' motions to dismiss or affirm from appellants Wes Allen, "
            + "et al. filed.",
            f"{_HOST}/opposition.pdf",
        ),
        _entry("Oct 02 2026", "Reply of appellants Wes Allen, et al. filed.", f"{_HOST}/late.pdf"),
    )
    assert _selected(payload) == [
        (KIND_PETITION, f"{_HOST}/statement.pdf"),
        (KIND_BRIEF_IN_OPPOSITION, f"{_HOST}/state.pdf"),
        (KIND_BRIEF_IN_OPPOSITION, f"{_HOST}/private.pdf"),
        (KIND_CERT_REPLY, f"{_HOST}/opposition.pdf"),
    ]
    motion = select_documents(payload)[1]
    assert motion.description == "Motion to dismiss filed by State Appellees."
    assert motion.entry_date == "Sep 18 2026"


def test_an_appellants_brief_in_opposition_is_the_reply_not_the_opposition() -> None:
    # "Brief in opposition" is the opposition arm's own wording; on a direct
    # appeal, after the appellees' motion, it is the appellants' answer.
    for text in (
        "Brief in opposition to motion to dismiss or affirm filed by appellants Wes Allen.",
        "Brief of appellants Wes Allen, et al. in opposition to motion to affirm filed.",
    ):
        assert _kind_of(text, after_motion=True) == KIND_CERT_REPLY


def test_the_reply_to_an_opposition_worded_answer_is_read() -> None:
    payload = _appeal(
        _entry("Sep 18 2026", "Brief of appellees John Doe in opposition filed.", f"{_HOST}/a.pdf"),
        _entry("Sep 29 2026", "Reply of appellants Wes Allen, et al. filed.", f"{_HOST}/r.pdf"),
    )
    assert _selected(payload)[1:] == [
        (KIND_BRIEF_IN_OPPOSITION, f"{_HOST}/a.pdf"),
        (KIND_CERT_REPLY, f"{_HOST}/r.pdf"),
    ]


def test_nothing_is_read_after_a_summary_exit() -> None:
    # A summary affirmance or a dismissal for want of jurisdiction disposes of
    # the appeal as a denial does a petition: a later paper is not the reply.
    for exit_text in ("Judgment AFFIRMED.", "The appeal is dismissed for want of jurisdiction."):
        payload = _appeal(
            _entry("Sep 18 2026", _MOTION, f"{_HOST}/motion.pdf"),
            {"Date": "Oct 20 2026", "Text": exit_text, "Links": []},
            _entry(
                "Nov 02 2026", "Reply of appellants Wes Allen, et al. filed.", f"{_HOST}/late.pdf"
            ),
        )
        assert KIND_CERT_REPLY not in {kind for kind, _url in _selected(payload)}, exit_text


def test_the_reply_is_read_where_the_motion_posts_no_link() -> None:
    payload = _appeal(
        _entry("Sep 18 2026", _MOTION, f"{_HOST}/motion.pdf", label="Other"),
        _entry("Sep 29 2026", "Reply of appellants Wes Allen, et al. filed.", f"{_HOST}/r.pdf"),
    )
    assert _selected(payload)[1:] == [(KIND_CERT_REPLY, f"{_HOST}/r.pdf")]


def test_a_motion_with_no_main_document_link_stores_nothing() -> None:
    # The motion entry posts its certificates beside the filing; none of them
    # may stand in for it.
    payload = _appeal(_entry("Sep 18 2026", _MOTION, f"{_HOST}/motion.pdf", label="Other"))
    assert _selected(payload) == [(KIND_PETITION, f"{_HOST}/statement.pdf")]


def test_papers_filed_after_jurisdiction_is_noted_are_not_the_answer_papers() -> None:
    # Once the Court notes probable jurisdiction the appeal is at the merits
    # stage: a later motion to dismiss and the appellant's merits reply are
    # not the papers a cert-stage cell reads.
    payload = _appeal(
        _entry("Sep 18 2026", _MOTION, f"{_HOST}/motion.pdf"),
        _NOTED,
        _entry(
            "Nov 20 2026",
            "Motion to dismiss as moot filed by appellees Bobby Singleton, et al.",
            f"{_HOST}/moot.pdf",
        ),
        _entry(
            "Feb 27 2027", "Reply of appellants Wes Allen, et al. filed.", f"{_HOST}/merits.pdf"
        ),
    )
    selected = _selected(payload)
    assert (KIND_BRIEF_IN_OPPOSITION, f"{_HOST}/motion.pdf") in selected
    assert f"{_HOST}/moot.pdf" not in {url for _kind, url in selected}
    assert KIND_CERT_REPLY not in {kind for kind, _url in selected}


def test_a_motion_to_dismiss_on_a_cert_docket_is_not_read() -> None:
    # A petition's docket carries none of the appeal's papers, so a Rule 46
    # motion to dismiss, whoever files it, stays out of the opposition row and
    # the response to it out of the reply.
    entries: list[dict[str, object]] = [
        _PETITION,
        _entry(
            "Sep 18 2026",
            "Motion to dismiss filed by appellees John Doe, et al.",
            f"{_HOST}/motion.pdf",
        ),
        _entry(
            "Sep 29 2026",
            "Response to motion to dismiss from appellants Jane Roe, et al. filed.",
            f"{_HOST}/response.pdf",
        ),
    ]
    assert not is_direct_appeal_docket(str(entry.get("Text")) for entry in entries)
    assert _selected({"ProceedingsandOrder": entries}) == [(KIND_PETITION, f"{_HOST}/petition.pdf")]


def test_the_appeal_arms_leave_a_cert_dockets_selection_alone() -> None:
    # The opposition and the reply on a petition are read as before.
    cert = {
        "ProceedingsandOrder": [
            _PETITION,
            _entry(
                "Sep 04 2026",
                "Brief of respondent Acme Corp. in opposition filed.",
                f"{_HOST}/bio.pdf",
            ),
            _entry("Sep 18 2026", "Reply of petitioner Jane Roe filed.", f"{_HOST}/reply.pdf"),
        ]
    }
    assert _selected(cert) == [
        (KIND_PETITION, f"{_HOST}/petition.pdf"),
        (KIND_BRIEF_IN_OPPOSITION, f"{_HOST}/bio.pdf"),
        (KIND_CERT_REPLY, f"{_HOST}/reply.pdf"),
    ]
