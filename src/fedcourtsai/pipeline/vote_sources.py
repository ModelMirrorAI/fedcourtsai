"""The registered vote sources: what may put a vote list into public git.

``Outcome.votes`` lands in ``data/``, which is public, so a vote list is a
publication, and it may cite only a source registered in
``docs/data-sources.md``. This module is that registration in code: each
:class:`VoteSource` names what its records must look like, and ``validate``'s
``outcome_votes_await_a_registered_source`` check holds every committed outcome
to it. A vote list naming any other source — SCDB included, whose terms are
unsettled — is refused, and so is a list with no provenance block at all.

A source is registered here in the same change that registers it in
``docs/data-sources.md``, and only then.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Final

from ..schemas import Stage
from ..supremecourt import is_court_url
from .justices import bench_on
from .syllabus_lineup import COURT as SYLLABUS_COURT
from .syllabus_lineup import GRAMMAR_NAME as SYLLABUS_GRAMMAR

#: The Court's own opinions, read through the syllabus lineup grammar.
SUPREMECOURT_OPINIONS: Final = "supremecourt-opinions"


@dataclass(frozen=True)
class VoteSource:
    """One registered vote source and the shape its records must take.

    ``courts`` and ``stages`` bound where its lists may appear; ``grammars``
    are the readers whose stamp a record may carry; ``document`` says whether
    a record's ``VoteProvenance.document`` is one this source reads; and
    ``bench``, where the source records whole benches, is the bench on an
    outcome's ``resolved_at`` that a complete record must name exactly — so
    ``complete: true``, the bit vote scoring is gated on, is checked against
    the roster rather than taken on the record's word.
    """

    source: str
    courts: frozenset[str]
    stages: frozenset[Stage]
    grammars: frozenset[str]
    document: Callable[[str], bool]
    bench: Callable[[date], tuple[str, ...]] | None = None


#: Every registered vote source, by ``VoteProvenance.source``.
REGISTERED_VOTE_SOURCES: Final[Mapping[str, VoteSource]] = MappingProxyType(
    {
        SUPREMECOURT_OPINIONS: VoteSource(
            source=SUPREMECOURT_OPINIONS,
            courts=frozenset({SYLLABUS_COURT}),
            stages=frozenset({Stage.merits}),
            grammars=frozenset({SYLLABUS_GRAMMAR}),
            document=is_court_url,
            bench=bench_on,
        ),
    }
)
