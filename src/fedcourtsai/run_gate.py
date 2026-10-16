"""The run gate: who may start a run of a gated workflow, or re-run one.

Every workflow that binds a deployment environment opens with an ``authorize``
job that runs this file, and every other job of the run needs that job. A
``workflow_dispatch`` proceeds only when its ``actor`` is a human
``config/dispatchers.json`` names, or a pipeline bot that file allows for the
workflow file being run; a re-run (``run_attempt`` above 1, whatever the event)
proceeds only when its ``triggering_actor`` is such a human, because no
pipeline bot re-runs anything. A first attempt of ``schedule``, ``push`` or
``pull_request`` is chosen by no person at run time and passes. Every other
event refuses, as does anything the gate cannot read: a blank actor on a
dispatch, an unparseable attempt, a missing or malformed allow-list.

Re-running *some* of a run's jobs does not re-run the authorize job: GitHub
keeps a succeeded job's result and outputs from the earlier attempt. So the
authorize job also publishes the attempt it judged and the listed humans
(:meth:`Dispatchers.rerunner_list`); every other job's condition admits it only
at that attempt or for a re-runner on that list, and a final ``run-gate`` job,
which needs every job and so re-runs on any partial re-run, fails the run when
neither holds. ``tests/test_workflow_auth_gate.py`` pins all three pieces.

**This file imports only the standard library, and the authorize job runs it
by path** (``python3 -I src/fedcourtsai/run_gate.py``) from a sparse checkout
holding this file and the allow-list alone, with the runner's own Python and
no project environment. The gate's whole behaviour is therefore this file plus
``config/dispatchers.json``, both owned by the maintainer, so no change to the
package, its dependencies or its lockfile — none of which are owned — can
loosen it on a branch an agent can merge to. Keep it that way: an import of
package code or a third-party library here would hand the gate to whatever
that import resolves to. ``tests/test_run_gate.py`` refuses one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: The allow-list, relative to the repository root the job runs from.
DISPATCHERS_PATH = "config/dispatchers.json"

#: The one event a person chooses to fire at run time.
DISPATCH_EVENT = "workflow_dispatch"

#: The events whose first attempt no person chooses: a cron, a push to a
#: branch, a pull request. Every other event that is not a dispatch refuses, so
#: a trigger added later is refused until this set names it.
UNCHOSEN_EVENTS = frozenset({"schedule", "push", "pull_request"})

# A GitHub user login: alphanumerics and single hyphens, at most 39 characters,
# never leading with a hyphen. Checked so a typo cannot widen the gate and so
# no login carries the comma the published re-runner list delimits on.
_HUMAN_LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
# An App's bot account: the App slug plus the literal ``[bot]`` suffix, which no
# user login can carry — so a bot entry can never name a person.
_BOT_LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\[bot\]")
# A workflow file name under ``.github/workflows/``, as each workflow passes it.
_WORKFLOW_FILE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.ya?ml")

_KEYS = frozenset({"humans", "bots"})


class DispatchersError(ValueError):
    """The allow-list is missing or malformed; the gate refuses on it."""


@dataclass(frozen=True)
class GateDecision:
    """Whether a run may proceed, with the line to log either way."""

    authorized: bool
    message: str


@dataclass(frozen=True)
class Dispatchers:
    """Who may start a run by hand or re-run one (``config/dispatchers.json``).

    ``humans`` may dispatch any gated workflow and re-run any run of one;
    ``bots`` maps a workflow file to the pipeline bot logins that may dispatch
    *that* workflow, and never re-run anything.
    """

    humans: tuple[str, ...]
    bots: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def is_human(self, login: str) -> bool:
        """Whether ``login`` is a listed human (GitHub logins are case-insensitive)."""
        folded = login.casefold()
        return any(human.casefold() == folded for human in self.humans)

    def is_dispatch_bot(self, login: str, workflow_file: str) -> bool:
        """Whether ``login`` is a bot this file allows to dispatch ``workflow_file``."""
        folded = login.casefold()
        return any(bot.casefold() == folded for bot in self.bots.get(workflow_file, ()))

    def rerunner_list(self) -> str:
        """The humans as one comma-delimited string, delimiters at both ends.

        The authorize job publishes it as an output, so a job re-run alone can
        test its own re-runner with ``contains(<list>, format(',{0},',
        github.triggering_actor))``. The outer commas make that an exact-login
        match (no login holds a comma), and an empty allow-list publishes the
        empty string, which contains no delimited login, rather than ``,,``.
        """
        return f",{','.join(self.humans)}," if self.humans else ""


def _refuse_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [key for key, _ in pairs]
    duplicated = sorted({key for key in keys if keys.count(key) > 1})
    if duplicated:
        raise DispatchersError(f"duplicate key(s) {duplicated}: a later entry would hide one")
    return dict(pairs)


def _logins(value: Any, where: str, pattern: re.Pattern[str], kind: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise DispatchersError(f"{where} must be a list of logins")
    for login in value:
        if not isinstance(login, str) or not pattern.fullmatch(login):
            raise DispatchersError(f"{where}: {login!r} is not {kind}")
    folded = [login.casefold() for login in value]
    if len(set(folded)) != len(folded):
        raise DispatchersError(f"{where} lists a login twice (logins compare case-insensitively)")
    return tuple(value)


def parse_dispatchers(text: str) -> Dispatchers:
    """Validate the allow-list's JSON text; raise :class:`DispatchersError` if malformed.

    A JSON object with a required ``humans`` list of user logins and an
    optional ``bots`` object mapping workflow file names to lists of
    ``<slug>[bot]`` logins. Unknown and duplicated keys are refused, so a
    misspelled or repeated section cannot read as an empty or a shadowed one.
    """
    try:
        data = json.loads(text, object_pairs_hook=_refuse_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise DispatchersError(f"not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise DispatchersError("must be a JSON object with a `humans` list")
    unknown = sorted(set(data) - _KEYS)
    if unknown:
        raise DispatchersError(f"unknown key(s) {unknown}")
    if "humans" not in data:
        raise DispatchersError("names no `humans` list")
    humans = _logins(data["humans"], "humans", _HUMAN_LOGIN, "a GitHub user login")
    raw_bots = data.get("bots", {})
    if not isinstance(raw_bots, dict):
        raise DispatchersError("`bots` must map workflow files to lists of bot logins")
    bots: dict[str, tuple[str, ...]] = {}
    for workflow, logins in raw_bots.items():
        if not _WORKFLOW_FILE.fullmatch(workflow):
            raise DispatchersError(f"bots: {workflow!r} is not a workflow file name")
        bots[workflow] = _logins(
            logins, f"bots.{workflow}", _BOT_LOGIN, "an App bot login (<slug>[bot])"
        )
    return Dispatchers(humans=humans, bots=bots)


def load_dispatchers(path: Path) -> Dispatchers:
    """Read and validate the allow-list at ``path``.

    There is no default: an allow-list that cannot be read must refuse every
    gated start, never admit one.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DispatchersError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except UnicodeDecodeError as exc:
        raise DispatchersError(f"{path} is not UTF-8") from exc
    try:
        return parse_dispatchers(text)
    except DispatchersError as exc:
        raise DispatchersError(f"{path}: {exc}") from exc


