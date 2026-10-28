"""run-repair's maintenance passes: what each one accepts, and the selector gate.

``run-repair.yml`` is one dispatch form over many passes, and every pass reads
the same five inputs differently: one takes a bound, another a parse label,
another a list of cells, most take no options. :data:`PASSES` is that table,
one entry per pass, and :func:`validate` is the credential-free refusal the
workflow's ``validate`` job runs before any writer job mints a token, assumes a
role or takes the corpus-write lock.

A field the pass does not take is refused rather than ignored: a number left
over from the previous dispatch is exactly how a bound meant for one pass
silently reaches another. Every refusal here that a step can reach is also
enforced in the step that acts on the input, which is the check of record; this
gate is the fail-fast copy. The two copies are kept word-for-word identical:
each refusal below is held as the step's own shell text, placeholder for
placeholder (``${REPAIR}``, ``${option}``), so
``tests/test_workflow_cell_invariants.py`` compares them directly and one
mistake never produces two differently worded refusals depending on where it
was caught.

**This file imports only the standard library, and the validate job runs it
by path** (``python3 -I -S src/fedcourtsai/repair_passes.py``) from a sparse
checkout holding this file alone, with the runner's own Python and no project
environment, so the gate in front of the writer credentials needs neither the
lockfile nor an install. ``tests/test_repair_passes.py`` refuses a non-stdlib
import, and pins the table against the dispatch form and the jobs' gates.
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass

#: The mode that writes; anything else is a dry run.
APPLY = "apply"

#: The dispatch form's initial state, which names no pass.
NO_PASS = "none"

#: A bound read off a dry-run ledger.
_BOUND = re.compile(r"[1-9][0-9]*")
#: A distribution parse label. Whether it is *registered* is the command's
#: refusal, not this one's: the registry lives in package code.
_PARSE_LABEL = re.compile(r"[a-z][a-z0-9-]*")
#: A two-digit October Term.
_TERM = re.compile(r"[0-9]{2}")
#: One re-grade subject, court/docket/event/run_id/actor. The grammar excludes
#: `.` deliberately: with no dots no field can be a `..` path segment.
REGRADE_CELL = re.compile(r"[a-z0-9-]+/[0-9]+/evt-[a-z0-9-]+/[0-9]{8}T[0-9]{6}Z/[a-z0-9-]+")

#: Separators the option list splits on: commas, spaces, tabs, line ends —
#: exactly the shell copy's, so a token one copy splits the other does too.
_OPTION_SEPARATORS = re.compile(r"[, \t\r\n]+")
#: Separators the cell list splits on: the same, less the comma.
_CELL_SEPARATORS = re.compile(r"[ \t\r\n]+")

# The refusals, in the shell copies' own words. A placeholder is the shell
# expansion the step prints in its place; `_render` fills it.
NO_PASS_NAMED = (
    "repair names no pass — pick one from the list. A dispatch left on the default "
    "asked for nothing."
)
UNKNOWN_PASS = (
    "unknown repair pass '${REPAIR}' — the selector and this validation have drifted "
    "apart; correct the workflow."
)
UNKNOWN_OPTION = (
    "repair=${REPAIR} does not accept the option '${option}' — it accepts: "
    "${accepted_options:-none}."
)
OPTION_LIST_REFUSED = "refusing the whole option list — correct the switches above and re-dispatch."
BOUND_NOT_TAKEN = (
    "repair=${REPAIR} takes no repair_bound — its blast radius is fixed in code, or "
    "it has none. Clear the field and re-dispatch."
)
TARGET_NOT_TAKEN = (
    "repair=${REPAIR} takes no repair_target — only the distribution re-derivation "
    "(a parse label), the re-grade (a cell list) and the application back-fill (a "
    "Term) name a subject. Clear the field and re-dispatch."
)
BOUND_NEEDED_ON_APPLY = (
    "repair=${REPAIR} with repair_mode=apply needs repair_bound set to a positive "
    "integer — the count read off a previous dry-run dispatch's ledger. Re-dispatch "
    "with that number."
)
BOUND_READ_IN_BOTH_MODES = (
    "repair=${REPAIR} reads repair_bound in BOTH modes, so it must be a positive "
    "integer wherever it is set — a bound its dry run would also spend. Clear the "
    "field or correct the number."
)
INCLUDE_SCORED_NEEDS_BOUND = (
    "the include-scored option needs repair_bound set to a positive integer — "
    "relabelling a graded cell takes on a re-grade backlog, so its size is stated "
    "up front in dry-run as much as in apply. Read the held-back lines off a plain "
    "dry-run dispatch's ledger."
)
PARSE_LABEL_NEEDED = (
    "repair=rederive-distribution-parse needs repair_target set to a distribution "
    "parse label — lowercase, e.g. dist-v2. A re-derivation names its reading rather "
    "than inheriting the ingest default, so there is no default to fall back on. "
    "Re-dispatch with the label."
)
TERM_NEEDED = (
    "repair=${REPAIR} needs repair_target set to a two-digit October Term, e.g. 24 — "
    "the back-fill reads one named Term per dispatch, so its ledger and the bound an "
    "apply carries answer for the same Term. Re-dispatch with the Term."
)
MALFORMED_CELL = (
    "malformed regrade cell (want court/docket/event/run_id/actor, e.g. "
    "scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge): ${line}"
)
CELL_LIST_REFUSED = "refusing the whole list — correct the lines above and re-dispatch."
NO_CELLS = "repair=regrade-stale names no cells — set repair_target."

#: Every refusal this gate can print, for the pairing test.
REFUSALS = frozenset(
    {
        NO_PASS_NAMED,
        UNKNOWN_PASS,
        UNKNOWN_OPTION,
        OPTION_LIST_REFUSED,
        BOUND_NOT_TAKEN,
        TARGET_NOT_TAKEN,
        BOUND_NEEDED_ON_APPLY,
        BOUND_READ_IN_BOTH_MODES,
        INCLUDE_SCORED_NEEDS_BOUND,
        PARSE_LABEL_NEEDED,
        TERM_NEEDED,
        MALFORMED_CELL,
        CELL_LIST_REFUSED,
        NO_CELLS,
    }
)

#: The two options that change what the gate itself requires or says.
INCLUDE_SCORED = "include-scored"
INCLUDE_FAILED_ATTEMPTS = "include-failed-attempts"

# The corpus passes' job, and the three jobs each credential-split pass runs:
# a projection, a credential-free parse, and the writer that lands its plan.
_CORPUS = ("repair",)
_HANDOFF = ("handoff-projection", "handoff-parse")


@dataclass(frozen=True)
class RepairPass:
    """What one pass reads from the dispatch form, and where it runs.

    ``bound_flag`` is the CLI flag ``repair_bound`` reaches, or empty for a pass
    that takes none. ``target_kind`` is how ``repair_target`` is read — a parse
    label, a cell list or a Term — or empty for a pass that names no subject.
    ``options`` is the pass's closed vocabulary for ``repair_options``.
    ``jobs`` are the workflow jobs a dispatch of the pass runs.
    """

    name: str
    jobs: tuple[str, ...]
    bound_flag: str = ""
    bound_required_on_apply: bool = False
    #: The pass's dry run also spends the bound, because it fetches per
    #: candidate, so the number must satisfy the grammar in both modes.
    bound_read_on_dry_run: bool = False
    target_kind: str = ""
    options: tuple[str, ...] = ()


def _bounded(
    name: str,
    flag: str,
    jobs: tuple[str, ...] = _CORPUS,
    *,
    bound_read_on_dry_run: bool = False,
    target_kind: str = "",
    options: tuple[str, ...] = (),
) -> RepairPass:
    """A pass whose apply carries the count its dry run's ledger reported."""
    return RepairPass(
        name=name,
        jobs=jobs,
        bound_flag=flag,
        bound_required_on_apply=True,
        bound_read_on_dry_run=bound_read_on_dry_run,
        target_kind=target_kind,
        options=options,
    )


