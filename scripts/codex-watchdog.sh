#!/usr/bin/env bash
# Runner-level deadline for a codex cell step (run-predict.yml / run-evaluate.yml).
#
# A wedged codex cell has outlasted the engine step's own `timeout-minutes`:
# the step stayed `in_progress` until the *job* cap cancelled the runner. A
# cancelled job runs none of the capture tail and GitHub drops its logs, so the
# hang erases its own evidence and spends the whole job budget. The pinned
# codex-action exposes no timeout input of its own, so the bound lives out
# here, in three beats at the deadline:
#
#   1. capture what the runner knows, first, so the evidence exists whatever
#      the kills then do;
#   2. end the engine, narrowly, by the pattern that names its invocation;
#   3. after a short grace, end the *step's own process tree* if the step is
#      still running — or immediately if no engine ever matched.
#
# Beat 3 is what actually converts the hang into a step failure. Killing the
# engine only concludes the step when the wedge is in the engine: a wedge in
# the action's node wrapper, or in a phase that runs before the engine spawns,
# leaves the wrapper waiting on nothing with the step still `in_progress`. A
# failed step is the same shape as a max-turns stop, which the tail already
# salvages.
#
# The arm step launches this detached and the disarm step kills it, so it can
# only ever fire while the engine step is still running.
#
# Configuration, all from the arm step's env:
#   WATCHDOG_DEADLINE_S  seconds to wait before firing (the call site does the
#                        arithmetic against the job cap and states it there)
#   WATCHDOG_DIR         where the diagnostics bundle and the marker are written
#   CODEX_HOME           the cell's codex home, listed by name and size only
#   WATCHDOG_MATCH       process-match overrides: the engine's invocation, the
#   WATCHDOG_RUNNER_MATCH  action's own entry argv, the runner's per-job worker
#   WATCHDOG_WORKER_MATCH  process (read as an anchor, never signalled), and
#   WATCHDOG_INFRA_MATCH   the infrastructure that must never be signalled
#   WATCHDOG_POLL_S      granularity of the deadline wait and of the kill
#                        escalation that follows it
#   WATCHDOG_STEP_GRACE_S  how long anything signalled here has to answer:
#                        the engine to a SIGTERM, then the step to the engine's
#                        death, then the step's tree to its own SIGTERM. Those
#                        run in sequence, so the deadline plus three of these is
#                        what has to stay inside the step's own timeout
#   WATCHDOG_ARM_SLACK_S  how far before this watchdog a process may have
#                        started and still be the step it guards
#   WATCHDOG_MIN_STEP_AGE_S  how long a process must already have been running
#                        to be the step this watchdog was armed for
#
# The workflows set only the first three and leave the overrides at their
# defaults; the overrides exist so a test can drive this against processes of
# its own, on its own clock, rather than against a pattern naming a real engine
# or the runner that is executing the test.
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
# One of the two routes to the step, and the weaker one — it is a claim about
# the pinned action's internal argv, which a version bump can change without
# any signal here. Parentage is the route that does not depend on it.
runner_match="${WATCHDOG_RUNNER_MATCH:-dist/main\.js run-codex-exec}"
# The runner starts each step as a child of its per-job worker process, and one
# job runs one step at a time, so the worker's live children under this user
# are that step. Read as an anchor only: worker pids are excluded from every
# candidate set below.
worker_match="${WATCHDOG_WORKER_MATCH:-Runner\.Worker}"
# The refusal list. Signalling the runner's own infrastructure force-kills the
# whole job, which is precisely the outcome this script exists to prevent, so
# no candidate that names it is ever signalled however it was discovered.
infra_match="${WATCHDOG_INFRA_MATCH:-Runner\.(Listener|Worker|PluginHost|Service)|/actions-runner/bin/}"
# How far before this watchdog a process may have started and still count as
# the step it guards. The step is launched by the runner *after* the arm step
# returns, so on a runner this only has to absorb scheduling noise between two
# /proc reads; it is a knob so a test can widen it rather than race it.
arm_slack_s="${WATCHDOG_ARM_SLACK_S:-2}"
poll_s="${WATCHDOG_POLL_S:-10}"
step_grace_s="${WATCHDOG_STEP_GRACE_S:-30}"
# Half the deadline: the guarded step has been running very nearly the whole
# deadline when this fires, and a process younger than that began after the
# deadline was already counting, which is what a tail step is. The floor has to
# stay longer than the salvage tail can run, or a tail step becomes selectable
# again — so a much shorter deadline, or a much longer tail, is a reason to
# revisit this ratio rather than to leave it deriving itself. It is deliberately
# generous in that direction: the cost of a floor that is too high is a wedge
# this script declines to end, which is the failure we already have, while the
# cost of one too low is killing the step that salvages the cell. Only a root is
# ever judged by it, and a step's root process starts when its step does.
min_step_age_s="${WATCHDOG_MIN_STEP_AGE_S:-$((deadline_s / 2))}"
clk_tck="$(getconf CLK_TCK 2>/dev/null || echo 100)"

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

