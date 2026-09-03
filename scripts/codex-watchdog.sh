#!/usr/bin/env bash
# Runner-level deadline for a codex cell step (run-predict.yml / run-evaluate.yml).
#
# A wedged `codex exec` has outlasted the engine step's own `timeout-minutes`:
# the step stayed `in_progress` until the *job* cap cancelled the runner. A
# cancelled job runs none of the capture tail and GitHub drops its logs, so the
# hang erases its own evidence and spends the whole job budget. The pinned
# codex-action exposes no timeout input of its own, so the bound lives out
# here: capture what the runner knows, then kill the engine, which fails the
# *step* — the same shape as a max-turns stop, which the tail already salvages.
#
# The arm step launches this detached and the disarm step kills it, so it can
# only ever fire while the engine step is still running.
#
# Configuration, all from the arm step's env:
#   WATCHDOG_DEADLINE_S  seconds to wait before firing (the call site does the
#                        arithmetic against the job cap and states it there)
#   WATCHDOG_DIR         where the diagnostics bundle and the marker are written
#   CODEX_HOME           the cell's codex home, listed by name and size only
#   WATCHDOG_MATCH       process-match overrides for the engine and for the
#   WATCHDOG_RUNNER_MATCH  action's own step process; the defaults name the
#                        pinned action's invocation
#   WATCHDOG_POLL_S      granularity of the deadline wait and of the kill
#                        escalation that follows it
#
# The workflows set only the first three and leave the overrides at their
# defaults; the overrides exist so a test can drive this against processes of
# its own, on its own clock, rather than against a pattern naming a real engine.
#
# The bundle is published: it rides the cell artifact, which is downloadable by
# anyone with a GitHub account for its retention window. So it holds shapes and
# metadata, never content — this runner user's process arguments, socket table
# and kernel state, and a name-and-size listing of the codex home. No process's
# environment is ever read; the session rollout is deliberately NOT copied,
# since it carries retrieved documents verbatim (the disarm step distils its
# item *shapes* instead, with the tested `codex-item-shapes` command that
# exists for exactly that reason); and the sidecar logs are left alone, because
# converting the hang into a step failure is itself what makes the cell's own
# sidecar-log step run and put them in a job log that now survives.

# Not `-e`: a best-effort capture must never skip the kill that follows it.
set -uo pipefail

deadline_s="${WATCHDOG_DEADLINE_S:?WATCHDOG_DEADLINE_S is required}"
dir="${WATCHDOG_DIR:?WATCHDOG_DIR is required}"
codex_home="${CODEX_HOME:-}"
# The action runs `<resolved path>/codex exec --skip-git-repo-check --cd ...`.
# Anchored on the binary, and matching the flag as well as the subcommand, so
# the pattern names that invocation and nothing else on the runner: a predictor
# id is itself spelled with "codex", the cell's tooling carries that id in its
# arguments, and an unanchored pattern would also match any process whose
# command line merely quotes it — this script's own launcher included.
match="${WATCHDOG_MATCH:-(^|/)codex exec --skip-git-repo-check}"
# The action's own step process: `node ... dist/main.js run-codex-exec ...`.
runner_match="${WATCHDOG_RUNNER_MATCH:-dist/main\.js run-codex-exec}"
poll_s="${WATCHDOG_POLL_S:-10}"

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(stamp)] watchdog: $*"; }

# A killed process that its parent has not reaped yet still answers `kill -0`,
# and waiting out a zombie is waiting out nothing — so read the state instead.
alive() {
  local pid state
  for pid in "$@"; do
    if [ -r "/proc/${pid}/stat" ]; then
      state="$(</proc/"${pid}"/stat)"
      state="${state##*) }"
      if [ "${state%% *}" != "Z" ]; then
        return 0
      fi
    elif kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  done
  return 1
}

