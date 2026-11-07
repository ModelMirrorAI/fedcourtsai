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

# The separators between the numbers of one ``DisplayCaseNumber`` that names
# several dockets: the Court writes a group of companions into a single entry
# ("26-199, 26-201, 26-332, 26-335"), so each listed number is read on its own.
_DISPLAY_NUMBER_SPLIT_RE = re.compile(r"[,;&]|\band\b", re.IGNORECASE)


def related_file_number(raw: str) -> str | None:
    """``raw`` as a docket number a ``record/related/`` file may be named by, or ``None``.

    Normalized (:func:`~fedcourtsai.corpus.normalize_docket_number`) and shaped
    as a SCOTUS docket number, so every reader that stages a related docket
    names its file by one rule.
    """
    number = normalize_docket_number(raw)
    if number is None or not _RELATED_NUMBER_RE.match(number):
        return None
    return number


def vide_docket_numbers(payload: Mapping[str, Any]) -> tuple[str, ...]:
    """The docket numbers ``payload`` links as ``Vide``, normalized, in served order.

    Read off ``RelatedCaseNumber``, the list the Court's JSON carries on both
    sides of the link (``{"DisplayCaseNumber": "25-1323", "RelatedType":
    "Vide"}``). Any other relation type is skipped, as are the docket's own
    number, a repeat and a number not shaped as a SCOTUS docket number, and the
    list stops at :data:`MAX_RELATED_DOCKETS`. One entry may list several
    dockets in its ``DisplayCaseNumber`` ("26-199, 26-201"); each is read in the
    order written, under the same rules, so a malformed part drops only itself. A caller passes the payload the
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
        display = str(item.get("DisplayCaseNumber") or "")
        for part in _DISPLAY_NUMBER_SPLIT_RE.split(display):
            number = related_file_number(part)
            if number is None or number == own or number in numbers:
                continue
            numbers.append(number)
    return tuple(numbers[:MAX_RELATED_DOCKETS])
