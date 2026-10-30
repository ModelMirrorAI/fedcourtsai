"""Petitions that raise the same question: a no-spend match on the stored QP text.

A cert cell sees a companion only where the docket links it as ``Vide``
(:mod:`.vide_links`). A petition that raises the same question without a link
is invisible to it, though it carries the hold and split signals a cert
forecast wants: a granted petition on the same question predicts a hold and a
GVR, and several pending petitions on it suggest a split worth resolving.

The QP topic labels (``docs/qp-topic.md``) are too broad to find those: one
topic spans well over a thousand petitions, and a petition docketed after the
labeling frame carries no label at all. The stored questions-presented text is
there from docketing, so this module matches on it directly.

**The match** is a TF-IDF cosine over the questions-presented texts: lowercased
words, with a short list of function words and the legal boilerplate every
question shares ("whether", "court", "petitioner") dropped, and the word pairs
adjacent once those are gone; any term found in more than :data:`MAX_DF_SHARE` of the texts
ignored, since a term that common carries no question. Weights are
``(1 + log tf) * idf`` with a smoothed ``idf``, L2-normalized, so a score is a
cosine in [0, 1]. Nothing is learned and nothing is stored: the index is
rebuilt from the texts on every read.

**The cut.** :func:`same_question_petitions` lists, for one petition and a
cutoff date, the other petitions docketed strictly before the cutoff whose
score is at least the threshold, each with its status as of the cutoff
(pending until its resolution date, its disposition once that date falls
before the cutoff). The cutoff is exclusive, the date rule every cell's
snapshot, documents and companions are cut by
(:func:`fedcourtsai.provision.moment_cutoff`), so a petition resolved on the
cutoff day itself reads as pending, and the list never carries an outcome the
cell's moment could not have seen. The index a list is read from weighs a term
by the texts docketed before the first day of the cutoff's month
(:meth:`QuestionFrame.index`), so a score does not move with anything filed
on or after the cutoff; the texts docketed between the month's first day and
the cutoff are listed but do not weigh. Counts and identifiers only: the
entries carry no filing text.

**How well it matches.** :func:`vide_agreement` measures the match against the
docket's own ``Vide`` links, which are a weak yardstick both ways: the Court
links petitions it considers together whether or not they raise one question,
and most same-question petitions carry no link. The default threshold of 0.5 is
chosen from an informal, unblinded single-grader reading of best-match pairs,
not from a precision estimate.

**What a cell reads.** :func:`cell_lists` builds one :class:`SameQuestionList`
per cert-stage cell of a round from one read of the frame, which is what the
predict plan job runs (``fedcourts same-question-lists``); provisioning stages a
cell's own list as ``record/same-question.json`` for a forward cell, behind the
harness boundary ``cert-same-question-list``
(:data:`fedcourtsai.provision.SAME_QUESTION_WITHHELD` holds it back when set).
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import pairwise
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import SameQuestionEntry, SameQuestionList, SameQuestionLists
from .documents import questions_presented_extract
from .prefetch import prefetch_by_case
from .vide_links import vide_docket_numbers

#: A term in more than this share of the texts is ignored.
MAX_DF_SHARE: Final = 0.2

#: The default score a match must reach to be listed.
DEFAULT_THRESHOLD: Final = 0.5

#: The default number of matches listed for one petition.
DEFAULT_LIMIT: Final = 10

_WORD_RE = re.compile(r"[a-z0-9§]+(?:[.'][a-z0-9]+)*")

# Function words, and the words nearly every question presented carries, which
# say nothing about which question it is.
_STOPWORDS: Final = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "may",
        "might",
        "must",
        "no",
        "not",
        "of",
        "on",
        "or",
        "other",
        "such",
        "than",
        "that",
        "the",
        "their",
        "then",
        "there",
        "these",
        "this",
        "those",
        "to",
        "under",
        "upon",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "whether",
        "will",
        "with",
        "would",
        "also",
        "any",
        "all",
        "only",
        "same",
        "so",
        "whose",
        "court",
        "courts",
        "circuit",
        "petitioner",
        "petitioners",
        "respondent",
        "respondents",
        "case",
        "cases",
        "question",
        "questions",
        "presented",
        "below",
        "held",
        "holding",
        "decision",
    ]
)


def terms(text: str) -> list[str]:
    """The words of ``text`` the match counts, and each pair adjacent once the rest are gone."""
    words = [w for w in _WORD_RE.findall(text.lower()) if len(w) > 1 and w not in _STOPWORDS]
    return words + [f"{a} {b}" for a, b in pairwise(words)]


@dataclass(frozen=True)
class Petition:
    """One petition the index holds: its identifiers, timing, and QP text."""

    case_id: str
    docket_number: str
    docketed: date | None
    resolved: date | None
    disposition: str | None
    text: str


def read_petitions(conn: corpus.ReadConnection) -> list[Petition]:
    """Every petition of the labeling frame with a stored questions-presented text.

    The frame is the QP labeling extract's (:func:`.documents.questions_presented_extract`):
    the live slice's modern discretionary-cert petitions. A petition's
    resolution date is its cert grant or denial, else its termination.
    """
    extract = questions_presented_extract(conn)
    rows = {row.case_id: row for row in corpus.iter_rows(conn, court="scotus", live_slice=True)}
    petitions = []
    for qp in extract.rows:
        row = rows.get(qp.case_id)
        if row is None:
            continue
        petitions.append(
            Petition(
                case_id=qp.case_id,
                docket_number=qp.docket_number,
                docketed=row.date_filed,
                resolved=row.date_cert_granted or row.date_cert_denied or row.date_decided,
                disposition=str(row.disposition) if row.disposition else None,
                text=qp.text,
            )
        )
    return petitions


def read_vide_links(
    conn: corpus.ReadConnection, case_ids: Sequence[str]
) -> dict[str, tuple[str, ...]]:
    """Each case's Vide-linked docket numbers, off its latest stored live snapshot."""
    links: dict[str, tuple[str, ...]] = {}
    with prefetch_by_case(
        sorted(case_ids),
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="same-question",
    ) as fetched:
        for case_id, snapshot in fetched:
            if snapshot is not None and (numbers := vide_docket_numbers(snapshot[1])):
                links[case_id] = numbers
    return links