# The bundle a maintainer reads afterwards: argv, kernel state and file names,
# never any process's environment and never a rollout's contents.
capture_runner_state() {
  # This runner user's processes only: the engine, the action's node runner and
  # both sidecars are all of them, and a whole-machine dump would put argv this
  # repo does not control into a public artifact.
  ps -ww -u "$uid" -o pid,ppid,stat,wchan:32,etime,args --forest >"$dir/process-tree.txt" 2>&1
  # Sockets separate a stalled call from a spinning loop.
  ss -tanp >"$dir/sockets.txt" 2>&1
  if [ -n "$codex_home" ] && [ -d "$codex_home" ]; then
    # Names, sizes and times only — the codex home holds the action's
    # model-proxy config, its server-info file, and the session rollout, and
    # none of their contents belong in a published bundle.
    ls -lR "$codex_home" >"$dir/codex-home-listing.txt" 2>&1
  fi
}

# End the step itself. The step shell `exec`s into the action's node runner, so
# killing that is what turns a hang into a step failure — and it is the only
# lever left when the engine pattern matched nothing.
kill_action_runner() {
  local runners
  mapfile -t runners < <(pgrep -u "$uid" -f -- "$runner_match")
  if [ "${#runners[@]}" -gt 0 ] && alive "${runners[@]}"; then
    log "killing the action's runner (pids: ${runners[*]}) to end the step"
    kill -KILL "${runners[@]}" 2>/dev/null
  fi
}

mkdir -p "$dir"
uid="$(id -u)"

log "armed; firing in ${deadline_s}s unless disarmed"
elapsed=0
while [ "$elapsed" -lt "$deadline_s" ]; do
  sleep "$poll_s"
  elapsed=$((elapsed + poll_s))
done

# `-u` narrows to this runner user: the engine's root-owned sudo wrapper
# carries the same arguments and could not be signalled from here anyway.
mapfile -t pids < <(pgrep -u "$uid" -f -- "$match")
if [ "${#pids[@]}" -eq 0 ]; then
  # The deadline is only reached while the engine step is still running, so
  # matching nothing means the pattern no longer names the engine — or the
  # wedge is in one of the step's earlier composite phases (the two npm
  # installs, the proxy start). Record that with the process tree as the
  # evidence, then still try to end the step: killing the action's runner
  # reaches a wedged engine phase whatever its argv now looks like, while a
  # wedge in a phase that runs before it stays out of reach, and the captured
  # tree is what names it.
  log "deadline reached but no process matches the engine; recording and ending the step"
  capture_runner_state
  {
    echo "stood_down_at=$(stamp)"
    echo "deadline_s=${deadline_s}"
    echo "match=${match}"
  } >"$dir/STOOD_DOWN"
  kill_action_runner
  exit 0
fi

log "deadline reached with the engine still running (pids: ${pids[*]})"
capture_runner_state
for pid in "${pids[@]}"; do
  {
    echo "## pid ${pid}"
    tr '\0' ' ' <"/proc/${pid}/cmdline"
    echo
    echo "wchan: $(cat "/proc/${pid}/wchan" 2>/dev/null)"
    cat "/proc/${pid}/status" 2>/dev/null
    echo
  } >>"$dir/engine-proc.txt" 2>&1
done
{
  echo "fired_at=$(stamp)"
  echo "deadline_s=${deadline_s}"
  echo "pids=${pids[*]}"
} >"$dir/FIRED"

log "diagnostics captured to ${dir}; terminating the engine"
kill -TERM "${pids[@]}" 2>/dev/null
waited=0
while [ "$waited" -lt 30 ] && alive "${pids[@]}"; do
  sleep "$poll_s"
  waited=$((waited + poll_s))
done
if alive "${pids[@]}"; then
  log "SIGTERM did not land; escalating to SIGKILL"
  kill -KILL "${pids[@]}" 2>/dev/null
fi

# A dead engine normally brings the action's runner down within seconds; if it
# does not, kill that too — a step that never ends is the whole failure this
# guards against.
sleep "$poll_s"
kill_action_runner

log "fired; the engine step should now fail and leave the capture tail to run"
