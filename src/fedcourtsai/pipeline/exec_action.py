"""Executive-action scope annotations for analytics: does an application test a federal policy?

Read-side only and deliberately not a prediction input, like the party and
counsel annotations it composes (:mod:`.party`, :mod:`.counsel`): every value is
a pure function of a corpus row's caption and stored counsel entries, its latest
live-shaped snapshot where the rule reads one, and a date the caller supplies,
so a cut re-derives from a corpus pointer with no stored column, no writer lane
and no model spend. The one consumer is the executive
success cut (:mod:`.executive_success`).

**Why the federal class is not the scope.** The ``federal`` class of
``party-v2`` is the federal government broadly: the United States, agencies,
officers and United States courts. An emergency-docket question about how the
Court treats *executive action* needs a narrower population. A criminal
defendant's stay application against the United States sits in the federal
class and challenges no executive policy; a mandamus petition against a
district court names a court the executive does not speak for; and an
individual's own removal or benefits case contests one decision about one
person, not a general policy. This rule narrows the class to the applications
that challenge or defend a general federal executive action, and names why
every row it leaves out was left out.

**What the rule reads, in order.**

1. **Which side the government is on.** The government is the applicant where
   the caption's petitioner half reads federal (``party-v2``) or the Solicitor
   General's office is counsel for the applicant (``sg-office-v1``); either
   suffices, because the office files every executive application while the
   caption convention for an officer sometimes reads private. It is the
   respondent where either reads federal on the respondent side instead. A
   row with neither is ``no-federal-party``.
2. **A government applicant is in scope** (``gov-applicant``), unnarrowed by
   the caption:
   the office files for the executive, and the caption's federal petitioner is
   an agency or officer acting for it. The rule does not set aside a
   government application in a criminal or individual case, which the
   respondent side's narrowing would; on the emergency docket such
   applications are rare, and ``review_rows`` lists every one.
3. **A government respondent is narrowed by who the opposing side is.** A
   respondent caption naming a United States court or judge is
   ``federal-court``, and one naming a federal custodian (a marshal, pretrial
   services, the Bureau of Prisons, a warden) is ``federal-prosecution``. A
   respondent that is the United States itself is a
   prosecution or a suit against the sovereign as such, ``federal-prosecution``,
   unless a state is the applicant — a state suing or sued by the United States
   is a federal-state dispute over executive enforcement, so it reads
   ``challenge-to-executive-action``. Against an agency or officer, an
   applicant that is a state or an organization is
   ``challenge-to-executive-action``; a single named individual is
   ``individual-claim``, out of scope (the organization words are a word
   list, so a surname that is also one, such as Church, reads as an
   organization; ``review_rows`` is where a reader catches it); a named
   individual with ``et al.`` is ``individual-group``, which may be a class
   challenge to a policy or several people's own cases and is left
   ``unknown`` for review. A row where only the
   counsel entries, not the caption, put the government on the respondent side
   takes the court and custodian checks and is otherwise
   ``sg-respondent-only``, also ``unknown``: the office answers for federal
   officers the caption reads as private, but it also files in private
   disputes.

4. **A procedural request is out of scope** (``procedural-request``), under
   ``exec-action-v2``. An application whose only ask is leave to file a brief
   or petition over the word or page limit decides nothing about the policy:
   the order granting it is a win for no one. The ask parser leaves it
   ``unknown``, so the caption steps above would count it like any other, and
   a granted one would read as the filer's win. The rule reads the
   application's own submission entry from its snapshot
   (:func:`.interim_signals.is_overlength_request`) for every row the caption
   steps leave in scope or unknown whose stored ask is not substantive, so the
   count stays visible under its own reason; a row the caption already sets
   out of scope keeps that reason. A row with no snapshot keeps its caption
   reason, so a cut that reads no snapshot gives v1's reasons under v2's
   label.

5. **A committed hand reading wins where it exists** (``hand-in-scope``,
   ``hand-out-of-scope``, ``hand-unclear``), under ``exec-action-v3``. The
   caption cannot tell a federal suit against a state law from one enforcing
   an agency's rule, a bankruptcy trustee from the executive, or a government
   named on the wrong side of a caption, and two AI raters reading the docket
   can. Their adjudicated codes are committed as the package's
   ``exec_action_hand.json``, one row per application with its scope, the
   government's side where it has one, and the code's ``basis``: both raters
   agreed (``raters-agreed``), the authoring session settled a disagreement
   (``adjudicated``), it overrode both raters on one of three stated points
   (``override``: a government application defending a policy, through
   mandamus or the federal execution schedule, is in scope; an individual
   prisoner's execution application is out), or the row is a request to file
   over the word or page limit (``procedural``, out). For a listed row the
   hand scope replaces steps 1 to 4, and its side replaces the caption's where
   the code names one; every other row reads as under ``exec-action-v2``.

   **What a hand code is.** The raters were blind to each other but not to
   the outcome (the docket entries carry the orders), and the adjudication
   was made with a published tally's figures in view, so a hand code is a
   reading of the record, not a measurement of the rule, and a cut under this
   version is not an independent replication of that tally. The codes cover
   the applications filed from 2017-01-20 through 2026-10-12 that the scope
   check's rating rounds coded: federal-side applications, the rule's
   in-scope and unknown rows, out-of-scope rows naming a federal agency or
   officer, and a seeded sample of the others; a later application reads by the rule until a code
   lists it, and adding one under the same rules keeps the label.

``unknown`` is a result, never an error: the rule cannot tell those rows apart
from the caption, and a reader counts them beside the in-scope population
rather than guessing which way they go.

**Versioned like the party and counsel rules, and for the same reason.**
``exec-action-v1`` is steps 1 to 3 over ``party-v2`` and ``sg-office-v1``;
``exec-action-v2`` adds step 4; ``exec-action-v3`` adds step 5.
:data:`EXEC_ACTION_RULES` registers each under
its label, and a change to what any reason means, or to the rules it composes,
is a new label beside them.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from functools import cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any, Final, Literal, cast

from .. import corpus
from .caption import petitioner_caption
from .counsel import SG_OFFICE_RULE_VERSION, counsel_rule
from .ingest import application_entry_texts
from .interim_signals import ApplicationKind, is_overlength_request
from .party import PARTY_RULE_VERSION_V2, party_rule, respondent_caption

#: Which side of an application the federal government is on.
GovernmentSide = Literal["applicant", "respondent"]

#: Why a row is in or out of scope. Reporting order: in scope first, then
#: unknown, then out of scope.
ScopeReason = Literal[
    "gov-applicant",
    "challenge-to-executive-action",
    "individual-group",
    "sg-respondent-only",
    "federal-prosecution",
    "federal-court",
    "individual-claim",
    "procedural-request",
    "no-federal-party",
    "hand-in-scope",
    "hand-unclear",
    "hand-out-of-scope",
]

SCOPE_REASONS: Final[tuple[ScopeReason, ...]] = (
    "gov-applicant",
    "challenge-to-executive-action",
    "individual-group",
    "sg-respondent-only",
    "federal-prosecution",
    "federal-court",
    "individual-claim",
    "procedural-request",
    "no-federal-party",
    "hand-in-scope",
    "hand-unclear",
    "hand-out-of-scope",
)

#: The scope each reason implies: ``True`` in scope, ``False`` out, ``None`` unknown.
REASON_SCOPE: Final[Mapping[ScopeReason, bool | None]] = MappingProxyType(
    {
        "gov-applicant": True,
        "challenge-to-executive-action": True,
        "individual-group": None,
        "sg-respondent-only": None,
        "federal-prosecution": False,
        "federal-court": False,
        "individual-claim": False,
        "procedural-request": False,
        "no-federal-party": False,
        "hand-in-scope": True,
        "hand-unclear": None,
        "hand-out-of-scope": False,
    }
)

#: The caption-only rule (steps 1 to 3), and the rule that also sets aside a
#: procedural request (step 4), which the cut defaults to.
EXEC_ACTION_RULE_VERSION_V1: Final[str] = "exec-action-v1"
EXEC_ACTION_RULE_VERSION: Final[str] = "exec-action-v2"
#: The rule that also applies the committed hand reading (step 5).
EXEC_ACTION_RULE_VERSION_V3: Final[str] = "exec-action-v3"

#: The committed hand reading step 5 applies, at the package root.
EXEC_ACTION_HAND_RESOURCE: Final[str] = "exec_action_hand.json"

#: How a hand code came to be, as the reference records it.
HandBasis = Literal["raters-agreed", "adjudicated", "override", "procedural"]
_HAND_BASES: Final[frozenset[str]] = frozenset(
    {"raters-agreed", "adjudicated", "override", "procedural"}
)
_HAND_SCOPES: Final[Mapping[str, ScopeReason]] = MappingProxyType(
    {"in": "hand-in-scope", "out": "hand-out-of-scope", "unclear": "hand-unclear"}
)


@dataclass(frozen=True)
class HandCode:
    """One application's committed hand reading."""

    reason: ScopeReason
    government_side: GovernmentSide | None
    basis: HandBasis