def _parse_attempt(run_attempt: str) -> int | None:
    text = run_attempt.strip()
    if not text.isascii() or not text.isdigit():
        return None
    attempt = int(text)
    return attempt if attempt >= 1 else None


def _dispatch_grant(actor: str, workflow_file: str, config: Dispatchers) -> tuple[bool, str]:
    """The dispatch rule: ``(allowed, reason-or-refusal)`` for a dispatch's actor."""
    if not actor.strip():
        return False, "a dispatch with no actor; refusing to run."
    if config.is_human(actor):
        return True, f"dispatched by {actor}, a listed dispatcher"
    if config.is_dispatch_bot(actor, workflow_file):
        return True, f"dispatched by {actor}, a pipeline bot allowed for {workflow_file}"
    return False, (
        f"{actor} may not dispatch {workflow_file}: not a human in "
        + f"{DISPATCHERS_PATH}, nor a bot it allows for this workflow; refusing to run."
    )


def _rerun_grant(triggering_actor: str, attempt: int, config: Dispatchers) -> tuple[bool, str]:
    """The re-run rule: ``(allowed, reason-or-refusal)`` for a re-run's starter."""
    if not triggering_actor.strip():
        return False, f"re-run attempt {attempt} names no triggering actor; refusing to run."
    if config.is_human(triggering_actor):
        return True, f"re-run (attempt {attempt}) by {triggering_actor}, a listed re-runner"
    return False, (
        f"{triggering_actor} may not re-run this run (attempt {attempt}): not a "
        + f"human in {DISPATCHERS_PATH}; refusing to run."
    )