#: Every pass the dispatch form offers, in its order.
PASSES: Mapping[str, RepairPass] = {
    p.name: p
    for p in (
        RepairPass("unlatch-overselected", _CORPUS),
        RepairPass("qp-backfill", _CORPUS),
        RepairPass("rederive-distribution-parse", _CORPUS, target_kind="parse"),
        _bounded("normalize-docket-markings", "--max-rewrites"),
        _bounded("response-backfill", "--max-fills"),
        _bounded("ocr-recovery", "--max-cases"),
        _bounded("document-backfill", "--max-cases", bound_read_on_dry_run=True),
        _bounded("recut", "--max-cases", bound_read_on_dry_run=True, options=("all-live",)),
        _bounded("arrival-backfill", "--max-fills"),
        _bounded("merits-phantom-removal", "--max-removals", options=(INCLUDE_FAILED_ATTEMPTS,)),
        _bounded("disposition-convergence", "--max-relabels", options=(INCLUDE_SCORED,)),
        _bounded("lost-outcomes", "--max-cases"),
        _bounded("event-definition-backfill", "--max-rewrites"),
        _bounded("amicus-rederive", "--max-changes"),
        _bounded("cert-amicus-rederive", "--max-changes"),
        RepairPass("regrade-stale", ("regrade",), target_kind="cells"),
        _bounded(
            "opinion-votes", "--max-stamps", (*_HANDOFF, "votes"), options=("replace-differing",)
        ),
        _bounded(
            "order-votes", "--max-stamps", (*_HANDOFF, "votes"), options=("replace-differing",)
        ),
        _bounded(
            "application-backfill", "--max-rows", (*_HANDOFF, "applications"), target_kind="term"
        ),
        _bounded("decision-record", "--max-fills", ("decision-record",)),
        _bounded("opinion-record", "--max-rows", (*_HANDOFF, "opinion-record")),
    )
}


@dataclass(frozen=True)
class Verdict:
    """The gate's answer: the lines it prints, and whether the dispatch stands."""

    accepted: bool
    errors: tuple[str, ...] = ()
    notices: tuple[str, ...] = ()


_PLACEHOLDER = re.compile(r"\$\{(REPAIR|option|accepted_options:-none|line)\}")


