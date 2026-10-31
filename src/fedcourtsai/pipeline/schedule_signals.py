"""Forward-looking dates the Court sets on a docket: argument, and the response deadline.

Two readings off the proceedings text the live channel already polls, written
to the corpus at ingest and read by :mod:`fedcourtsai.schedule`, which publishes
the dates still ahead for the public site's case timeline:

- **The argument day** (:func:`argument_set_date`): the date the newest
  ``SET FOR ARGUMENT on …`` entry names. A rescheduled argument gets a fresh
  entry, so the last one in docket order is the current setting.
- **The response deadline** (:func:`response_deadline`): the date a response
  to the petition or application is due, and whether it is still owed. The
  proceedings are walked in docket order as a small state machine. An entry
  that states a deadline — the docketing entry's ``(Response due …)``, a call
  for response's ``(Due …)``, a granted extension's "extended to and including
  …", a Justice's request for a response to an application — sets the date and
  makes the response ``due``. A response, brief in opposition or memorandum
  the respondent files makes it ``filed``, and a waiver of the right to respond makes it
  ``waived``, until a later entry states a new deadline.

Neither date is a cell input. The columns they land in are withheld from the
retrieval surface (:data:`fedcourtsai.corpus.RETRIEVAL_WITHHELD_COLUMNS`), and
the schedule built from them is held out of provisioning by a test.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, Literal

from .cert_signals import proceedings_entries, snapshot_carries_proceedings

ResponseState = Literal["due", "filed", "waived"]

#: A calendar date as the Clerk writes it in entry text: "November 3, 2026".
_DAY = (
    r"((?:January|February|March|April|May|June|July|August|September|October|November|"
    r"December)\s+\d{1,2},?\s+\d{4})"
)

#: The argument setting: "SET FOR ARGUMENT on Monday, November 3, 2026."
_SET_FOR_ARGUMENT_RE = re.compile(
    r"^\s*SET\s+FOR\s+ARGUMENT\s+on\s+(?:[A-Za-z]+day,?\s+)?" + _DAY, re.IGNORECASE
)

#: A deadline stated in parentheses on the docketing or call-for-response entry:
#: "Petition for a writ of certiorari filed. (Response due July 2, 2026)" and
#: "Response Requested. (Due September 11, 2026)".
_PAREN_DUE_RE = re.compile(r"\(\s*(?:response\s+)?due\s+" + _DAY, re.IGNORECASE)
#: A granted extension of the time to respond: "Motion to extend the time to file
#: a response is granted and the time is extended to and including December 4,
#: 2026.", or the same for a brief in opposition. The request itself ("…
#: submitted to The Clerk.") moves nothing.
_EXTENDED_RE = re.compile(
    r"\btime\s+to\s+file\s+(?:a\s+|the\s+)?(?:response|brief\s+in\s+opposition)\b"
    r".*?\bextended\s+to\s+and\s+including\s+" + _DAY,
    re.IGNORECASE | re.DOTALL,
)
#: A Justice's call for a response to an application: "Response to application
#: (26A123) requested by Justice Kavanaugh, due by 4 p.m. (EST) on Friday,
#: January 10, 2026."
_APPLICATION_REQUEST_RE = re.compile(
    r"^\s*response\s+to\s+(?:the\s+)?application\b.*?\brequested\b.*?\bdue\b.*?" + _DAY,
    re.IGNORECASE | re.DOTALL,
)
#: The respondent's answer on file, with the respondent as the filer: "Brief of
#: respondent X in opposition filed.", "Memorandum of respondent United States
#: filed.", "Motion of appellee to dismiss or affirm filed.", and "Response to
#: application (26A123) from respondent X filed." A filing that only names the
#: respondent ("… to respondent's motion …", "… in support of respondent …") or
#: answers a motion rather than the petition is not the answer, and neither is an
#: extension request.
_RESPONSE_FILED_RE = re.compile(
    r"^\s*(?:"
    r"(?:brief|response|motion|memorandum)\s+(?:of|from)\s+(?:the\s+)?(?:federal\s+)?"
    r"(?:respondents?|appellees?)\b"
    r"|response\s+to\s+(?:the\s+)?application\b[^.]{0,80}?\bfrom\s+(?:the\s+)?"
    r"(?:respondents?|appellees?)\b"
    r")"
    r"(?!.*\b(?:in\s+support\s+of|extend\w*|extension)\b)"
    r".{0,300}?\bfiled\b",
    re.IGNORECASE,
)
#: "Waiver of right of respondent X to respond filed."
_WAIVER_RE = re.compile(r"^\s*waiver\b.{0,300}?\bto\s+respond\b", re.IGNORECASE)


def _day(text: str) -> date | None:
    """The calendar date ``text`` names ("November 3, 2026"), or ``None``."""
    try:
        return datetime.strptime(" ".join(text.replace(",", " ").split()), "%B %d %Y").date()
    except ValueError:
        return None


def argument_set_date(payload: Mapping[str, Any]) -> date | None:
    """The day the newest ``SET FOR ARGUMENT`` entry names, or ``None``.

    The last setting in docket order wins, so a rescheduled argument reads its
    new day. ``None`` when no entry sets the case for argument, and on a payload
    that discloses no proceedings, which the corpus column's fill-in latch then
    reads as "keep what is stored".
    """
    setting: date | None = None
    for text, _raw in proceedings_entries(payload):
        match = _SET_FOR_ARGUMENT_RE.search(text)
        if match is not None:
            setting = _day(match.group(1)) or setting
    return setting


def _stated_deadline(text: str) -> date | None:
    """The response deadline one entry states, or ``None``."""
    for pattern in (_APPLICATION_REQUEST_RE, _EXTENDED_RE, _PAREN_DUE_RE):
        match = pattern.search(text)
        if match is not None:
            return _day(match.group(1))
    return None


def response_deadline(
    payload: Mapping[str, Any],
) -> tuple[date | None, ResponseState | None]:
    """The newest stated response deadline, and whether the response is still owed.

    Returns ``(deadline, state)``. ``state`` is ``due`` while the newest
    deadline stands unanswered, ``filed`` once a respondent's response or brief
    in opposition follows it, and ``waived`` once a waiver does. ``(None,
    None)`` when no entry states a deadline, or the payload discloses no
    proceedings: nothing was read, so the corpus pair latch keeps the stored
    pair. A filing or waiver before any deadline was stated reads as that
    state with no date.
    """
    if not snapshot_carries_proceedings(payload):
        return None, None
    deadline: date | None = None
    state: ResponseState | None = None
    for text, _raw in proceedings_entries(payload):
        stated = _stated_deadline(text)
        if stated is not None:
            deadline, state = stated, "due"
        elif _WAIVER_RE.search(text):
            state = "waived"
        elif _RESPONSE_FILED_RE.search(text):
            state = "filed"
    return deadline, state
