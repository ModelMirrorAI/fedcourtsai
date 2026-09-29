"""The lineup model: who voted how, and who wrote what, in one decision.

A court's published lineup — the paragraph that closes a Supreme Court
syllabus, a circuit opinion's panel recital, an order list's noted votes —
says two different things, and this model keeps them apart because they are
observed differently:

- **Writings** (:class:`Writing`): each opinion filed, its kind, its author,
  and who joined it, in full or in part. A final opinion discloses every
  writing, so once a grammar has read the whole lineup the absence of a
  writing is itself an observation (:attr:`Lineup.writings_complete`).
- **Votes** (:attr:`Lineup.votes`): each Justice's side, on the shared
  :class:`~fedcourtsai.schemas.VoteValue` vocabulary. A vote list may be
  **partial** — an order list names only the Justices who noted a vote, so
  the silent ones are unobserved rather than absent — and
  :attr:`Lineup.complete` says whether every participating Justice is
  accounted for. A partial list is a legitimate lineup, never an error.

The model is court-neutral: names are the strings a grammar resolved them to,
and the bench and quorum are the caller's. A **grammar** reads one source's
text into a :class:`Lineup` and stamps its own name and version on the result
(:class:`LineupGrammar`), so a grammar fix can re-read cached text and the
reader can tell which reading a stored lineup came from. The SCOTUS syllabus
grammar is :mod:`fedcourtsai.pipeline.syllabus_lineup`; an order-list grammar,
a separate-writing-header grammar, or a circuit panel grammar sits beside it
over this same model.

:func:`lineup_from_writings` is the shared derivation from a complete set of
writings to votes — the part of a merits lineup that is the same for every
court whose opinions carry joins. It never guesses: any problem a grammar
reports empties the vote list rather than leaving a best-effort reading in it,
and a Justice the writings do not account for keeps the lineup incomplete.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Protocol

from ..schemas import JusticeVote, VoteValue, WritingRole


class WritingKind(StrEnum):
    """What kind of opinion one writing is.

    Finer than :class:`~fedcourtsai.schemas.WritingRole`, because a vote is
    derived from it: "concurring in part and concurring in the judgment"
    (joined some of the Court's opinion) and "concurring in part and
    dissenting in part" (on both sides) put their author on different sides,
    so neither may collapse into a plain concurrence or dissent here. Which
    role each kind records as on ``Outcome.votes`` is :data:`WRITING_ROLES`.
    """

    opinion_of_the_court = "opinion-of-the-court"
    plurality = "plurality"
    per_curiam = "per-curiam"
    concurrence = "concurrence"
    concurrence_in_part = "concurrence-in-part"
    concurrence_in_judgment = "concurrence-in-judgment"
    concurrence_in_part_dissent_in_part = "concurrence-in-part-dissent-in-part"
    dissent = "dissent"
    statement = "statement"


#: The schema role each writing kind records as on ``JusticeVote.writing``, or
#: ``None`` where no role says it faithfully. ``WritingRole`` has one value per
#: Justice and no member for a writing on both sides, so the two mixed kinds —
#: "concurring in part and concurring in the judgment" (joined some of the
#: Court's opinion, so neither a plain concurrence nor a concurrence in the
#: judgment alone) and "concurring in part and dissenting in part" — record
#: nothing rather than the nearer of two wrong roles. A per curiam has no
#: author to record it.
WRITING_ROLES: Final[Mapping[WritingKind, WritingRole | None]] = MappingProxyType(
    {
        WritingKind.opinion_of_the_court: WritingRole.majority,
        WritingKind.plurality: WritingRole.plurality,
        WritingKind.per_curiam: None,
        WritingKind.concurrence: WritingRole.concurrence,
        WritingKind.concurrence_in_part: None,
        WritingKind.concurrence_in_judgment: WritingRole.concurrence_in_judgment,
        WritingKind.concurrence_in_part_dissent_in_part: None,
        WritingKind.dissent: WritingRole.dissent,
        WritingKind.statement: WritingRole.statement,
    }
)

#: The kinds that carry the disposition — at most one per lineup.
LEAD_KINDS: Final[frozenset[WritingKind]] = frozenset(
    {WritingKind.opinion_of_the_court, WritingKind.plurality, WritingKind.per_curiam}
)

#: Separate writings whose author or joiners did not join the lead opinion in
#: full. The Court's convention that a lead clause without its own joiner list
#: was joined by everyone else excludes exactly these Justices.
NOT_JOINING_LEAD_KINDS: Final[frozenset[WritingKind]] = frozenset(
    {
        WritingKind.concurrence_in_part,
        WritingKind.concurrence_in_judgment,
        WritingKind.concurrence_in_part_dissent_in_part,
        WritingKind.dissent,
    }
)


@dataclass(frozen=True)
class Join:
    """One Justice joining one writing.

    ``qualifier`` is the printed limit ("as to Part II-B", "except as to
    Part IV-B", "with respect to Parts I and II"); ``None`` is a join in full.
    """

    justice: str
    qualifier: str | None = None

    @property
    def partial(self) -> bool:
        return self.qualifier is not None


@dataclass(frozen=True)
class Writing:
    """One opinion filed in the decision.

    ``author`` is ``None`` only for a per curiam, which nobody signs.
    ``coauthors`` are the other signers of a jointly written opinion ("BREYER,
    SOTOMAYOR, and KAGAN, JJ., filed a dissenting opinion"): authors in their
    own right, not joiners, so each records the writing as their own.
    ``scope`` is the lead opinion's own limit where the author's opinion is
    the Court's for only some parts ("except as to Part II"); a separate
    writing leaves it ``None``.
    """

    kind: WritingKind
    author: str | None
    joins: tuple[Join, ...] = ()
    scope: str | None = None
    coauthors: tuple[str, ...] = ()

    @property
    def authors(self) -> tuple[str, ...]:
        """Everyone who signed this writing as its author."""
        return ((self.author,) if self.author else ()) + self.coauthors

    @property
    def joiners(self) -> frozenset[str]:
        """Everyone who joined any part of this writing, author excluded."""
        return frozenset(join.justice for join in self.joins)

    @property
    def signatories(self) -> frozenset[str]:
        """Every author plus every joiner, in full or in part."""
        return self.joiners | frozenset(self.authors)


@dataclass(frozen=True)
class Lineup:
    """One decision's lineup as one grammar read it.

    ``votes`` carries only observed votes; a Justice absent from it is
    unobserved. ``complete`` is true only when every Justice on ``bench`` is
    accounted for — a side, or ``did-not-participate`` — with no problem
    reported, and it is the one field that lets a consumer treat the vote
    list as the whole bench. ``writings_complete`` is the same claim about
    writings: every participating Justice's writing role is observed, so a
    Justice who authored nothing is observed to have written nothing.
    ``problems`` says, in words, why either is false.
    """

    court: str
    grammar: str
    grammar_version: int
    bench: tuple[str, ...]
    writings: tuple[Writing, ...] = ()
    votes: Mapping[str, VoteValue] = field(default_factory=lambda: MappingProxyType({}))
    complete: bool = False
    writings_complete: bool = False
    problems: tuple[str, ...] = ()

    @property
    def lead(self) -> Writing | None:
        """The writing that carries the disposition, if the lineup read one."""
        return next((w for w in self.writings if w.kind in LEAD_KINDS), None)

    @property
    def participating(self) -> int | None:
        """How many Justices took part — known only for a complete lineup.

        ``None`` otherwise: on a partial list the count of non-recused names
        is a floor, not the denominator a vote threshold counts against.
        """
        if not self.complete:
            return None
        return sum(1 for vote in self.votes.values() if vote is not VoteValue.did_not_participate)

    @property
    def writing_roles(self) -> Mapping[str, tuple[WritingKind, ...]]:
        """Each Justice's own writings, by kind.

        Authors only, unless ``writings_complete``: then every participating
        Justice appears, and an empty tuple is the observation that they wrote
        nothing — never inferred from a lineup that could have missed one.
        """
        roles: dict[str, list[WritingKind]] = {}
        if self.writings_complete:
            for justice in self.bench:
                if self.votes.get(justice) is not VoteValue.did_not_participate:
                    roles[justice] = []
        for writing in self.writings:
            for author in writing.authors:
                roles.setdefault(author, []).append(writing.kind)
        return MappingProxyType({justice: tuple(kinds) for justice, kinds in roles.items()})


class LineupGrammar(Protocol):
    """A reader from one source's lineup text onto :class:`Lineup`.

    ``name`` and ``version`` are stamped on every lineup it returns. Bump
    ``version`` whenever a change could read the same text differently, so a
    stored lineup says which reading it is and cached text can be re-read.
    """

    @property
    def court(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> int: ...

    def parse(self, text: str, *, bench: Sequence[str]) -> Lineup: ...


def _derive_vote(justice: str, lead: Writing, separate: Sequence[Writing]) -> VoteValue | None:
    """One participating Justice's side, or ``None`` when the writings do not say.

    A Justice who joined any part of the lead opinion is on its side unless
    they also wrote or joined a dissent (then both sides); one who did not
    join it is placed by their separate writings alone. A plain concurrence
    without any join of the lead places nobody, because it does not say
    whether its author supported the judgment.
    """
    kinds = {w.kind for w in separate if justice in w.signatories}
    joined_lead = justice in lead.signatories
    dissenting = WritingKind.dissent in kinds
    if WritingKind.concurrence_in_part_dissent_in_part in kinds:
        return VoteValue.concur_in_part
    if dissenting:
        in_support = (
            joined_lead
            or WritingKind.concurrence_in_part in kinds
            or WritingKind.concurrence_in_judgment in kinds
        )
        return VoteValue.concur_in_part if in_support else VoteValue.dissent
    if joined_lead or WritingKind.concurrence_in_part in kinds:
        return VoteValue.majority
    if WritingKind.concurrence_in_judgment in kinds:
        return VoteValue.concur_in_judgment
    return None


def _join_conflicts(writing: Writing) -> list[str]:
    """A writing whose joiner list repeats a name or names its own author."""
    found: list[str] = []
    seen: set[str] = set()
    for join in writing.joins:
        if join.justice in writing.authors:
            found.append(f"{join.justice} joins their own {writing.kind}")
        elif join.justice in seen:
            found.append(f"{join.justice} joins one {writing.kind} twice")
        seen.add(join.justice)
    return found


def _side_conflicts(lead: Writing, separate: Sequence[Writing]) -> list[str]:
    """Justices a reading puts wholly behind the lead and also against it.

    Both sides is a real vote only where the lead join is qualified; the
    lead's author, or a Justice joining it in full, who also signs a dissent
    is a text that contradicts itself, which is how a misread or a merged
    paragraph shows up. Refused, never resolved to both sides.
    """
    full = set(lead.authors) | {j.justice for j in lead.joins if not j.partial}
    against = {
        name
        for w in separate
        if w.kind in {WritingKind.dissent, WritingKind.concurrence_in_part_dissent_in_part}
        for name in w.signatories
    }
    return [
        f"{name} is read as joining the lead in full and as dissenting"
        for name in sorted(full & against)
    ]


def lineup_from_writings(
    *,
    court: str,
    grammar: str,
    grammar_version: int,
    bench: Sequence[str],
    writings: Iterable[Writing],
    took_no_part: Iterable[str] = (),
    problems: Iterable[str] = (),
    quorum: int,
) -> Lineup:
    """Derive votes and completeness from a merits decision's writings.

    ``bench`` is every Justice who could have sat; ``took_no_part`` those the
    source says did not, recorded as ``did-not-participate`` (a syllabus does
    not say whether a non-participation is a recusal). ``problems`` are the
    grammar's own: any one of them empties the vote list, because a lineup
    read around an unparsed sentence could be missing the very dissent that
    would move a Justice's side. The writings themselves are kept — each is a
    direct reading, not an inference.
    """
    bench_t = tuple(bench)
    writings_t = tuple(writings)
    absent = frozenset(took_no_part)
    found = list(problems)

    leads = [w for w in writings_t if w.kind in LEAD_KINDS]
    if len(leads) != 1:
        found.append(f"expected exactly one lead opinion, read {len(leads)}")
    on_bench = set(bench_t)
    for name in sorted(absent - on_bench):
        found.append(f"{name} took no part but is not on the bench")
    for writing in writings_t:
        for name in sorted(writing.signatories - on_bench):
            found.append(f"{name} signs a {writing.kind} but is not on the bench")
        for name in sorted(writing.signatories & absent):
            found.append(f"{name} took no part but signs a {writing.kind}")
        found.extend(_join_conflicts(writing))
    if len(leads) == 1:
        found.extend(_side_conflicts(leads[0], [w for w in writings_t if w is not leads[0]]))

    if found:
        return Lineup(
            court=court,
            grammar=grammar,
            grammar_version=grammar_version,
            bench=bench_t,
            writings=writings_t,
            problems=tuple(found),
        )

    lead = leads[0]
    separate = [w for w in writings_t if w is not lead]
    votes: dict[str, VoteValue] = {}
    for justice in bench_t:
        if justice in absent:
            votes[justice] = VoteValue.did_not_participate
            continue
        vote = _derive_vote(justice, lead, separate)
        if vote is None:
            found.append(f"{justice} is not accounted for by any writing")
        else:
            votes[justice] = vote

    participating = len(bench_t) - len(absent)
    if participating < quorum:
        found.append(f"{participating} participating is below the quorum of {quorum}")

    complete = not found
    return Lineup(
        court=court,
        grammar=grammar,
        grammar_version=grammar_version,
        bench=bench_t,
        writings=writings_t,
        votes=MappingProxyType(votes),
        complete=complete,
        writings_complete=complete,
        problems=tuple(found),
    )


def writing_role(kinds: Sequence[WritingKind]) -> WritingRole | None:
    """One Justice's ``JusticeVote.writing`` from the kinds they authored.

    ``none`` for an observed empty tuple (see :attr:`Lineup.writing_roles`);
    the kind's role (:data:`WRITING_ROLES`) when every writing maps to one and
    the same role; otherwise ``None``, "not stated". A Justice who wrote two
    writings of different roles — the Court's opinion and a concurrence to it,
    a concurrence and a dissent — has no single role that is true, and a
    mixed kind has none at all, so neither is forced onto the nearest value.
    """
    if not kinds:
        return WritingRole.none
    roles = {WRITING_ROLES[kind] for kind in kinds}
    if len(roles) != 1:
        return None
    return roles.pop()


def justice_votes(lineup: Lineup) -> list[JusticeVote]:
    """A lineup's observed votes on the schema's per-Justice shape, in bench order.

    ``writing`` is :func:`writing_role` wherever the lineup observed the
    Justice's writings — every participating Justice when
    ``writings_complete``, authors only otherwise — and ``None`` (not stated)
    everywhere else, so an incomplete reading never claims a Justice wrote
    nothing. A Justice who took no part records no writing either.
    """
    roles = lineup.writing_roles
    votes: list[JusticeVote] = []
    for justice in lineup.bench:
        vote = lineup.votes.get(justice)
        if vote is None:
            continue
        kinds = roles.get(justice)
        writing = None if kinds is None else writing_role(kinds)
        votes.append(JusticeVote(justice=justice, vote=vote, writing=writing))
    return votes