cmdline_of() { tr '\0' ' ' <"/proc/$1/cmdline" 2>/dev/null; }

# Field 4 of /proc/<pid>/stat, read past the comm field — which is parenthesised
# and may itself contain spaces and parentheses, so it cannot be split on.
# Stripping to the last ") " is exact for every ordinary comm, and a process
# whose own comm contains that sequence shifts its own fields; since a process
# can only do that to itself, no decision about a *third* process may be built
# on these readers.
ppid_of() {
  local stat _state ppid
  [ -r "/proc/$1/stat" ] || return 1
  stat="$(</proc/"$1"/stat)" || return 1
  stat="${stat##*) }"
  read -r _state ppid _ <<<"$stat"
  [ -n "$ppid" ] || return 1
  printf '%s\n' "$ppid"
}

# When a process started, in clock ticks since boot: field 22 of
# /proc/<pid>/stat, read past the comm as above. Read from /proc rather than
# from `ps`, so a binary shadowed on PATH cannot forge an age. Start times are
# compared rather than ages because an age keeps growing while this script
# waits out a grace, and the question — did this process begin before or after
# the watchdog was armed — has a fixed answer.
start_of() {
  local stat fields start
  [ -r "/proc/$1/stat" ] || return 1
  stat="$(</proc/"$1"/stat)" || return 1
  stat="${stat##*) }"
  read -r -a fields <<<"$stat"
  # Field 22 of the whole line is field 20 of what follows the comm.
  start="${fields[19]:-}"
  [ -n "$start" ] || return 1
  printf '%s\n' "$start"
}

# Now, on the same clock.
uptime_ticks() {
  local uptime
  read -r uptime _ </proc/uptime || return 1
  printf '%s\n' "$(( ${uptime%.*} * clk_tck ))"
}

# This process and everything above it, walked at fire time.
collect_ancestry() {
  local pid="$$" guard=0
  own_ancestry=()
  while [ "$pid" -gt 1 ] && [ "$guard" -lt 64 ]; do
    own_ancestry+=("$pid")
    pid="$(ppid_of "$pid")" || break
    guard=$((guard + 1))
  done
}

# The first of two questions, and the one asked of every kill target: may this
# be signalled at all? Three independent reasons to refuse, any one of which
# alone keeps the runner's infrastructure safe:
#
#   - the anchor's own pids: whatever parentage discovery found, the worker it
#     was found under is never itself a candidate;
#   - argv: anything naming the runner's infrastructure is refused, as is a
#     process whose argv cannot be read at all — unreadable fails closed;
#   - ancestry: this watchdog's own ancestors are refused. On a runner the
#     watchdog is an orphan of the arm step and no ancestor of the engine step,
#     so this can never block the escalation; under a test harness the harness's
#     own step *is* an ancestor, so a suite driving this script cannot signal
#     the process running it.
signalable() {
  local pid="$1" other cmd
  [ "$pid" -gt 1 ] 2>/dev/null || return 1
  [ "$pid" != "$$" ] || return 1
  for other in "${own_ancestry[@]}"; do
    [ "$pid" = "$other" ] && return 1
  done
  for other in "${worker_pids[@]}"; do
    [ "$pid" = "$other" ] && return 1
  done
  cmd="$(cmdline_of "$pid")"
  [ -n "$cmd" ] || return 1
  printf '%s' "$cmd" | grep -Eq -- "$infra_match" && return 1
  return 0
}

