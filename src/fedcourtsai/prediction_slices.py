"""Prediction slices: committed lower-court case lists the predict scope can admit.

``predict.scope=scotus_docket`` admits a case on its corpus row's court
(``court == "scotus"``). A **slice** widens that by name, never by court: it is
a committed list of lower-court dockets, and switching it on
(``predict.slices`` in ``config/tracking.yaml``) admits exactly the dockets the
list names and nothing else from their courts. The registry below says which
committed file each slice reads, so a second slice is one more entry here and a
list beside it, not new scope code.

Every slice is its own **population**: the SCOTUS docket is one, and each slice
is another. A population is orthogonal to the forward / retrospective stratum
the scoring join assigns (:func:`fedcourtsai.integrity.classify_stratum`): it
says which docket a cell's case belongs to, and the SCOTUS figures — the
leaderboard, the claim boards, the big-case board, the window records and the
public exports — read the SCOTUS population only (:data:`SCOTUS_POPULATION`),
so a slice's events never pool with the Court's. Two consequences are part of
the design rather than options:

- **No docket is in two populations.** :func:`load_slices` refuses two enabled
  slices that name one docket, so a cell can never be counted in two figures.
- **The salience gate does not apply to a slice.** Salience scores SCOTUS
  petitions for a capacity slice of the Court's docket; a slice's list is the
  selection, so the matrix backstop never drops a slice case as
  salience-deferred.

Admitting a slice's cases is only the scope half. A slice is switched on
together with its own moments, prompts and decision model, and under its own
process version (``docs/process-version.md``), so that no SCOTUS digest moves
when a slice opens; until those exist the registry's slices stay off.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from . import ids
from .ai_watchlist import AI_WATCHLIST_FILENAME, load_ai_watchlist, tagged_case_ids

#: The population key of the SCOTUS docket, the one ``scotus_docket`` admits.
SCOTUS_POPULATION_KEY = "scotus"


@dataclass(frozen=True)
class Population:
    """One population of predicted cases: the SCOTUS docket, or one slice's list.

    ``court`` admits every docket of one court (the SCOTUS population only);
    ``case_ids`` admits exactly the named dockets (a slice). Exactly one is set.
    """

    key: str
    court: str | None = None
    case_ids: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if (self.court is None) == (self.case_ids is None):
            raise ValueError(f"population {self.key!r} names a court or a case list, not both")

    def admits(self, court_id: str, docket_id: int) -> bool:
        """Whether the docket ``court_id/docket_id`` belongs to this population."""
        if self.court is not None:
            return court_id == self.court
        return self.case_ids is not None and ids.case_id(court_id, docket_id) in self.case_ids

    def admits_case(self, case_id: str) -> bool:
        """:meth:`admits` over a ``<court>/<docket>`` case id."""
        court_id, _, docket = case_id.partition("/")
        return docket.isdigit() and self.admits(court_id, int(docket))


#: The SCOTUS docket: every population-scoped reader's default.
SCOTUS_POPULATION = Population(key=SCOTUS_POPULATION_KEY, court="scotus")


@dataclass(frozen=True)
class SliceSource:
    """Where one slice's committed list lives and how its dockets are read off it."""

    #: The file under the config root that holds the list.
    filename: str
    #: The dockets the list admits, as ``<court>/<docket>`` case ids.
    case_ids: Callable[[Path], frozenset[str]]
    #: One line on what the slice is, for the refusal a bad config gets.
    description: str


def _watchlist_case_ids(path: Path) -> frozenset[str]:
    """Every docket the AI-case watchlist names: each case's own and its related ones."""
    return tagged_case_ids(load_ai_watchlist(path))


#: The slices the scope can admit, by id. An entry names a committed list; it
#: does not switch the slice on, which ``predict.slices`` does.
SLICES: Mapping[str, SliceSource] = MappingProxyType(
    {
        "ai-watchlist": SliceSource(
            filename=AI_WATCHLIST_FILENAME,
            case_ids=_watchlist_case_ids,
            description="the AI-case watchlist's listed cases and their related dockets",
        ),
    }
)


class SliceOverlapError(ValueError):
    """Two enabled slices name the same docket, so its population would be ambiguous."""


def check_slice_ids(slice_ids: Iterable[str]) -> list[str]:
    """``slice_ids`` as a list, refusing an unknown or repeated id."""
    names = list(slice_ids)
    unknown = sorted(set(names) - set(SLICES))
    if unknown:
        raise ValueError(f"unknown prediction slice(s) {unknown}; known: {sorted(SLICES)}")
    if len(set(names)) != len(names):
        raise ValueError(f"prediction slices must be distinct: {names}")
    return names


def load_slices(config_root: Path, slice_ids: Iterable[str]) -> dict[str, Population]:
    """Each enabled slice's population, read off its committed list under ``config_root``.

    A missing list is an error, not an empty slice: a switched-on slice whose
    file is gone would otherwise plan nothing and look like a quiet day. A
    SCOTUS docket in a list is refused (the SCOTUS population already holds it),
    and so is a docket two enabled slices both name.
    """
    populations: dict[str, Population] = {}
    owner: dict[str, str] = {}
    for slice_id in check_slice_ids(slice_ids):
        source = SLICES[slice_id]
        path = config_root / source.filename
        if not path.exists():
            raise FileNotFoundError(
                f"prediction slice {slice_id!r} ({source.description}) is enabled but "
                f"its list {path} is missing"
            )
        case_ids = source.case_ids(path)
        for case_id in sorted(case_ids):
            if SCOTUS_POPULATION.admits_case(case_id):
                raise ValueError(
                    f"prediction slice {slice_id!r} names SCOTUS docket {case_id}; "
                    "a SCOTUS docket is in the SCOTUS population"
                )
            if case_id in owner:
                raise SliceOverlapError(
                    f"docket {case_id} is in prediction slices {owner[case_id]!r} and "
                    f"{slice_id!r}; a docket belongs to one population"
                )
            owner[case_id] = slice_id
        populations[slice_id] = Population(key=slice_id, case_ids=frozenset(case_ids))
    return populations


def population_of(case_id: str, slices: Mapping[str, Population]) -> str | None:
    """The population key of ``case_id``: ``scotus``, an enabled slice's id, or ``None``.

    ``None`` is a case no population admits, which ``scotus_docket`` keeps out of
    the predict scope.
    """
    if SCOTUS_POPULATION.admits_case(case_id):
        return SCOTUS_POPULATION_KEY
    for slice_id, population in slices.items():
        if population.admits_case(case_id):
            return slice_id
    return None