def _refuse_repeated_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object, refusing a key the document repeats verbatim."""
    built: dict[str, object] = {}
    for key, value in pairs:
        if key in built:
            raise ValueError(f"the hand reading lists {key.strip().upper()} twice")
        built[key] = value
    return built


def parse_hand_codes(text: str) -> Mapping[str, HandCode]:
    """Parse a hand-reading document, keyed by normalized docket number.

    Refuses an unknown version, a docket listed twice in any spelling, an
    unknown scope, side or basis, and an in-scope code with no side.
    """
    document = json.loads(text, object_pairs_hook=_refuse_repeated_keys)
    if not isinstance(document, dict) or not isinstance(document.get("rows"), dict):
        raise ValueError("the hand reading is an object with a rows object")
    if document.get("rule_version") != EXEC_ACTION_RULE_VERSION_V3:
        raise ValueError(
            f"the hand reading is {document.get('rule_version')!r}, "
            f"not {EXEC_ACTION_RULE_VERSION_V3!r}"
        )
    codes: dict[str, HandCode] = {}
    for docket, entry in document["rows"].items():
        spelled = docket.strip().upper()
        if spelled in codes:
            raise ValueError(f"the hand reading lists {spelled} twice")
        if not isinstance(entry, dict) or not set(entry) <= {"scope", "government_side", "basis"}:
            raise ValueError(f"{docket}: a code holds scope, government_side and basis")
        scope, side, basis = entry.get("scope"), entry.get("government_side"), entry.get("basis")
        if not isinstance(scope, str) or scope not in _HAND_SCOPES:
            raise ValueError(f"{docket}: unknown scope {scope!r}")
        if side not in (None, "applicant", "respondent"):
            raise ValueError(f"{docket}: unknown government side {side!r}")
        if not isinstance(basis, str) or basis not in _HAND_BASES:
            raise ValueError(f"{docket}: unknown basis {basis!r}")
        if scope == "in" and side is None:
            raise ValueError(f"{docket}: an in-scope code names the government's side")
        codes[spelled] = HandCode(
            reason=_HAND_SCOPES[scope],
            government_side=cast("GovernmentSide | None", side),
            basis=cast(HandBasis, basis),
        )
    return MappingProxyType(codes)


@cache
def hand_codes() -> Mapping[str, HandCode]:
    """The committed hand reading, keyed by normalized docket number."""
    resource = files("fedcourtsai").joinpath(EXEC_ACTION_HAND_RESOURCE)
    return parse_hand_codes(resource.read_text(encoding="utf-8"))


#: The rules both versions compose.
EXEC_ACTION_PARTY_RULE: Final[str] = PARTY_RULE_VERSION_V2
EXEC_ACTION_COUNSEL_RULE: Final[str] = SG_OFFICE_RULE_VERSION

#: A respondent half that is the United States itself, alone or with others.
_UNITED_STATES_RE: Final = re.compile(
    r"^\s*(?:the\s+)?United\s+States(?:\s+of\s+America)?\s*(?:,?\s*et\s+al\.?)?\s*,?\s*$",
    re.IGNORECASE,
)

#: A respondent half naming a federal court or a federal judge by title.
_FEDERAL_COURT_RE: Final = re.compile(
    r"\bUnited\s+States\s+(?:District\s+|Bankruptcy\s+|Tax\s+)?Court\b"
    r"|\bCourt\s+of\s+(?:Appeals|Federal\s+Claims)\b"
    r"|\bU\.\s?S\.\s+District\s+Court\b"
    r"|\bUnited\s+States\s+(?:District|Circuit|Magistrate|Bankruptcy)\s+Judge\b"
    r"|\bJudge,\s+United\s+States\b",
    re.IGNORECASE,
)

#: A respondent half naming a federal custodian: the marshals, pretrial services,
#: the Bureau of Prisons, a warden. A stay against one is a criminal or custody
#: matter, read with the prosecutions.
_CUSTODY_RE: Final = re.compile(
    r"\bMarshal\b|\bPretrial\s+Services\b|\bBureau\s+of\s+Prisons\b|\bWarden\b",
    re.IGNORECASE,
)

#: Words that mark an applicant as an organization rather than a person.
_ORGANIZATION_RE: Final = re.compile(
    r"\b(?:Inc|Incorporated|LLC|L\.L\.C|LLP|LP|L\.P|Ltd|Corp|Corporation|Co|Company"
    r"|Association|Ass'n|Assn|Council|Coalition|Union|Committee|Foundation|Institute"
    r"|Cooperative|Authority|Tribe|Band|Nation|Party|Group|Alliance|Federation"
    r"|Chamber|Center|Centre|Society|Trust|Church|University|College|Board|League"
    r"|Organization|Network|Fund|Project|Services|Industries|Holdings|Partners"
    r"|Enterprises|Agency|District|City|County|Town|Township|Village|Borough"
    r"|Commonwealth|Department|Commission|Hospital|Clinic|Bank|Club|Federal)\b\.?",
    re.IGNORECASE,
)

_ET_AL_RE: Final = re.compile(r"\bet\.?\s*al\b", re.IGNORECASE)


@dataclass(frozen=True)
class ExecActionAnnotation:
    """One row's scope annotation under one rule version, self-describing."""

    rule_version: str
    in_scope: bool | None
    reason: ScopeReason
    government_side: GovernmentSide | None


