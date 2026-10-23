"""The dockets a SCOTUS docket links as ``Vide``, read off its own payload.

A leaf over the corpus's docket-number normalizer, so both readers take one
rule: the provisioner, which stages each linked docket under
``record/related/``, and the cell context, which freezes the list on the
prediction so a board can cut a forecast by whether its docket was linked.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

from ..corpus import normalize_docket_number

#: The relation the Court's docket JSON writes on a linked docket in its
#: ``RelatedCaseNumber`` list: a cross-petition, a companion case, or the
#: petition this one is held for, linked on both sides.
VIDE_RELATION: Final = "Vide"

#: At most this many linked dockets are staged, in the order the Court lists
#: them. Each costs a snapshot read, and a docket linked to more than a handful
#: is a group whose lead the cell's own snapshot already names.
MAX_RELATED_DOCKETS: Final = 4

# A SCOTUS docket number as `normalize_docket_number` leaves it: a two-digit
# Term, the form letter (`-` for a petition, `A` for an application, `O` for an
# original action) and the sequence. The number becomes a file name under
# `record/related/`, so anything else upstream serves is refused, as a document
# kind is (`_checked_kind`).
_RELATED_NUMBER_RE = re.compile(r"^\d{2}[-AO]\d{1,5}$")


def vide_docket_numbers(payload: Mapping[str, Any]) -> tuple[str, ...]:
    """The docket numbers ``payload`` links as ``Vide``, normalized, in served order.

    Read off ``RelatedCaseNumber``, the list the Court's JSON carries on both
    sides of the link (``{"DisplayCaseNumber": "25-1323", "RelatedType":
    "Vide"}``). Any other relation type is skipped, as are the docket's own
    number, a repeat and a number not shaped as a SCOTUS docket number, and the
    list stops at :data:`MAX_RELATED_DOCKETS`. A caller passes the payload the
    cell is placed on, so a link the Court added after the cell's moment is not
    read off a ``dated`` snapshot; a ``truncated`` one keeps the latest list,
    since the field is undated.
    """
    linked = payload.get("RelatedCaseNumber")
    if not isinstance(linked, list):
        return ()
    own = normalize_docket_number(str(payload.get("CaseNumber") or ""))
    numbers: list[str] = []
    for item in linked:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("RelatedType") or "").strip().lower() != VIDE_RELATION.lower():
            continue
        number = normalize_docket_number(str(item.get("DisplayCaseNumber") or ""))
        if number is None or not _RELATED_NUMBER_RE.match(number):
            continue
        if number == own or number in numbers:
            continue
        numbers.append(number)
    return tuple(numbers[:MAX_RELATED_DOCKETS])
