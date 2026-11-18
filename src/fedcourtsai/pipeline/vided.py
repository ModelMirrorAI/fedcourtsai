"""The filings a SCOTUS docket marks ``VIDED``, read as keys another docket can match.

When one filing serves two or more dockets, the Clerk enters it on each and
ends the entry with ``VIDED``: "Brief amici curiae of Samaritan's Purse, et al.
filed.  VIDED." The Court does not always link those dockets as ``Vide`` in
``RelatedCaseNumber`` (:mod:`.vide_links`), so the shared filing can be the
only trace that two petitions are being considered together. Each docket
serves its own copy of the PDF under its own path, so the link is not in the
URL. It is the entry.

This module reads such an entry as a **key**, of one of two kinds, told apart
by their shape (:func:`is_party_key`).

An **amicus** filing keys as ``<ISO date>|<filer text>``: the entry's own date
and its text less the ``VIDED`` mark, case-folded and with every run of
punctuation and whitespace collapsed to one space. Two dockets that share the
key share a brief.

A **party** filing (a brief in opposition answering two petitions, a reply, a
motion) cannot key on its text. The Clerk words it for each docket's own
caption, so one consolidated opposition reads "respondent A" on one docket and
"respondents A, et al." on the other, while a repeat litigant's oppositions to
unrelated petitions read alike. It keys instead on what the two dockets do
share, the case below: ``<ISO date>|<lower court>|<lower-court number>``, one
key for each number the docket's ``LowerCourtCaseNumbers`` lists, so two
petitions from a consolidated appeal match on any number they have in common.
A docket that names no court below or no number keys no party filing.

The live poll writes a docket's keys to the corpus (``cases.vided_amicus``,
which holds both kinds), so a reader can find a docket's companions with one
query over the few rows that carry any.

A shared key makes a **candidate**, not a fact, and the two kinds differ in
strength. A repeat filer who enters two separate VIDED amicus briefs on one
day, for two unrelated pairs of petitions, writes the same key on all four
dockets, so a predict cell's ``related.json`` names such a companion
``vided-amicus`` with the number of filings the two dockets share as the
strength of the match. A party key matches only two petitions from one case
below that each took a VIDED filing on one day, and its row reads
``vided-party`` (:func:`companion_relation`,
:func:`~fedcourtsai.provision.read_vided`).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any, Final

from .cert_signals import entry_date, proceedings_entries, snapshot_carries_proceedings

#: The relation a ``related.json`` row names for a docket found through a
#: shared VIDED amicus brief rather than linked by the Court as ``Vide``
#: (:data:`~.vide_links.VIDE_RELATION`).
VIDED_AMICUS_RELATION: Final = "vided-amicus"

#: The relation a ``related.json`` row names for a docket found through a VIDED
#: party filing entered the same day on a petition from the same case below.
VIDED_PARTY_RELATION: Final = "vided-party"

#: The Clerk's mark, at the end of the entry, with or without a closing period,
#: and with any trailing parenthetical the Clerk adds after it: a brief filed
#: after distribution reads "... filed.  VIDED. (Distributed)". The
#: parenthetical goes with the mark, so the brief's key is the same on a
#: docket where it arrived before distribution and one where it arrived after.
_VIDED_RE: Final = re.compile(r"\s*\bVIDED\b\.?\s*(?:\([^()]*\)\s*)?$", re.IGNORECASE)

#: The entries a key is read from: an amicus filing. A motion for leave to file
#: a brief as amicus curiae names amicus too and is entered on each docket the
#: brief is, so it reads as a key of its own that both dockets carry.
_AMICUS_RE: Final = re.compile(r"\bamic(?:us|i)\b", re.IGNORECASE)

#: What a party key is read from: a VIDED entry that names a filing. An entry
#: that does not say ``filed`` (an argument setting, a bare grant, a judgment)
#: is not one. The Court's action on a filed motion ("Motion … filed by
#: petitioner GRANTED. VIDED.") still says it and keys too, which costs
#: nothing: the case below is what ties two dockets, not the entry's kind.
_FILED_RE: Final = re.compile(r"\bfiled\b", re.IGNORECASE)

_SEPARATORS_RE: Final = re.compile(r"[\W_]+", re.UNICODE)


def _folded(text: str) -> str:
    return _SEPARATORS_RE.sub(" ", text).strip().casefold()


def vided_key(text: str, raw_date: str | None) -> str | None:
    """The amicus key one entry reads as, or ``None`` if it is not a VIDED amicus filing.

    ``None`` too where the entry carries no fully specified date
    (:func:`~.cert_signals.entry_date`), since a key without its day would
    match the same filer's brief in an unrelated case.
    """
    if not _VIDED_RE.search(text) or not _AMICUS_RE.search(text):
        return None
    filed = entry_date(raw_date)
    if filed is None:
        return None
    filer = _folded(_VIDED_RE.sub("", text))
    return f"{filed.isoformat()}|{filer}" if filer else None


def lower_cases(payload: Mapping[str, Any]) -> list[str]:
    """The case below as ``<lower court>|<number>``, one for each number the docket lists.

    Read off the supremecourt.gov fields ``LowerCourt`` and
    ``LowerCourtCaseNumbers`` (a parenthesized list, comma- or
    semicolon-separated), each folded as a key's text is. Empty where the
    payload names no court or no number, so a number alone never matches the
    same number in another court.
    """
    court = _folded(str(payload.get("LowerCourt") or ""))
    if not court:
        return []
    found: list[str] = []
    for part in re.split(r"[,;]", str(payload.get("LowerCourtCaseNumbers") or "")):
        number = _folded(part)
        if number and f"{court}|{number}" not in found:
            found.append(f"{court}|{number}")
    return found


def vided_party_keys(text: str, raw_date: str | None, below: Iterable[str]) -> list[str]:
    """The party keys one proceedings entry reads as, one for each case in ``below``.

    Empty unless the entry is marked ``VIDED``, says ``filed``, names no amicus
    (:func:`vided_key` reads those) and carries a fully specified date.
    ``below`` is the docket's :func:`lower_cases`. A party's filing that
    mentions an amicus, such as an opposition to a motion for leave to file an
    amicus brief, is read as an amicus entry and keys on its text.
    """
    if not _VIDED_RE.search(text) or _AMICUS_RE.search(text) or not _FILED_RE.search(text):
        return []
    filed = entry_date(raw_date)
    if filed is None:
        return []
    return [f"{filed.isoformat()}|{case}" for case in below]


def is_party_key(key: str) -> bool:
    """Whether ``key`` is a party key rather than an amicus key.

    A party key has three ``|``-separated parts and an amicus key two: folding
    leaves no ``|`` inside a part.
    """
    return key.count("|") == 2


def companion_relation(shared: Iterable[str]) -> tuple[str, int]:
    """The relation and strength of a companion found through the ``shared`` keys.

    ``vided-party`` where any shared key is a party key, since the case below
    ties the two dockets as no filer's name does; ``vided-amicus`` otherwise.
    The strength counts filings, not keys: each shared amicus brief, and each
    day on which both dockets took a VIDED party filing, whatever number of
    lower-court numbers they share.
    """
    keys = set(shared)
    party_days = {key.split("|", 1)[0] for key in keys if is_party_key(key)}
    amicus = sum(1 for key in keys if not is_party_key(key))
    relation = VIDED_PARTY_RELATION if party_days else VIDED_AMICUS_RELATION
    return relation, amicus + len(party_days)


def vided_keys(payload: Mapping[str, Any]) -> list[str] | None:
    """Every VIDED key ``payload`` discloses, amicus and party, sorted and without repeats.

    ``None`` where the docket shows none, and where the payload discloses no
    proceedings at all, so the corpus's fill-in latch keeps a stored reading
    over a degraded poll. The proceedings list is append-only, so a later poll's
    keys contain an earlier poll's, as long as it still names the case below:
    the latch replaces a stored list with any non-empty reading, so a poll that
    shows an amicus key and no lower-court fields would drop the stored party
    keys until the next poll that names them.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    below = lower_cases(payload)
    keys: set[str] = set()
    for text, raw_date in proceedings_entries(payload):
        key = vided_key(text, raw_date)
        if key is not None:
            keys.add(key)
        keys.update(vided_party_keys(text, raw_date, below))
    return sorted(keys) or None