def _applicant_kind(text: str, petitioner_is_state: bool) -> ScopeReason:
    """Read a challenger's caption half: organization, state, or individual(s)."""
    if petitioner_is_state or _ORGANIZATION_RE.search(text):
        return "challenge-to-executive-action"
    if _ET_AL_RE.search(text):
        return "individual-group"
    return "individual-claim"


#: A row's latest live-shaped snapshot payload, or ``None`` where it has none.
Payload = Mapping[str, Any] | None


def exec_action_annotations(
    row: corpus.CorpusRow, as_of: date | None, payload: Payload = None
) -> ExecActionAnnotation:
    """The ``exec-action-v1`` annotation of ``row``: steps 1 to 3 of the module docstring.

    ``as_of`` is passed through to the party rule, which stamps it; scope does
    not depend on it. Counsel is read without a moment, as the stored list
    stands. ``payload`` is not read: this version reads the caption alone.
    """
    return _caption_annotation(row, as_of, EXEC_ACTION_RULE_VERSION_V1)


def exec_action_annotations_v2(
    row: corpus.CorpusRow, as_of: date | None, payload: Payload = None
) -> ExecActionAnnotation:
    """The ``exec-action-v2`` annotation of ``row``: steps 1 to 4 of the module docstring.

    Step 4 reads ``payload``, the row's latest live-shaped snapshot, and only
    where the caption steps leave the row in scope or unknown and the stored
    ask is not substantive; without one the caption reason stands.
    """
    annotation = _caption_annotation(row, as_of, EXEC_ACTION_RULE_VERSION)
    if (
        annotation.government_side is None
        or annotation.in_scope is False
        or row.application_kind == ApplicationKind.substantive.value
        or payload is None
        or not is_overlength_request(application_entry_texts(payload))
    ):
        return annotation
    return ExecActionAnnotation(
        rule_version=EXEC_ACTION_RULE_VERSION,
        in_scope=REASON_SCOPE["procedural-request"],
        reason="procedural-request",
        government_side=annotation.government_side,
    )