def decide(
    *,
    event_name: str,
    actor: str,
    triggering_actor: str,
    run_attempt: str,
    workflow_file: str,
    config: Dispatchers,
) -> GateDecision:
    """Whether a run (or a re-run of one) may proceed past its authorize job.

    Pure decision over the GitHub context the authorize job passes in. Both
    rules apply cumulatively, so a re-run of a hand-started run needs a listed
    dispatcher *and* a listed re-runner:

    - a ``workflow_dispatch`` — at every attempt, since ``actor`` stays the
      dispatcher's across re-runs — needs ``actor`` among the humans, or among
      the bots allowed for ``workflow_file``;
    - any attempt above the first needs ``triggering_actor`` among the humans.

    A first attempt of an event in :data:`UNCHOSEN_EVENTS` passes; any other
    event refuses. A blank workflow file or needed login, or an attempt that is
    not a positive integer, refuses.
    """
    attempt = _parse_attempt(run_attempt)
    if attempt is None:
        return GateDecision(
            False, f"run attempt {run_attempt!r} is not a positive integer; refusing to run."
        )
    if not workflow_file.strip():
        return GateDecision(False, "the run names no workflow file; refusing to run.")
    if event_name != DISPATCH_EVENT and event_name not in UNCHOSEN_EVENTS:
        return GateDecision(
            False,
            f"event {event_name!r} is neither a dispatch nor one of "
            + f"{sorted(UNCHOSEN_EVENTS)}; refusing to run.",
        )
    grants: list[tuple[bool, str]] = []
    if event_name == DISPATCH_EVENT:
        grants.append(_dispatch_grant(actor, workflow_file, config))
    if attempt > 1:
        grants.append(_rerun_grant(triggering_actor, attempt, config))
    for allowed, text in grants:
        if not allowed:
            return GateDecision(False, text)
    reasons = [text for _, text in grants] or [
        f"{event_name} first attempt, chosen by no person at run time"
    ]
    return GateDecision(True, f"Authorized {workflow_file}: " + "; ".join(reasons) + ".")


def main(argv: Sequence[str] | None = None) -> int:
    """Gate a run on who started it; exit 0 to proceed, 1 to refuse.

    Prints the authorization line on success and appends ``attempt`` and
    ``rerunners`` to ``--github-output``; prints the refusal as an
    ``::error::`` annotation otherwise. A usage error exits 2, which refuses
    too. No token and no network: the inputs are the run's own context.
    """
    parser = argparse.ArgumentParser(
        prog="run_gate.py", description="Gate a run on who started it (fail closed)."
    )
    parser.add_argument("--workflow", required=True, help="The workflow's file name.")
    parser.add_argument("--event-name", required=True, help="github.event_name.")
    parser.add_argument("--actor", required=True, help="github.actor.")
    parser.add_argument("--triggering-actor", required=True, help="github.triggering_actor.")
    parser.add_argument("--run-attempt", required=True, help="github.run_attempt.")
    parser.add_argument("--config", default=DISPATCHERS_PATH, help="The allow-list's path.")
    parser.add_argument("--github-output", help="Where to append the job outputs.")
    args = parser.parse_args(argv)
    try:
        config = load_dispatchers(Path(args.config))
    except DispatchersError as exc:
        print(f"::error::{exc}; refusing to run.", file=sys.stderr)
        return 1
    decision = decide(
        event_name=args.event_name,
        actor=args.actor,
        triggering_actor=args.triggering_actor,
        run_attempt=args.run_attempt,
        workflow_file=args.workflow,
        config=config,
    )
    if not decision.authorized:
        print(f"::error::{decision.message}", file=sys.stderr)
        return 1
    print(decision.message)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as out:
            out.write(f"attempt={args.run_attempt.strip()}\n")
            out.write(f"rerunners={config.rerunner_list()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