class QuestionIndex:
    """TF-IDF vectors over a set of questions-presented texts, with an inverted index.

    ``weigh`` names the texts the term weights are counted over, all of them by
    default; a text outside it still gets a vector, weighted by the others.
    """

    def __init__(
        self,
        petitions: Sequence[Petition],
        *,
        max_df_share: float = MAX_DF_SHARE,
        counts: Mapping[str, Counter[str]] | None = None,
        weigh: Callable[[Petition], bool] | None = None,
    ):
        self.petitions: dict[str, Petition] = {p.case_id: p for p in petitions}
        counts = {
            p.case_id: counts[p.case_id] if counts is not None else Counter(terms(p.text))
            for p in petitions
        }
        df: Counter[str] = Counter()
        n = 0
        for case_id, bag in counts.items():
            if weigh is None or weigh(self.petitions[case_id]):
                df.update(bag.keys())
                n += 1
        # Below five texts a one-fifth ceiling drops every term; only a fixture is that small.
        ceiling = max_df_share * n
        idf = {t: math.log((n + 1) / (d + 1)) + 1 for t, d in df.items() if d <= ceiling}
        self.vectors: dict[str, dict[str, float]] = {}
        self.postings: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for case_id, bag in counts.items():
            weights = {t: (1 + math.log(c)) * idf[t] for t, c in bag.items() if t in idf}
            norm = math.sqrt(sum(w * w for w in weights.values()))
            if not norm:
                continue
            vector = {t: w / norm for t, w in weights.items()}
            self.vectors[case_id] = vector
            for t, w in vector.items():
                self.postings[t].append((case_id, w))

    def scores(self, case_id: str) -> dict[str, float]:
        """Every other petition sharing a counted term with ``case_id``, by cosine."""
        vector = self.vectors.get(case_id)
        if vector is None:
            return {}
        out: dict[str, float] = defaultdict(float)
        for t, w in vector.items():
            for other, v in self.postings[t]:
                if other != case_id:
                    out[other] += w * v
        return dict(out)