def exec_action_annotations_v3(
    row: corpus.CorpusRow, as_of: date | None, payload: Payload = None
) -> ExecActionAnnotation:
    """The ``exec-action-v3`` annotation of ``row``: step 5 over ``exec-action-v2``.

    A row the committed hand reading lists takes its hand scope, and its hand
    side where the code names one; any other row reads as under v2.
    """
    rule = exec_action_annotations_v2(row, as_of, payload)
    code = hand_codes().get((row.docket_number or "").strip().upper())
    if code is None:
        return ExecActionAnnotation(
            rule_version=EXEC_ACTION_RULE_VERSION_V3,
            in_scope=rule.in_scope,
            reason=rule.reason,
            government_side=rule.government_side,
        )
    return ExecActionAnnotation(
        rule_version=EXEC_ACTION_RULE_VERSION_V3,
        in_scope=REASON_SCOPE[code.reason],
        reason=code.reason,
        government_side=code.government_side or rule.government_side,
    )


def _caption_annotation(
    row: corpus.CorpusRow, as_of: date | None, rule_version: str
) -> ExecActionAnnotation:
    """Steps 1 to 3: the caption and counsel reading both versions share."""
    party = party_rule(EXEC_ACTION_PARTY_RULE)(row, as_of)
    counsel = counsel_rule(EXEC_ACTION_COUNSEL_RULE)(row, None).side
    caption_applicant = party.federal_party in ("petitioner", "both")
    caption_respondent = party.federal_party == "respondent"
    side: GovernmentSide | None
    if caption_applicant or counsel in ("petitioner", "both"):
        side = "applicant"
        reason: ScopeReason = "gov-applicant"
    elif caption_respondent or counsel == "respondent":
        side = "respondent"
        respondent = respondent_caption(row) or ""
        petitioner_is_state = party.petitioner_class == "state"
        if _FEDERAL_COURT_RE.search(respondent):
            reason = "federal-court"
        elif _CUSTODY_RE.search(respondent):
            reason = "federal-prosecution"
        elif not caption_respondent:
            reason = "sg-respondent-only"
        elif _UNITED_STATES_RE.match(respondent):
            reason = (
                "challenge-to-executive-action" if petitioner_is_state else "federal-prosecution"
            )
        else:
            reason = _applicant_kind(petitioner_caption(row), petitioner_is_state)
    else:
        side = None
        reason = "no-federal-party"
    return ExecActionAnnotation(
        rule_version=rule_version,
        in_scope=REASON_SCOPE[reason],
        reason=reason,
        government_side=side,
    )


#: A scope annotator: a row, the cut's date for it, and its snapshot where read.
Annotator = Callable[[corpus.CorpusRow, date | None, Payload], ExecActionAnnotation]

#: The registered scope rules, by version.
EXEC_ACTION_RULES: Final[Mapping[str, Annotator]] = MappingProxyType(
    {
        EXEC_ACTION_RULE_VERSION_V1: exec_action_annotations,
        EXEC_ACTION_RULE_VERSION: exec_action_annotations_v2,
        EXEC_ACTION_RULE_VERSION_V3: exec_action_annotations_v3,
    }
)


def exec_action_rule(rule_version: str) -> Annotator:
    """The registered scope annotator for ``rule_version``; :class:`KeyError` if none."""
    return EXEC_ACTION_RULES[rule_version]
