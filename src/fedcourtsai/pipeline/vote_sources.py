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

Two are registered, both the Court's own public-domain documents:

- ``supremecourt-opinions`` — the syllabus lineup of a signed merits opinion,
  a whole bench (``complete``) or nothing;
- ``supremecourt-orders`` — the cert- and interim-stage notations and
  separate-writing headers of the Court's orders, which are never a whole
  bench of votes: a Justice who noted nothing is unobserved, so its records
  are always partial, and ``complete: true`` from it is refused. Vote scoring
  never reads them either way, since it is gated on a merits moment
  (:func:`fedcourtsai.pipeline.moments.scores_votes`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Final
from urllib.parse import unquote, urlsplit

from ..schemas import Stage
from ..supremecourt import is_court_url
from .justices import bench_on
from .order_grammars import COURT as ORDERS_COURT
from .order_grammars import HEADERS_GRAMMAR, NOTATIONS_GRAMMAR
from .syllabus_lineup import COURT as SYLLABUS_COURT
from .syllabus_lineup import GRAMMAR_NAME as SYLLABUS_GRAMMAR

#: The Court's own opinions, read through the syllabus lineup grammar.
SUPREMECOURT_OPINIONS: Final = "supremecourt-opinions"

#: The Court's orders, read through the order-notation and writing-header grammars.
SUPREMECOURT_ORDERS: Final = "supremecourt-orders"


def _has_dot_segment(path: str) -> bool:
    """Whether any path segment is, or percent-decodes to, ``.`` or ``..``."""
    return any(unquote(segment) in {".", ".."} for segment in path.split("/"))


def is_opinion_pdf(url: str) -> bool:
    """Whether ``url`` is an opinion PDF on the Court's own host.

    Narrower than the host rule alone: the Court's host also serves docket
    JSON and filed briefs, none of which is a document this source reads.
    """
    if not is_court_url(url):
        return False
    path = urlsplit(url).path
    if _has_dot_segment(path):
        return False
    return path.startswith("/opinions/") and path.lower().endswith(".pdf")


def is_order_document_url(url: str) -> bool:
    """Whether ``url`` is an order or opinion PDF on the Court's own host.

    The documents the orders source reads: order lists and miscellaneous orders
    under ``/orders/``, and opinions relating to orders under ``/opinions/``.
    """
    if not is_court_url(url):
        return False
    path = urlsplit(url).path
    if _has_dot_segment(path):
        return False
    return path.lower().endswith(".pdf") and (
        path.startswith("/orders/") or path.startswith("/opinions/")
    )


@dataclass(frozen=True)
class VoteSource:
    """One registered vote source and the shape its records must take.

    ``courts`` and ``stages`` bound where its lists may appear; ``grammars``
    are the readers whose stamp a record may carry; ``document`` says whether
    each of a record's ``VoteProvenance.documents`` is one this source reads;
    ``bench`` is the bench the roster seats on an outcome's ``resolved_at``,
    which every Justice a record names must sit on, which a complete record
    must name exactly, and from which a record's ``participating`` is counted
    — so ``complete: true``, the bit vote scoring is gated on, is checked
    against the roster rather than taken on the record's word. ``complete``
    says whether the source can record a whole bench of votes at all; a
    source that cannot has ``complete: true`` refused outright.
    """

    source: str
    courts: frozenset[str]
    stages: frozenset[Stage]
    grammars: frozenset[str]
    document: Callable[[str], bool]
    bench: Callable[[date], tuple[str, ...]] | None = None
    complete: bool = True


#: Every registered vote source, by ``VoteProvenance.source``.
REGISTERED_VOTE_SOURCES: Final[Mapping[str, VoteSource]] = MappingProxyType(
    {
        SUPREMECOURT_OPINIONS: VoteSource(
            source=SUPREMECOURT_OPINIONS,
            courts=frozenset({SYLLABUS_COURT}),
            stages=frozenset({Stage.merits}),
            grammars=frozenset({SYLLABUS_GRAMMAR}),
            document=is_opinion_pdf,
            bench=bench_on,
        ),
        SUPREMECOURT_ORDERS: VoteSource(
            source=SUPREMECOURT_ORDERS,
            courts=frozenset({ORDERS_COURT}),
            stages=frozenset({Stage.cert, Stage.interim}),
            grammars=frozenset({NOTATIONS_GRAMMAR, HEADERS_GRAMMAR}),
            document=is_order_document_url,
            bench=bench_on,
            complete=False,
        ),
    }
)