# The second question, and it is asked only of a *root*: is this the step this
# watchdog was armed for, rather than some other step of the same job? The
# guarded step began just after the arming and has been running ever since,
# which nothing else on the runner has done — anything older predates the
# arming (the sidecars, the model proxy, an orphan of an earlier step) and
# anything younger began after the deadline was already counting, which is what
# a tail step is. Both bounds matter: the steps that salvage the cell are
# children of the same worker, and killing one would destroy the evidence this
# script exists to save.
#
# Descendants are deliberately *not* asked. A root's children are the guarded
# step by construction — parentage is the whole evidence — and most of what
# holds a wedged step open is spawned during its run, so asking a descendant
# its age would refuse exactly the processes the tree kill exists to reach.
guarded_step_root() {
  local pid="$1" start now
  # Fail closed rather than open: without our own start time the window has no
  # reference, and an unbounded window is how a tail step gets killed.
  [ -n "$own_start" ] || return 1
  start="$(start_of "$pid")" || return 1
  now="$(uptime_ticks)" || return 1
  [ "$start" -ge $((own_start - arm_slack_s * clk_tck)) ] || return 1
  [ "$start" -le $((now - min_step_age_s * clk_tck)) ] || return 1
  return 0
}

# The step the runner is currently waiting on, by both routes: the worker's own
# children (parentage, which holds whatever the action's argv looks like) and
# the action's entry argv (precise where it still matches, and the only route
# left if the worker cannot be found).
discover_step_roots() {
  local candidates=() roots=() byname=() pid ppid worker candidate seen=""
  if [ "${#worker_pids[@]}" -gt 0 ]; then
    while read -r pid ppid; do
      [ -n "$ppid" ] || continue
      for worker in "${worker_pids[@]}"; do
        [ "$ppid" = "$worker" ] && candidates+=("$pid")
      done
    done < <(ps -u "$uid" -o pid=,ppid= 2>/dev/null)
  fi
  mapfile -t byname < <(pgrep -u "$uid" -f -- "$runner_match")
  [ "${#byname[@]}" -gt 0 ] && candidates+=("${byname[@]}")
  for candidate in "${candidates[@]}"; do
    case " $seen " in *" $candidate "*) continue ;; esac
    seen="$seen $candidate"
    signalable "$candidate" && guarded_step_root "$candidate" && roots+=("$candidate")
  done
  [ "${#roots[@]}" -gt 0 ] && printf '%s\n' "${roots[@]}"
  return 0
}

# Every process under this runner user reachable downward from the given roots,
# roots included: a lingering grandchild still holding the step's stdout keeps
# the runner waiting even once the entry process is gone, so the tree is the
# unit that ends a step. Traversal never descends through this watchdog. The
# refusals apply to the result, not to the walk — a refused process is dropped
# from the kill list rather than pruning the branch below it — and `ps -u`
# selects on the effective uid, so a setuid intermediate would hide its own
# subtree from the walk.
tree_pids() {
  local pairs=() out=() line pid ppid root added=1
  declare -A want=()
  for root in "$@"; do want["$root"]=1; done
  mapfile -t pairs < <(ps -u "$uid" -o pid=,ppid= 2>/dev/null)
  while [ "$added" -eq 1 ]; do
    added=0
    for line in "${pairs[@]}"; do
      read -r pid ppid <<<"$line"
      [ -n "$pid" ] && [ -n "$ppid" ] || continue
      [ "$pid" = "$$" ] && continue
      if [ -n "${want[$ppid]:-}" ] && [ -z "${want[$pid]:-}" ]; then
        want["$pid"]=1
        added=1
      fi
    done
  done
  for pid in "${!want[@]}"; do
    signalable "$pid" && out+=("$pid")
  done
  [ "${#out[@]}" -gt 0 ] && printf '%s\n' "${out[@]}"
  return 0
}

