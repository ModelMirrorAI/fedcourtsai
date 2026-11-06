"""The amicus filings a SCOTUS docket marks ``VIDED``, read as keys another docket can match.

When one amicus brief supports petitions on two or more dockets, the Clerk
enters it on each and ends the entry with ``VIDED``: "Brief amici curiae of
Samaritan's Purse, et al. filed.  VIDED." The Court does not always link those
dockets as ``Vide`` in ``RelatedCaseNumber`` (:mod:`.vide_links`), so the shared
brief can be the only trace that two petitions are being considered together.
Each docket serves its own copy of the PDF under its own path, so the link is
not in the URL. It is the entry: the same filer, filed the same day, marked
``VIDED`` on both dockets.

This module reads that entry as a **key**, ``<ISO date>|<filer text>``: the
entry's own date and its text less the ``VIDED`` mark, case-folded and with
every run of punctuation and whitespace collapsed to one space. Two dockets
that share a key share a brief. The live poll writes a docket's keys to the
corpus (``cases.vided_amicus``), so a reader can find a docket's companions
with one query over the few rows that carry any.

A shared key makes a **candidate**, not a fact. A repeat filer who enters two
separate VIDED briefs on one day, for two unrelated pairs of petitions, writes
the same key on all four dockets, so a predict cell's ``related.json`` names
such a companion ``vided-amicus`` rather than ``Vide``, with the number of
keys the two dockets share as the strength of the match
(:func:`~fedcourtsai.provision.read_vided`).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

from .cert_signals import entry_date, proceedings_entries, snapshot_carries_proceedings

#: The relation a ``related.json`` row names for a docket found through a
#: shared VIDED amicus brief rather than linked by the Court as ``Vide``
#: (:data:`~.vide_links.VIDE_RELATION`).
VIDED_AMICUS_RELATION: Final = "vided-amicus"

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

_SEPARATORS_RE: Final = re.compile(r"[\W_]+", re.UNICODE)


def vided_key(text: str, raw_date: str | None) -> str | None:
    """The key one proceedings entry reads as, or ``None`` if it is not a VIDED amicus filing.

    ``None`` too where the entry carries no fully specified date
    (:func:`~.cert_signals.entry_date`), since a key without its day would
    match the same filer's brief in an unrelated case.
    """
    if not _VIDED_RE.search(text) or not _AMICUS_RE.search(text):
        return None
    filed = entry_date(raw_date)
    if filed is None:
        return None
    filer = _SEPARATORS_RE.sub(" ", _VIDED_RE.sub("", text)).strip().casefold()
    return f"{filed.isoformat()}|{filer}" if filer else None


def vided_amicus_keys(payload: Mapping[str, Any]) -> list[str] | None:
    """Every VIDED amicus key ``payload`` discloses, sorted and without repeats.

    ``None`` where the docket shows none, and where the payload discloses no
    proceedings at all, so the corpus's fill-in latch keeps a stored reading
    over a degraded poll. The proceedings list is append-only, so a later poll's
    keys contain an earlier poll's.
    """
    if not snapshot_carries_proceedings(payload):
        return None
    keys = {
        key
        for text, raw_date in proceedings_entries(payload)
        if (key := vided_key(text, raw_date)) is not None
    }
    return sorted(keys) or None