class QuestionFrame:
    """The frame's texts, split into terms once, from which an index is built per month.

    A round's cells sit at many cutoffs, and an index over the frame takes
    seconds to build, so one index serves every cutoff in a calendar month: its
    term weights are counted over the texts docketed before the month began,
    and it holds a vector for every text docketed before the month ends, each
    weighted by those earlier texts alone. A list read from it at a cutoff in
    the month (:func:`same_question_petitions`) keeps only the texts docketed
    before the cutoff, so nothing it lists or weighs is filed on or after it.
    """

    def __init__(self, petitions: Sequence[Petition], *, max_df_share: float = MAX_DF_SHARE):
        self.petitions: dict[str, Petition] = {p.case_id: p for p in petitions}
        self.max_df_share = max_df_share
        self.counts: dict[str, Counter[str]] = {
            p.case_id: Counter(terms(p.text)) for p in petitions
        }
        self._last: tuple[date, QuestionIndex] | None = None

    def index(self, cutoff: date) -> QuestionIndex:
        """The index serving ``cutoff``: weighted as of its month's first day.

        A petition with no docketing date is left out, since it cannot be placed
        before any cutoff.
        """
        month = cutoff.replace(day=1)
        if self._last is None or self._last[0] != month:
            following = (month + timedelta(days=32)).replace(day=1)
            held = [
                p
                for p in self.petitions.values()
                if p.docketed is not None and p.docketed < following
            ]
            # Only the latest index is kept: each holds a vector per text, so a
            # round's months held at once would hold the frame many times.
            index = QuestionIndex(
                held,
                max_df_share=self.max_df_share,
                counts=self.counts,
                weigh=lambda p: p.docketed is not None and p.docketed < month,
            )
            self._last = (month, index)
        return self._last[1]


def status_on(petition: Petition, cutoff: date) -> str:
    """The petition's status as of ``cutoff``, exclusive: pending until it was resolved."""
    if petition.resolved is None or petition.resolved >= cutoff or petition.disposition is None:
        return "pending"
    return petition.disposition


def same_question_petitions(
    index: QuestionIndex,
    case_id: str,
    cutoff: date,
    *,
    threshold: float = DEFAULT_THRESHOLD,
    limit: int = DEFAULT_LIMIT,
) -> list[SameQuestionEntry]:
    """The petitions docketed before ``cutoff`` that score at least ``threshold``, best first.

    The cutoff is exclusive. A petition with no docketing date is left out,
    since it cannot be placed before the cutoff.
    """
    scored = []
    for other, score in index.scores(case_id).items():
        petition = index.petitions[other]
        if score < threshold or petition.docketed is None or petition.docketed >= cutoff:
            continue
        scored.append((score, petition))
    scored.sort(key=lambda pair: (-pair[0], pair[1].docket_number))
    return [
        SameQuestionEntry(
            docket_number=p.docket_number,
            case_id=p.case_id,
            score=round(min(score, 1.0), 4),
            docketed=p.docketed,
            status=status_on(p, cutoff),
        )
        for score, p in scored[:limit]
    ]


@dataclass(frozen=True)
class CellCutoff:
    """One cell a list is built for: its case, its event, and its exclusive cutoff."""

    case_id: str
    event_id: str
    cutoff: date