# Which of a recorded (pid, argv) pair of lists are still the processes that
# were recorded: alive, argv unchanged, and still refusal-free. Re-verifying
# argv is what makes a recorded pid list safe to signal later — a recorded
# process may have exited and its pid been handed to something else meanwhile.
# The two arguments are array *names*, so callers pass literals: a name built
# from data would be evaluated by the nameref.
verify_recorded() {
  local -n _pids="$1" _cmds="$2"
  # Underscored so a caller's own locals can never be what the namerefs bind.
  local _index _pid _out=()
  for _index in "${!_pids[@]}"; do
    _pid="${_pids[$_index]}"
    alive "$_pid" || continue
    # Defaulted: two lists of different lengths would otherwise abort this
    # subshell under `set -u`, and empty output reads as "nothing survived" —
    # which would silently skip the signal that follows.
    [ "$(cmdline_of "$_pid")" = "${_cmds[$_index]-}" ] || continue
    signalable "$_pid" && _out+=("$_pid")
  done
  [ "${#_out[@]}" -gt 0 ] && printf '%s\n' "${_out[@]}"
  return 0
}

# What is left of the step recorded at the deadline. The whole tree, not just
# its roots: the runner waits on the step's output as well as on its entry
# process, so a lingering descendant holds the step open after the entry is
# gone, and a survival check watching only the roots would call that concluded.
surviving_members() { verify_recorded step_tree step_tree_cmds; }

