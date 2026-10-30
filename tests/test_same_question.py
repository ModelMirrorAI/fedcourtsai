"""Same-question petitions: the TF-IDF match over stored questions-presented texts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, provision
from fedcourtsai.cli import _read_same_question, app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import cascade, moments
from fedcourtsai.pipeline.documents import KIND_QUESTIONS_PRESENTED
from fedcourtsai.pipeline.same_question import (
    CellCutoff,
    Petition,
    QuestionFrame,
    QuestionIndex,
    cell_lists,
    same_question_petitions,
    status_on,
    terms,
    vide_agreement,
)
from fedcourtsai.schemas import Moment, SameQuestionList, SameQuestionLists, Stage
from fedcourtsai.serialize import read_model

runner = CliRunner()

FELON = (
    "Whether 18 U.S.C. 922(g)(1), which bars firearm possession by anyone convicted "
    + "of a felony, violates the Second Amendment as applied to nonviolent offenders."
)
FELON_AGAIN = (
    "Whether the felon-in-possession ban of 18 U.S.C. 922(g)(1) violates the Second "
    + "Amendment as applied to a nonviolent offender."
)
PATENT = (
    "Whether claims directed to a method of detecting cell-free fetal DNA are patent "
    + "eligible under 35 U.S.C. 101 as a law of nature."
)
ARBITRATION = (
    "Whether the Federal Arbitration Act preempts a state rule barring waivers of "
    + "representative claims under the Private Attorneys General Act."
)
HABEAS = (
    "Whether a habeas petitioner must exhaust state remedies before raising an "
    + "ineffective assistance claim in a successive federal petition."
)


def _petition(
    case_id: str,
    text: str,
    *,
    docketed: date | None = date(2025, 1, 10),
    resolved: date | None = None,
    disposition: str | None = None,
    number: str | None = None,
) -> Petition:
    return Petition(
        case_id=case_id,
        docket_number=number or f"25-{case_id.rsplit('/', 1)[-1]}",
        docketed=docketed,
        resolved=resolved,
        disposition=disposition,
        text=text,
    )


def _index(*petitions: Petition) -> QuestionIndex:
    # The default ceiling ignores any term in over a fifth of the texts, which in a
    # five-text fixture drops every shared word; the ceiling is lifted so the
    # fixture measures the weighting instead.
    return QuestionIndex(petitions, max_df_share=1.0)


def test_terms_drop_function_words_and_add_pairs() -> None:
    assert terms("Whether the Court should overrule Chevron") == [
        "should",
        "overrule",
        "chevron",
        "should overrule",
        "overrule chevron",
    ]


def test_the_same_question_outscores_a_different_one() -> None:
    index = _index(
        _petition("scotus/1", FELON),
        _petition("scotus/2", FELON_AGAIN),
        _petition("scotus/3", PATENT),
        _petition("scotus/4", ARBITRATION),
        _petition("scotus/5", HABEAS),
    )
    scores = index.scores("scotus/1")
    assert max(scores, key=lambda case_id: scores[case_id]) == "scotus/2"
    assert scores["scotus/2"] > 2 * scores.get("scotus/3", 0.0)
    assert "scotus/1" not in scores


def test_an_identical_text_scores_one() -> None:
    index = _index(_petition("scotus/1", FELON), _petition("scotus/2", FELON))
    assert index.scores("scotus/1")["scotus/2"] == pytest.approx(1.0)


def test_a_term_in_too_many_texts_is_ignored() -> None:
    index = QuestionIndex(
        [_petition("scotus/1", FELON), _petition("scotus/2", FELON)], max_df_share=0.5
    )
    assert index.scores("scotus/1") == {}


def test_the_list_is_cut_to_the_cutoff() -> None:
    cutoff = date(2025, 3, 1)
    index = _index(
        _petition("scotus/1", FELON),
        _petition(
            "scotus/2",
            FELON,
            docketed=date(2025, 1, 2),
            resolved=date(2025, 2, 20),
            disposition="denied",
        ),
        _petition(
            "scotus/3",
            FELON,
            docketed=date(2025, 1, 3),
            resolved=date(2025, 4, 1),
            disposition="granted",
        ),
        _petition("scotus/4", FELON, docketed=date(2025, 3, 2)),
        _petition("scotus/5", FELON, docketed=None),
        _petition("scotus/6", HABEAS),
    )
    entries = same_question_petitions(index, "scotus/1", cutoff, threshold=0.5)
    # Docketed after the cutoff, or undated, is left out; a later grant reads as pending.
    assert [(e.case_id, e.status) for e in entries] == [
        ("scotus/2", "denied"),
        ("scotus/3", "pending"),
    ]
    assert all(e.score == 1.0 for e in entries)


def test_the_threshold_and_limit_bound_the_list() -> None:
    index = _index(*[_petition(f"scotus/{n}", FELON) for n in range(1, 6)])
    assert len(same_question_petitions(index, "scotus/1", date(2026, 1, 1), limit=2)) == 2
    assert same_question_petitions(index, "scotus/1", date(2026, 1, 1), threshold=1.01) == []


def test_status_is_pending_until_resolved_before_the_cutoff() -> None:
    petition = _petition("scotus/1", FELON, resolved=date(2025, 5, 1), disposition="granted")
    # The cutoff is exclusive, as every cell's cut is: a grant on the cutoff day is unseen.
    assert status_on(petition, date(2025, 5, 1)) == "pending"
    assert status_on(petition, date(2025, 5, 2)) == "granted"


def test_a_petition_docketed_on_the_cutoff_day_is_not_listed() -> None:
    index = _index(
        _petition("scotus/1", FELON),
        _petition("scotus/2", FELON, docketed=date(2025, 3, 1)),
        _petition("scotus/3", FELON, docketed=date(2025, 2, 28)),
    )
    entries = same_question_petitions(index, "scotus/1", date(2025, 3, 1))
    assert [e.case_id for e in entries] == ["scotus/3"]


def test_the_index_weighs_only_the_texts_before_its_cutoff() -> None:
    later = [
        _petition(f"scotus/{n}", HABEAS + " Second Amendment", docketed=date(2025, 6, 1))
        for n in range(10, 14)
    ]
    frame = QuestionFrame(
        [_petition("scotus/1", FELON), _petition("scotus/2", FELON_AGAIN), *later],
        max_df_share=1.0,
    )
    before = frame.index(date(2025, 3, 1))
    assert set(before.vectors) == {"scotus/1", "scotus/2"}
    # Texts filed later would lower the weight of the terms they share; as of
    # the cutoff they are not there to.
    whole = QuestionIndex(list(frame.petitions.values()), max_df_share=1.0)
    assert before.scores("scotus/1")["scotus/2"] != whole.scores("scotus/1")["scotus/2"]
    assert frame.index(date(2025, 3, 1)) is before


def test_each_cell_gets_its_own_list_at_its_own_cutoff() -> None:
    frame = QuestionFrame(
        [
            _petition("scotus/1", FELON),
            _petition("scotus/2", FELON, docketed=date(2025, 2, 25)),
            _petition("scotus/3", PATENT),
            _petition("scotus/4", ARBITRATION, docketed=date(2025, 5, 1)),
        ],
        max_df_share=1.0,
    )
    lists = cell_lists(
        frame,
        [
            CellCutoff("scotus/1", "evt-a", date(2025, 2, 20)),
            CellCutoff("scotus/1", "evt-b", date(2025, 3, 1)),
            CellCutoff("scotus/4", "evt-a", date(2025, 3, 1)),
            CellCutoff("scotus/9", "evt-a", date(2025, 3, 1)),
        ],
    )
    early, late, undocketed, unknown = lists.lists
    assert early.petitions == [] and early.indexed == 2
    assert late.indexed == 3
    assert [e.case_id for e in late.petitions or []] == ["scotus/2"]
    # A petition with no text in the index as of its cutoff has nothing to match on.
    assert undocketed.petitions is None and unknown.petitions is None
    assert SameQuestionLists.model_validate_json(lists.model_dump_json()) == lists


def test_the_vide_check_ranks_the_linked_petitions() -> None:
    index = _index(
        _petition("scotus/1", FELON, number="25-1"),
        _petition("scotus/2", FELON_AGAIN, number="25-2"),
        _petition("scotus/3", PATENT, number="25-3"),
        _petition("scotus/4", ARBITRATION, number="25-4"),
        _petition("scotus/5", PATENT, number="25-5"),
    )
    # 25-3's link is to a different question, and its best match is the unlinked copy.
    agreement = vide_agreement(index, {"scotus/1": ["25-2"], "scotus/3": ["25-4", "25-9", "25-3"]})
    assert agreement.petitions == 5
    assert agreement.linked == 2
    assert agreement.top1_linked == 1
    assert sum(agreement.link_scores.values()) == 2
    assert sum(n for n, _ in agreement.top1_by_score.values()) == 5


def test_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["same-question"]).exit_code == 1  # no corpus yet
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(app, ["same-question", "--docket", "25-1", "--as-of", "2026-01-01"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"lists": {"25-1": None}, "vide_check": None}
    assert runner.invoke(app, ["same-question", "--as-of", "Jan 1"]).exit_code == 2


def test_the_command_normalizes_and_bounds_its_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass
    result = runner.invoke(
        app, ["same-question", "--docket", "No. 25-123", "--as-of", "2026-01-01"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["lists"] == {"25-123": None}
    assert runner.invoke(app, ["same-question", "--threshold", "-0.1"]).exit_code == 2


def _empty_corpus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")):
        pass


def test_the_lists_command_builds_one_list_per_cert_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _empty_corpus(tmp_path, monkeypatch)
    cert = moments.DECLARED_MOMENTS[0]
    merits = next(m for m in moments.DECLARED_MOMENTS if m.stage == Stage.merits)
    assert provision.carries_same_question(cert.event_id)
    assert not provision.carries_same_question(merits.event_id)
    matrix = tmp_path / "matrix.json"
    cells = [
        {"predictor_id": p, "court": "scotus", "docket": 7, "event_id": e}
        for p in ("a", "b")
        for e in (cert.event_id, merits.event_id)
    ]
    matrix.write_text(json.dumps({"include": cells}))
    out = tmp_path / "lists.json"
    result = runner.invoke(
        app,
        [
            "same-question-lists",
            "--matrix-file",
            str(matrix),
            "--out",
            str(out),
            "--today",
            "2026-10-28",
        ],
    )
    assert result.exit_code == 0, result.output
    lists = SameQuestionLists.model_validate_json(out.read_bytes()).lists
    # One per (case, event), the predictors folded; the baseline is uncut, so
    # its list is read through the plan's day.
    assert [(item.case_id, item.event_id, item.cutoff) for item in lists] == [
        ("scotus/7", cert.event_id, date(2026, 10, 29))
    ]
    assert lists[0].petitions is None
    matrix.write_text("{}")
    assert (
        runner.invoke(
            app, ["same-question-lists", "--matrix-file", str(matrix), "--out", str(out)]
        ).exit_code
        == 2
    )


def _lists(cutoff: date) -> SameQuestionLists:
    return SameQuestionLists(
        lists=[
            SameQuestionList(
                case_id="scotus/1",
                event_id=moments.DECLARED_MOMENTS[0].event_id,
                cutoff=cutoff,
                threshold=0.5,
                indexed=3,
                petitions=[],
            )
        ]
    )


def test_a_cell_reads_its_list_only_while_not_held_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = moments.DECLARED_MOMENTS[0].event_id
    path = tmp_path / "lists.json"
    path.write_text(_lists(date(2026, 3, 1)).model_dump_json())
    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", True)
    assert (
        _read_same_question(path, "scotus/1", event, cutoff=date(2026, 3, 1), mode="forward")
        is None
    )
    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", False)
    found = _read_same_question(path, "scotus/1", event, cutoff=date(2026, 3, 1), mode="forward")
    assert found == _lists(date(2026, 3, 1)).lists[0]
    assert _read_same_question(path, "scotus/1", event, cutoff=None, mode="forward") == found
    # A replay cell, another cell, a list cut elsewhere, or no file: none.
    assert _read_same_question(path, "scotus/1", event, cutoff=None, mode="replay") is None
    assert _read_same_question(path, "scotus/2", event, cutoff=None, mode="forward") is None
    assert (
        _read_same_question(path, "scotus/1", event, cutoff=date(2026, 3, 2), mode="forward")
        is None
    )
    assert (
        _read_same_question(tmp_path / "none.json", "scotus/1", event, cutoff=None, mode="forward")
        is None
    )


def test_the_record_carries_the_list_only_while_not_held_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = CasePaths(tmp_path / "data", "scotus", 1)
    placement = provision.Placement(
        snapshot_date=date(2026, 1, 25),
        payload={},
        documents=[],
        provenance="as-stored",
        boundary=None,
        dropped_entries=0,
        dropped_documents=0,
    )
    listed = _lists(date(2026, 1, 26)).lists[0]
    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", True)
    held = provision.write_cell_record(
        paths, "scotus/1", placement, mode="forward", cutoff=None, same_question=listed
    )
    assert held.same_question is None and not paths.same_question.exists()
    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", False)
    written = provision.write_cell_record(
        paths, "scotus/1", placement, mode="forward", cutoff=None, same_question=listed
    )
    assert written.same_question == listed
    assert read_model(paths.same_question, SameQuestionList) == listed
    # The next cell provisioned in the same tree, with no list, does not inherit it.
    provision.write_cell_record(paths, "scotus/1", placement, mode="forward", cutoff=None)
    assert not paths.same_question.exists()


def _seed_frame(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Live cert petitions, three on one question docketed either side of a CVSG cutoff."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    cvsg = next(m for m in moments.DECLARED_MOMENTS if m.moment == Moment.cvsg)
    filed = {"scotus/1": date(2025, 10, 1), "scotus/2": date(2025, 11, 1)}
    filed["scotus/3"] = date(2026, 2, 1)
    texts = {"scotus/1": FELON, "scotus/2": FELON, "scotus/3": FELON}
    # Distinct questions enough that the shared terms stay under the
    # frequency ceiling the match ignores a term above.
    for n in range(10, 22):
        texts[f"scotus/{n}"] = f"Whether statute{n} bars remedy{n} under clause{n}."
        filed[f"scotus/{n}"] = date(2025, 10, 2)
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"25-{case_id.rsplit('/', 1)[-1]}",
                    date_filed=filed[case_id],
                    last_live_polled=date(2026, 8, 27),
                )
                for case_id in texts
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind=KIND_QUESTIONS_PRESENTED,
                    url=f"https://example/{case_id}.pdf",
                    fetched_at=date(2026, 8, 27),
                    text=text,
                )
                for case_id, text in texts.items()
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=cvsg.event_id,
                    case_id="scotus/1",
                    court="scotus",
                    kind=cvsg.kind,
                    stage=cvsg.stage,
                    opened_at=date(2026, 1, 9),
                )
            ],
        )
    return cvsg.event_id


def test_the_lists_command_cuts_a_placed_cell_at_its_moment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = _seed_frame(tmp_path, monkeypatch)
    matrix = tmp_path / "matrix.json"
    matrix.write_text(
        json.dumps({"include": [{"court": "scotus", "docket": 1, "event_id": event}]})
    )
    out = tmp_path / "lists.json"
    result = runner.invoke(
        app, ["same-question-lists", "--matrix-file", str(matrix), "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    (listed,) = SameQuestionLists.model_validate_json(out.read_bytes()).lists
    # The day after the CVSG opened: the petition docketed later is neither
    # listed nor weighed.
    assert listed.cutoff == date(2026, 1, 10)
    assert listed.indexed == 14
    assert [e.case_id for e in listed.petitions or []] == ["scotus/2"]


def test_the_cascade_reads_a_list_not_held_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    event = _seed_frame(tmp_path, monkeypatch)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    placement = provision.Placement(
        snapshot_date=date(2026, 1, 9),
        payload={},
        documents=[],
        provenance="truncated",
        boundary=None,
        dropped_entries=0,
        dropped_documents=0,
    )
    read = provision.CellRead(
        latest=None, documents=[], events=[], row=None, cutoff=date(2026, 1, 10), dated=None
    )

    def lists(mode: str) -> dict[str, SameQuestionList]:
        return cascade._read_same_question_lists(
            db, "local", "scotus/1", {event: placement}, {event: read}, {event: mode}
        )

    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", True)
    assert lists("forward") == {}
    monkeypatch.setattr(provision, "SAME_QUESTION_WITHHELD", False)
    assert lists("replay") == {}
    found = lists("forward")
    assert found[event].cutoff == date(2026, 1, 10)
    assert [e.case_id for e in found[event].petitions or []] == ["scotus/2"]


def test_a_petition_docketed_earlier_in_the_month_is_listed_but_does_not_weigh() -> None:
    frame = QuestionFrame(
        [
            _petition("scotus/1", FELON),
            _petition("scotus/2", PATENT),
            _petition("scotus/3", FELON, docketed=date(2025, 3, 5)),
            _petition("scotus/4", FELON, docketed=date(2025, 3, 25)),
        ],
        max_df_share=1.0,
    )
    index = frame.index(date(2025, 3, 20))
    # Listed: docketed before the cutoff. Not listed: docketed after it.
    entries = same_question_petitions(index, "scotus/1", date(2025, 3, 20))
    assert [e.case_id for e in entries] == ["scotus/3"]
    # The weights are the two texts docketed before March, whatever March added.
    alone = QuestionIndex(
        [_petition("scotus/1", FELON), _petition("scotus/2", PATENT)], max_df_share=1.0
    )
    assert index.vectors["scotus/1"] == alone.vectors["scotus/1"]