def cell_lists(
    frame: QuestionFrame,
    cells: Iterable[CellCutoff],
    *,
    threshold: float = DEFAULT_THRESHOLD,
    limit: int = DEFAULT_LIMIT,
) -> SameQuestionLists:
    """Each cell's list, read from the index as of its own cutoff, in the order given.

    The cells are walked by cutoff, so each month's index is built once and
    dropped before the next (:meth:`QuestionFrame.index`). ``indexed`` counts
    the texts docketed before the cell's cutoff.
    """
    given = list(cells)
    out: dict[int, SameQuestionList] = {}
    for position, cell in sorted(enumerate(given), key=lambda pair: pair[1].cutoff):
        index = frame.index(cell.cutoff)
        own = index.petitions.get(cell.case_id)
        listable = (
            own is not None
            and own.docketed is not None
            and own.docketed < cell.cutoff
            and cell.case_id in index.vectors
        )
        petitions = (
            same_question_petitions(
                index, cell.case_id, cell.cutoff, threshold=threshold, limit=limit
            )
            if listable
            else None
        )
        out[position] = SameQuestionList(
            case_id=cell.case_id,
            event_id=cell.event_id,
            cutoff=cell.cutoff,
            threshold=threshold,
            indexed=sum(
                1
                for case_id in index.vectors
                if (docketed := index.petitions[case_id].docketed) is not None
                and docketed < cell.cutoff
            ),
            petitions=petitions,
        )
    return SameQuestionLists(lists=[out[position] for position in range(len(given))])


class VideAgreement(BaseModel):
    """How the match ranks the petitions the docket itself links as ``Vide``."""

    model_config = ConfigDict(extra="forbid")

    petitions: int = Field(ge=0, description="Indexed petitions")
    linked: int = Field(
        ge=0, description="Indexed petitions with at least one Vide link to another indexed one"
    )
    top1_linked: int = Field(ge=0, description="Of `linked`, whose best match is a Vide link")
    top5_linked: int = Field(ge=0, description="Of `linked`, with a Vide link in the best five")
    link_scores: dict[str, int] = Field(
        description="Each Vide link's score, counted from each linked end, bucketed by "
        "tenths (`0.9` holds [0.9, 1.0])"
    )
    top1_by_score: dict[str, list[int]] = Field(
        description="Every indexed petition's best match, bucketed by score: "
        "`[matches, of which Vide-linked]`, the linked share being a lower bound "
        "on the bucket's precision, since an unlinked match may raise the same question"
    )


def _bucket(score: float) -> str:
    return f"{min(math.floor(score * 10), 9) / 10:.1f}"


def vide_agreement(index: QuestionIndex, vide: Mapping[str, Iterable[str]]) -> VideAgreement:
    """Measure the match against the Vide links, keyed by case id to linked docket numbers."""
    by_number = {
        corpus.normalize_docket_number(p.docket_number) or p.docket_number: case_id
        for case_id, p in index.petitions.items()
    }
    linked = top1 = top5 = 0
    link_scores: Counter[str] = Counter()
    top1_by: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for case_id in sorted(index.vectors):
        partners = {
            by_number[n]
            for n in vide.get(case_id, ())
            if n in by_number and by_number[n] != case_id
        }
        ranked = sorted(
            index.scores(case_id).items(),
            key=lambda kv: (-kv[1], index.petitions[kv[0]].docket_number),
        )
        if ranked:
            best, best_score = ranked[0]
            bucket = top1_by[_bucket(best_score)]
            bucket[0] += 1
            bucket[1] += best in partners
        partners &= set(index.vectors)
        if not partners:
            continue
        linked += 1
        top1 += bool(ranked) and ranked[0][0] in partners
        top5 += any(other in partners for other, _ in ranked[:5])
        scores = dict(ranked)
        for partner in partners:
            link_scores[_bucket(scores.get(partner, 0.0))] += 1
    return VideAgreement(
        petitions=len(index.vectors),
        linked=linked,
        top1_linked=top1,
        top5_linked=top5,
        link_scores=dict(sorted(link_scores.items())),
        top1_by_score={k: v for k, v in sorted(top1_by.items())},
    )