# End the step itself, so the runner concludes it as a failure and runs the
# capture tail. Returns the pids ended, for the marker.
end_step_tree() {
  local roots=("$@") tree=() tree_cmds=() still=() waited=0 pid
  # Expanded again here rather than reused from the deadline: a wedged tree can
  # still be spawning, and anything it started is holding the step open too.
  mapfile -t tree < <(tree_pids "${roots[@]}")
  escalation_capture
  if [ "${#tree[@]}" -eq 0 ]; then
    log "no step process left to end"
    return 1
  fi
  for pid in "${tree[@]}"; do
    tree_cmds+=("$(cmdline_of "$pid")")
  done
  log "ending the step's process tree (pids: ${tree[*]})"
  kill -TERM "${tree[@]}" 2>/dev/null
  while [ "$waited" -lt "$step_grace_s" ] && alive "${tree[@]}"; do
    sleep "$poll_s"
    waited=$((waited + poll_s))
  done
  # The list is a whole grace old by now, so what survived it is re-verified
  # before the harder signal rather than blasted from memory.
  mapfile -t still < <(verify_recorded tree tree_cmds)
  if [ "${#still[@]}" -gt 0 ]; then
    log "SIGTERM did not end the step; escalating to SIGKILL (pids: ${still[*]})"
    kill -KILL "${still[@]}" 2>/dev/null
  fi
  ended_pids="${tree[*]}"
  return 0
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

# What the escalation did, appended to whichever marker the deadline wrote, so
# the one file the disarm step already surfaces carries the whole account.
note_escalation() {
  local marker="$1" outcome="$2"
  {
    echo "escalated_at=$(stamp)"
    echo "escalation=${outcome}"
    echo "escalated_pids=${ended_pids}"
    echo "step_tree=${step_tree[*]}"
  } >>"$dir/$marker"
}

# The state at the moment of the escalation: whether the engine kill landed,
# and what is still holding the step open. Same shapes-only rules as the first
# capture.
escalation_capture() {
  ps -ww -u "$uid" -o pid,ppid,stat,wchan:32,etime,args --forest \
    >"$dir/process-tree-escalation.txt" 2>&1
}

mkdir -p "$dir"
uid="$(id -u)"
own_ancestry=()
worker_pids=()
own_start=""
step_roots=()
step_tree=()
step_tree_cmds=()
ended_pids=""

log "armed; firing in ${deadline_s}s unless disarmed"
elapsed=0
while [ "$elapsed" -lt "$deadline_s" ]; do
  sleep "$poll_s"
  elapsed=$((elapsed + poll_s))
done

# Everything the escalation may signal is decided now, at the deadline, while
# the wedged step is still the step the runner is waiting on.
collect_ancestry
# Read now rather than at launch only because nothing before the deadline needs
# it; a process's start time does not change. Empty on failure, which refuses
# every root rather than widening the window to everything.
own_start="$(start_of "$$")" || own_start=""
mapfile -t worker_pids < <(pgrep -u "$uid" -f -- "$worker_match")
mapfile -t step_roots < <(discover_step_roots)
if [ "${#step_roots[@]}" -eq 0 ]; then
  log "deadline reached but no step process was identified; the step cannot be ended from here"
else
  # The whole tree, recorded with its argv: what the grace below watches for
  # survival, and what a maintainer reads back off the marker.
  mapfile -t step_tree < <(tree_pids "${step_roots[@]}")
  for root in "${step_tree[@]}"; do
    step_tree_cmds+=("$(cmdline_of "$root")")
  done
  log "the step this watchdog guards is pids: ${step_tree[*]}"
fi

# `-u` narrows to this runner user: the engine's root-owned sudo wrapper
# carries the same arguments and could not be signalled from here anyway.
mapfile -t pids < <(pgrep -u "$uid" -f -- "$match")
# Through the same refusals as everything else. The shipped pattern names the
# action's invocation and nothing else, but a pattern is a claim about argv and
# this is the one signal path that would otherwise trust it outright — and the
# refusals are exactly what keeps a mis-set pattern off this script's own
# ancestors and off the runner's processes.
engine_pids=()
for pid in "${pids[@]}"; do
  signalable "$pid" && engine_pids+=("$pid")
done
pids=("${engine_pids[@]}")
if [ "${#pids[@]}" -eq 0 ]; then
  # The deadline is only reached while the engine step is still running, so
  # matching nothing means either the engine never spawned — a wedge in one of
  # the step's earlier phases, the two npm installs or the proxy start — or the
  # pattern no longer names it. The captured tree is the evidence that tells
  # those apart afterwards; either way the step still has to end, and with no
  # engine to kill there is nothing to wait for, so the tree goes now.
  log "deadline reached but no process matches the engine; recording and ending the step"
  capture_runner_state
  {
    echo "stood_down_at=$(stamp)"
    echo "deadline_s=${deadline_s}"
    echo "match=${match}"
  } >"$dir/STOOD_DOWN"
  mapfile -t survivors < <(surviving_members)
  if [ "${#survivors[@]}" -eq 0 ]; then
    note_escalation STOOD_DOWN "no step process was identified at the deadline"
  elif end_step_tree "${survivors[@]}"; then
    note_escalation STOOD_DOWN "the step's tree was ended with no engine process present"
  else
    note_escalation STOOD_DOWN "the step's tree was already gone"
  fi
  exit 0
fi

log "deadline reached with the engine still running (pids: ${pids[*]})"
capture_runner_state
engine_cmds=()
for pid in "${pids[@]}"; do
  engine_cmds+=("$(cmdline_of "$pid")")
  {
    echo "## pid ${pid}"
    cmdline_of "$pid"
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
while [ "$waited" -lt "$step_grace_s" ] && alive "${pids[@]}"; do
  sleep "$poll_s"
  waited=$((waited + poll_s))
done
# Re-verified before the harder signal, as the step's tree is: by now the list
# has been held across a whole grace.
mapfile -t engine_survivors < <(verify_recorded pids engine_cmds)
if [ "${#engine_survivors[@]}" -gt 0 ]; then
  log "SIGTERM did not land; escalating to SIGKILL (pids: ${engine_survivors[*]})"
  kill -KILL "${engine_survivors[@]}" 2>/dev/null
fi

# A dead engine normally brings the step down within seconds. Where it does
# not, the wedge was never only in the engine, and a step that never ends is
# the whole failure this guards against — so the step's own tree goes too.
if [ "${#step_roots[@]}" -eq 0 ]; then
  note_escalation FIRED "no step process was identified at the deadline"
else
  waited=0
  while [ "$waited" -lt "$step_grace_s" ] && [ -n "$(surviving_members)" ]; do
    sleep "$poll_s"
    waited=$((waited + poll_s))
  done
  mapfile -t survivors < <(surviving_members)
  if [ "${#survivors[@]}" -eq 0 ]; then
    log "the step ended with the engine; no escalation needed"
    note_escalation FIRED "the step ended with the engine"
  elif end_step_tree "${survivors[@]}"; then
    note_escalation FIRED "the step outlived the engine kill and its tree was ended"
  else
    note_escalation FIRED "the step's tree was already gone"
  fi
fi

log "fired; the engine step should now fail and leave the capture tail to run"