def _render(template: str, **values: str) -> str:
    """Fill a refusal's shell placeholders the way the shell would, in one pass.

    One pass, so a value that itself spells a placeholder is printed as typed.
    """
    filled = {
        "REPAIR": values.get("repair", ""),
        "option": values.get("option", ""),
        "accepted_options:-none": values.get("accepted") or "none",
        "line": values.get("line", ""),
    }
    return _PLACEHOLDER.sub(lambda match: filled[match.group(1)], template)


def _tokens(text: str, separators: re.Pattern[str]) -> list[str]:
    return [token for token in separators.split(text) if token]


def _field_refusal(
    selected: RepairPass, *, mode: str, bound: str, target: str, chosen: list[str]
) -> str:
    """The refusal of a bound or target the pass cannot take as given, or ''."""
    well_formed_bound = _BOUND.fullmatch(bound) is not None
    if not selected.bound_flag and bound:
        return BOUND_NOT_TAKEN
    if not selected.target_kind and target:
        return TARGET_NOT_TAKEN
    if selected.bound_required_on_apply and mode == APPLY and not well_formed_bound:
        return BOUND_NEEDED_ON_APPLY
    if selected.bound_read_on_dry_run and bound and not well_formed_bound:
        return BOUND_READ_IN_BOTH_MODES
    # The widened disposition sweep owes a re-grade per relabel, so its size is
    # stated in every mode. The widened phantom removal owes none, and its
    # removal set is already sized by the apply's own bound.
    if INCLUDE_SCORED in chosen and not well_formed_bound:
        return INCLUDE_SCORED_NEEDS_BOUND
    return ""


def _subject_refusals(selected: RepairPass, target: str) -> tuple[str, ...]:
    """The refusals of a target that does not name the pass's subject.

    Each grammar rejects the empty string, so a missing target is refused in
    the words of the pass that wanted it.
    """
    if selected.target_kind == "parse" and _PARSE_LABEL.fullmatch(target) is None:
        return (PARSE_LABEL_NEEDED,)
    if selected.target_kind == "term" and _TERM.fullmatch(target) is None:
        return (_render(TERM_NEEDED, repair=selected.name),)
    if selected.target_kind == "cells":
        cells = _tokens(target, _CELL_SEPARATORS)
        malformed = tuple(
            _render(MALFORMED_CELL, line=cell)
            for cell in cells
            if REGRADE_CELL.fullmatch(cell) is None
        )
        if malformed:
            return (*malformed, CELL_LIST_REFUSED)
        if not cells:
            return (NO_CELLS,)
    return ()


def validate(
    repair: str, *, mode: str, bound: str = "", target: str = "", options: str = ""
) -> Verdict:
    """Refuse anything the selected pass cannot legally run, in the shell's order.

    The first refusal ends the check, except that a malformed option or cell
    list names every bad token before the one refusal of the whole list.
    """
    if repair == NO_PASS:
        return Verdict(accepted=False, errors=(NO_PASS_NAMED,))
    selected = PASSES.get(repair)
    if selected is None:
        return Verdict(accepted=False, errors=(_render(UNKNOWN_PASS, repair=repair),))
    accepted_options = " ".join(selected.options)
    chosen = _tokens(options, _OPTION_SEPARATORS)
    unknown = tuple(
        _render(UNKNOWN_OPTION, repair=repair, option=token, accepted=accepted_options)
        for token in chosen
        if token not in selected.options
    )
    if unknown:
        return Verdict(accepted=False, errors=(*unknown, OPTION_LIST_REFUSED))
    refusal = _field_refusal(selected, mode=mode, bound=bound, target=target, chosen=chosen)
    if refusal:
        return Verdict(accepted=False, errors=(_render(refusal, repair=repair),))
    notices: list[str] = []
    if INCLUDE_FAILED_ATTEMPTS in chosen:
        notices.append(
            "include-failed-attempts: the removal will include phantoms whose only "
            "committed output is attempt.json cell-failure records."
        )
    subject = _subject_refusals(selected, target)
    if subject:
        return Verdict(accepted=False, errors=subject, notices=tuple(notices))
    notices.append(
        f"repair={repair} mode={mode} accepted; the step of record re-checks every refusal above."
    )
    return Verdict(accepted=True, notices=tuple(notices))


def main(environ: Mapping[str, str] | None = None) -> int:
    """Validate the dispatch named by the five ``REPAIR*`` variables.

    The inputs are maintainer-typed free text, so they arrive through the
    environment, never through a command line the workflow interpolates. Exit
    0 to proceed, 1 to refuse.
    """
    env = os.environ if environ is None else environ
    verdict = validate(
        env.get("REPAIR", ""),
        mode=env.get("REPAIR_MODE", ""),
        bound=env.get("REPAIR_BOUND", ""),
        target=env.get("REPAIR_TARGET", ""),
        options=env.get("REPAIR_OPTIONS", ""),
    )
    for notice in verdict.notices:
        print(notice)
    for error in verdict.errors:
        print(f"::error::{error}")
    return 0 if verdict.accepted else 1


if __name__ == "__main__":
    sys.exit(main())
