#!/usr/bin/env bash
# Runner-level bound on one engine cell step (run-predict.yml, run-evaluate.yml,
# and integration-test.yml's application-repro leg).
#
# The failure is a step that never concludes. It has two observed shapes, and
# this script has one trigger for each.
#
# **The success reaper**, which fires first because it is the safer of the two.
# An agent has been seen writing every output file its contract names,
# self-validating them, and printing its closing token count — and *then* the
# step froze in that state until the job cap cancelled the runner, destroying
# finished work. The hang is in teardown, after the agent is done, so the
# highest-value move is not to document the death but to conclude the step
# while the output is intact: watch for the cell's **completion sentinel** —
# every required output present, non-empty, and parsing — plus a write
# quiescence grace, so an agent still revising a draft is never cut off, then
# end the step's process tree. The step concludes, the capture tail runs, and
# the cell lands as the success it already was.
#
# **The deadline**, which stays as the second line for a wedge that never
# completes anything. It runs in three beats:
#
#   1. capture what the runner knows, first, so the evidence exists whatever
#      the kills then do;
#   2. end the engine, narrowly, by the pattern that names its invocation;
#   3. after a short grace, end the *step's own process tree* if the step is
#      still running — or immediately if no engine ever matched.
#
# Beat 3 is what actually converts that hang into a step failure. Killing the
# engine only concludes the step when the wedge is in the engine: a wedge in
# the action's node wrapper, or in a phase that runs before the engine spawns,
# leaves the wrapper waiting on nothing with the step still `in_progress`. A
# failed step is the same shape as a max-turns stop, which the tail already
# salvages.
#
# Neither trigger is engine-specific: the reaper reads files the contract names
# and the deadline reads the runner's own process shapes, so every cell of every
# engine is bracketed. The engine-match pattern below still names codex's
# invocation, because that is the only engine whose CLI the deadline has ever
# had to kill narrowly; on a cell of any other engine it simply matches nothing
# and the escalation goes straight to the step's tree, which is the path a
# never-spawned engine already takes.
#
# The arm step launches this detached and the disarm step kills it, so it can
# only ever fire while the engine step is still running.
#
# Configuration, all from the arm step's env:
#   WATCHDOG_DEADLINE_S  seconds to wait before firing (the call site does the
#                        arithmetic against the job cap and states it there)
#   WATCHDOG_DIR         where the diagnostics bundle and the marker are written
#   WATCHDOG_SENTINEL_PATHS  the completion sentinel, as a newline-separated list
#                        of the files a finished cell owes — `fedcourts
#                        cell-outputs`, run by the arm step before the agent
#                        starts. Empty disables the reaper and leaves the
#                        deadline alone. It arrives as **env, never as a file**,
#                        for the reason the check-in body does: the agent owns
#                        the workspace for the whole of its turn, and a list it
#                        could rewrite is a list it could satisfy vacuously
#   WATCHDOG_OUTPUT_DIR  the directory whose write quiescence the reaper waits
#                        on, from the same command's first line
#   WATCHDOG_QUIESCE_S   how long that directory must go unwritten before a
#                        complete cell is judged finished rather than mid-edit
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
#                        run in sequence, so the deadline plus three of these —
#                        plus the check-ins, each capped at curl's `--max-time`
#                        and three of them between the deadline and the first
#                        signal — is what has to stay inside the step's own
#                        timeout
#   WATCHDOG_ARM_SLACK_S  how far before this watchdog a process may have
#                        started and still be the step it guards
#   WATCHDOG_MIN_STEP_AGE_S  how long a process must already have been running
#                        to be the step this watchdog was armed for
#   WATCHDOG_CHECKIN_URL   the off-runner record: the API URL of this cell's
#   WATCHDOG_CHECKIN_TOKEN comment on the `codex-watchdog` telemetry issue, the
#   WATCHDOG_CHECKIN_BASE  comment-only App token that may PATCH it, and the
#                        armed body already written there, which every PATCH
#                        below appends to rather than replaces — so the arming
#                        time, the fire ETA and the run link survive the first
#                        heartbeat. All three come from the arm step
#                        (`fedcourts watchdog-checkin`); an empty URL or token
#                        makes every check-in below a no-op. Only the codex
#                        cells mint that token, so on every other engine this
#                        trio is empty by design and the record is the bundle
#                        the tail uploads — which a *reaped* cell keeps, since
#                        a concluded step is exactly what runs its own tail
#   WATCHDOG_HEARTBEAT_S how often to beat while waiting out the deadline
#
# The workflows set the first three, the sentinel pair, and the check-in trio,
# and leave the overrides at their defaults; the overrides exist so a test can
# drive this against processes of its own, on its own clock, rather than against
# a pattern naming a real engine or the runner that is executing the test.
#
# One channel does not live on the runner, because every runner-local one dies
# with a cancelled job — which is the failure being guarded against, so the
# bundle below is exactly the evidence a wedge is best placed to destroy. Each
# state this script passes is also PATCHed onto this cell's comment on the long-lived
# `codex-watchdog` issue, opened by the arm step before the agent starts. That
# body is composed **only** from this script's own variables and never from any
# file: WATCHDOG_DIR is writable by the very agent the watchdog may be about to
# kill, and a public issue is no place to let it choose what is said. It is
# stricter than the bundle for the same reason it outlives it — timestamps,
# phase names, pid numbers, counts and the configured deadline, never argv,
# never a file listing, never anything the cell read.
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
# The completion sentinel, read once here and never again: the arm step composed
# it before the agent had the tree, so re-reading it later would be reading a
# list the agent could have rewritten into one it had already satisfied.
sentinel_paths=()
if [ -n "${WATCHDOG_SENTINEL_PATHS:-}" ]; then
  while IFS= read -r sentinel_line; do
    [ -n "$sentinel_line" ] && sentinel_paths+=("$sentinel_line")
  done <<<"$WATCHDOG_SENTINEL_PATHS"
fi
output_dir="${WATCHDOG_OUTPUT_DIR:-}"
# Five minutes, and the asymmetry is the whole argument. Too high costs a wedge
# reaped later, against a job cap tens of minutes away; too low cuts off a cell
# that had written every file it owes and was still revising — which is the one
# outcome worse than the failure being fixed, and worse still now that a reaped
# cell is recorded as agent-clean, since it would publish as ready with nobody
# looking. So this is not set to the shortest gap that looks like "finished": the
# committed retrieval logs show a predict cell going 104 s between the moment all
# five of its required files first exist and its next write to one of them, so a
# grace near that is at the edge of the observed distribution rather than clear
# of it. Five minutes is clear of it and still costs a small fraction of the
# headroom the cells' own deadlines leave above the work envelope. It is also
# what keeps the reaper from racing the disarm step on a
# healthy cell, whose step concludes within seconds of its agent.
quiesce_s="${WATCHDOG_QUIESCE_S:-300}"
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
# The off-runner record. Empty is the ordinary degraded state, not an error: the
# arm step's check-in is best-effort, because a watchdog that refused to arm
# without a telemetry channel would trade the kill duty for the reporting one.
checkin_url="${WATCHDOG_CHECKIN_URL:-}"
checkin_token="${WATCHDOG_CHECKIN_TOKEN:-}"
checkin_body="${WATCHDOG_CHECKIN_BASE:-}"
# Long enough that an ordinary 40-minute wait costs single-digit API calls,
# short enough that a maintainer reading mid-round can tell a live watchdog from
# one whose runner is already gone.
heartbeat_s="${WATCHDOG_HEARTBEAT_S:-300}"

# Every knob below is expanded inside `$(( ))` somewhere, and arithmetic
# expansion evaluates a variable's *value* as an expression — so a non-numeric
# one is not a bad setting but an execution surface. All of them are repo-set
# (the workflows, or a test), so this is insurance rather than a boundary, and it
# fails the watchdog loudly rather than arming one that computes nonsense.
for _knob in WATCHDOG_DEADLINE_S WATCHDOG_POLL_S WATCHDOG_STEP_GRACE_S \
  WATCHDOG_ARM_SLACK_S WATCHDOG_MIN_STEP_AGE_S WATCHDOG_QUIESCE_S \
  WATCHDOG_HEARTBEAT_S; do
  _value="${!_knob:-0}"
  case "$_value" in
    "" | *[!0-9]*)
      echo "watchdog: ${_knob} is not a whole number of seconds" >&2
      exit 2
      ;;
  esac
done
unset _knob _value

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(stamp)] watchdog: $*"; }

# Append one stamped line to the off-runner record and re-PATCH the whole of it.
#
# The whole body every time, because a comment has no append operation — and
# accumulating it in a variable is also what keeps the payload composed from
# this script alone. Bounded three ways so this can never become the reason a
# kill is late: curl's own `--max-time`, an unconditional `|| true`, and the
# no-op when the arm step handed over no URL or token.
#
# The token reaches curl through a config file on a pipe, never as an argument:
# `capture_runner_state` below dumps every argument of every process this user
# owns into a bundle that gets published, so a token in argv would be one
# unlucky overlap away from a public artifact. Nothing here is echoed either —
# the watchdog's own log rides that same artifact.
checkin() {
  # The base is checked alongside the URL and the token, and for a sharper
  # reason than either: an empty one would PATCH a body carrying no marker over
  # a real record, destroying the row instead of skipping it. A broken hand-over
  # has to degrade to no telemetry, never to corrupted telemetry.
  [ -n "$checkin_url" ] && [ -n "$checkin_token" ] && [ -n "$checkin_body" ] || return 0
  local line payload
  for line in "$@"; do
    checkin_body="${checkin_body}"$'\n'"[$(stamp)] ${line}"
  done
  # `jq` does the JSON quoting rather than a hand-rolled escape, and its absence
  # is said out loud: a silently skipped encode would look exactly like a
  # watchdog whose runner was cancelled, which is the one thing this must never
  # be mistaken for.
  if ! payload="$(printf '%s' "$checkin_body" | jq -Rs '{body: .}' 2>/dev/null)"; then
    log "the off-runner check-in could not be encoded"
    return 0
  fi
  [ -n "$payload" ] || return 0
  if ! curl --max-time 10 --silent --output /dev/null \
    --request PATCH \
    --header "Accept: application/vnd.github+json" \
    --header "X-GitHub-Api-Version: 2022-11-28" \
    --config <(printf 'header = "Authorization: Bearer %s"\n' "$checkin_token") \
    --data-binary @- \
    --url "$checkin_url" <<<"$payload" 2>/dev/null; then
    log "the off-runner check-in did not land"
  fi
  return 0
}

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
# anything younger began after the trigger's own reference moment, which is what
# a tail step is. Both bounds matter: the steps that salvage the cell are
# children of the same worker, and killing one would destroy the evidence this
# script exists to save.
#
# The upper bound is `step_start_ceiling`, an absolute start time each trigger
# sets for itself, because the two triggers know different things. The deadline
# knows only how long it has been counting, so it uses the age floor. The reaper
# knows something sharper: the agent's output was already complete at the moment
# the sentinel was observed, so the step that wrote it had to start before then —
# and a tail step, which can only begin once the engine step has concluded,
# cannot have. That is what lets the reaper end a step the age floor would have
# refused for being younger than half a deadline it never reached.
#
# Descendants are deliberately *not* asked. A root's children are the guarded
# step by construction — parentage is the whole evidence — and most of what
# holds a wedged step open is spawned during its run, so asking a descendant
# its age would refuse exactly the processes the tree kill exists to reach.
guarded_step_root() {
  local pid="$1" start
  # Fail closed rather than open: without our own start time, or without a
  # ceiling, the window has no reference — and an unbounded window is how a tail
  # step gets killed.
  [ -n "$own_start" ] || return 1
  [ -n "$step_start_ceiling" ] || return 1
  start="$(start_of "$pid")" || return 1
  [ "$start" -ge $((own_start - arm_slack_s * clk_tck)) ] || return 1
  [ "$start" -le "$step_start_ceiling" ] || return 1
  return 0
}

# The step the runner is currently waiting on, by both routes: the worker's own
# children (parentage, which holds whatever the action's argv looks like) and
# the action's entry argv (precise where it still matches, and the only route
# left if the worker cannot be found).
#
# The first line of the output is a tally, and the roots follow it. It is a
# tally because the interesting failure is silent: discovery that proposes
# candidates and then refuses every one of them looks exactly like discovery
# that found nothing to propose, and the two have opposite fixes — a mis-set
# floor or a stale refusal against a runner whose shape moved. Counted here
# rather than derived by the caller because this runs in a subshell, so nothing
# it assigns survives.
discover_step_roots() {
  local candidates=() roots=() byname=() pid ppid worker candidate seen=""
  local seen_n=0 refused_infra=0 refused_age=0
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
    seen_n=$((seen_n + 1))
    if ! signalable "$candidate"; then
      refused_infra=$((refused_infra + 1))
      continue
    fi
    if ! guarded_step_root "$candidate"; then
      refused_age=$((refused_age + 1))
      continue
    fi
    roots+=("$candidate")
  done
  printf 'candidates=%d refused_infra=%d refused_age=%d\n' \
    "$seen_n" "$refused_infra" "$refused_age"
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
  checkin "step tree SIGTERM issued (pids: ${tree[*]})"
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
    checkin "step tree survived SIGTERM; SIGKILL issued (pids: ${still[*]})"
  else
    checkin "step tree ended on SIGTERM"
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

# Everything the escalation may signal, decided at whichever trigger is firing.
# `step_start_ceiling` is that trigger's own upper bound on when the guarded step
# can have started (see `guarded_step_root`); the rest is the same walk either
# way, so a change to discovery cannot drift between the two paths.
identify_step() {
  step_start_ceiling="$1"
  collect_ancestry
  # Read now rather than at launch only because nothing before a trigger needs
  # it; a process's start time does not change. Empty on failure, which refuses
  # every root rather than widening the window to everything.
  own_start="$(start_of "$$")" || own_start=""
  mapfile -t worker_pids < <(pgrep -u "$uid" -f -- "$worker_match")
  # The tally leads the output (see `discover_step_roots`); the roots follow it.
  mapfile -t discovery < <(discover_step_roots)
  discovery_counts="${discovery[0]:-candidates=0 refused_infra=0 refused_age=0}"
  step_roots=("${discovery[@]:1}")
  step_tree=()
  step_tree_cmds=()
  if [ "${#step_roots[@]}" -eq 0 ]; then
    log "no step process was identified; the step cannot be ended from here"
    return 0
  fi
  # The whole tree, recorded with its argv: what a grace watches for survival,
  # and what a maintainer reads back off the marker.
  mapfile -t step_tree < <(tree_pids "${step_roots[@]}")
  local pid
  for pid in "${step_tree[@]}"; do
    step_tree_cmds+=("$(cmdline_of "$pid")")
  done
  log "the step this watchdog guards is pids: ${step_tree[*]}"
}

# --- the completion sentinel --------------------------------------------------
#
# File truth, and only file truth: the reaper reads what the cell wrote, never
# what the engine said about it. The list is the **prompt contract's** — every
# file a finished cell owes — which is a stronger set than either downstream
# check. `finalize-produced` probes one artifact and `validate` resolves the two
# documents `prediction.json` points at; neither looks at `retrieval.md`, and
# `tooling.json` is validated where present but never required. That asymmetry is
# the right way round: a set narrower than the contract could call a cell
# finished mid-run, while a set this wide only ever declines to reap.
#
# Cheap by design, because it runs every poll for the whole deadline: existence
# and size first, and the JSON parse only once every file is there — which on an
# ordinary cell is the last minute of a forty-minute wait. Nothing here reads a
# file's *contents* into a variable, so nothing the agent writes can reach the
# log or the off-runner record.
#
# Deliberately weaker than `validate`: a parse, not a schema check. If the output
# is malformed the tail's own validate marks the cell not-validated and collect
# routes it to a draft PR a maintainer completes — which is strictly better than
# the job cap deleting it, and it keeps the schema's verdict in the one place
# that can act on it.
outputs_complete() {
  local path
  # An empty list is not a satisfied one: with no sentinel the reaper stays off
  # and the deadline is the only bound, which is the behaviour without it.
  [ "${#sentinel_paths[@]}" -gt 0 ] || return 1
  for path in "${sentinel_paths[@]}"; do
    [ -f "$path" ] && [ -s "$path" ] || return 1
  done
  for path in "${sentinel_paths[@]}"; do
    case "$path" in
      *.json)
        python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$path" 2>/dev/null || return 1
        ;;
    esac
  done
  return 0
}

# Has the cell stopped writing? An agent revising a draft it has already written
# once would otherwise satisfy the sentinel mid-edit, so completeness alone is
# never enough to end a step. `-quit` on the first hit keeps this to a directory
# walk that stops early, and it reads names and timestamps only.
#
# The cut-off is carried by a reference file and `-newer` — POSIX, and accepted
# by every `find` the tests and the runners put in front of this — rather than by
# `-newermt` and a relative time, which several implementations reject outright.
# (`touch -d @<epoch>` is itself a GNU spelling, so this is not portability in
# general; it is portability across the `find` implementations in play, which is
# where the divergence actually bit.) The failure mode is what makes it worth
# the care: a quiescence test that errors on every call reads exactly like a cell
# that never stops writing, so the reaper would simply never fire, silently.
outputs_quiescent() {
  [ -n "$output_dir" ] && [ -d "$output_dir" ] || return 1
  [ -n "$quiesce_ref" ] || return 1
  touch -d "@$(($(date +%s) - quiesce_s))" "$quiesce_ref" 2>/dev/null || return 1
  [ -z "$(find "$output_dir" -newer "$quiesce_ref" -print -quit 2>/dev/null)" ]
}

# The reap: the cell's work is done and the step will not end on its own, so end
# it. Returns 0 only when a step was actually identified and signalled.
#
# That return is what the `REAPED` marker means, and the marker is written only
# on it — deliberately, because the marker is not merely a record. The disarm
# step reads it to set `AGENT_OK`, which is what routes a cell into the *ready*
# run PR rather than the draft one, so a marker written before discovery would
# publish "the watchdog ended this step" on a path where the watchdog ended
# nothing. That path is reachable: an engine step that concludes on its own
# between the poll that saw quiescence and the disarm step's signal leaves no
# root to find, and the cell it belongs to — a max-turns stop, say — is exactly
# one a maintainer should see in the draft PR.
#
# Discovery therefore runs first; it signals nothing and takes milliseconds, so
# nothing is at risk from ordering it ahead of the capture. The capture still
# comes before any kill, and it is the diagnostic that matters most here — a
# process forest and socket table taken *after* the agent finished is what names
# whatever is holding a finished step open.
reap_completed_step() {
  log "the cell's outputs are complete and quiescent; ending the step"
  checkin "REAPING: outputs complete and quiescent for ${quiesce_s}s"
  # The sentinel's own moment is the ceiling: the step that wrote the output
  # started before it, and every tail step starts after. Where that reading was
  # unavailable the deadline's age floor stands in, which refuses more rather
  # than less — a refused reap is the deadline we already had.
  local ceiling
  if [ -n "$sentinel_ticks" ]; then
    ceiling="$sentinel_ticks"
  else
    ceiling="$(uptime_ticks)" || ceiling=""
    [ -n "$ceiling" ] && ceiling=$((ceiling - min_step_age_s * clk_tck))
  fi
  identify_step "$ceiling"
  checkin "discovery: roots=${#step_roots[@]} ${discovery_counts}"
  if [ "${#step_roots[@]}" -eq 0 ]; then
    # Nothing to end. Say so once and keep waiting rather than exiting: the
    # deadline is still the backstop, and the next poll re-asks — which is the
    # right answer whether the step concluded on its own (the disarm step is
    # about to end this process anyway) or discovery is momentarily blind.
    log "the outputs are complete but no step process was identified; not reaping"
    if [ -z "$reap_refused" ]; then
      reap_refused=1
      checkin "reap declined: no step process was identified at the sentinel"
    fi
    return 1
  fi
  capture_runner_state
  {
    echo "reaped_at=$(stamp)"
    echo "sentinel_at=${sentinel_at}"
    echo "quiesce_s=${quiesce_s}"
    echo "outputs=${#sentinel_paths[@]}"
    echo "roots=${#step_roots[@]}"
  } >"$dir/REAPED"
  if end_step_tree "${step_roots[@]}"; then
    note_escalation REAPED "the completed cell's step tree was ended"
  else
    note_escalation REAPED "the step's tree was already gone"
  fi
  log "reaped; the engine step should now conclude and leave the capture tail to run"
  checkin "outcome: reaped escalated_pids=${ended_pids:-none}"
  return 0
}

mkdir -p "$dir"
uid="$(id -u)"
own_ancestry=()
worker_pids=()
own_start=""
step_start_ceiling=""
step_roots=()
step_tree=()
step_tree_cmds=()
discovery_counts="candidates=0 refused_infra=0 refused_age=0"
ended_pids=""
sentinel_at=""
sentinel_ticks=""
# Set once the first reap has found nothing to end, so the off-runner record
# carries that fact one time rather than once per poll for the rest of a
# forty-minute wait.
reap_refused=""
# The quiescence cut-off's carrier, outside the bundle directory so it never
# rides the published artifact. Empty on failure, which leaves the quiescence
# test unsatisfiable and so the reaper off — the deadline is then the only bound,
# which is the behaviour without a sentinel at all.
quiesce_ref="$(mktemp 2>/dev/null)" || quiesce_ref=""
# The watchdog is killed by the disarm step rather than exiting, so this fires on
# the reap path and on the deadline's own exits; on a cancelled runner nothing
# survives to clean anyway.
trap '[ -n "$quiesce_ref" ] && rm -f "$quiesce_ref"' EXIT

log "armed; firing in ${deadline_s}s unless disarmed"
checkin "watching: deadline_s=${deadline_s} poll_s=${poll_s} grace_s=${step_grace_s}"
if [ "${#sentinel_paths[@]}" -eq 0 ]; then
  log "no completion sentinel was configured; the deadline is the only bound"
  checkin "sentinel: disabled (no required outputs were handed over)"
elif ! command -v python3 >/dev/null 2>&1; then
  # Said out loud rather than degraded silently: without the parse check the
  # sentinel would accept a half-written JSON file, so it stands down entirely
  # and a reader can see why the reaper never fired.
  sentinel_paths=()
  log "no python3 on this runner; the completion sentinel stands down"
  checkin "sentinel: disabled (no parser available)"
else
  checkin "sentinel: armed on ${#sentinel_paths[@]} required output(s), quiesce_s=${quiesce_s}"
fi

elapsed=0
since_beat=0
while [ "$elapsed" -lt "$deadline_s" ]; do
  sleep "$poll_s"
  elapsed=$((elapsed + poll_s))
  since_beat=$((since_beat + poll_s))
  # A beat is how a maintainer tells a watchdog that is still counting from one
  # whose runner was cancelled out from under it — the difference the whole
  # off-runner channel exists to make readable.
  if [ "$heartbeat_s" -gt 0 ] && [ "$since_beat" -ge "$heartbeat_s" ]; then
    since_beat=0
    checkin "waiting: elapsed=${elapsed}s of ${deadline_s}s${sentinel_at:+ sentinel_at=${sentinel_at}}"
  fi
  # Completeness is re-asked every poll, including after the sentinel has been
  # seen: an agent that goes back and rewrites a file leaves it briefly absent or
  # unparseable, and that must hold the reap off rather than race it. The
  # observation itself is recorded once — it is the durable proof that the work
  # existed, and a second announcement would say nothing new.
  outputs_complete || continue
  if [ -z "$sentinel_at" ]; then
    sentinel_at="$(stamp)"
    sentinel_ticks="$(uptime_ticks)" || sentinel_ticks=""
    log "completion sentinel observed at ${sentinel_at}"
    checkin "completion sentinel observed at ${sentinel_at} (outputs=${#sentinel_paths[@]})"
  fi
  outputs_quiescent || continue
  # Only a reap that actually ended a step ends this watchdog. Where there was
  # nothing to signal the loop keeps its deadline, which is the backstop for
  # every case discovery cannot see.
  if reap_completed_step; then
    exit 0
  fi
done
checkin "deadline reached after ${deadline_s}s"

# Everything the escalation may signal is decided now, at the deadline, while
# the wedged step is still the step the runner is waiting on. The ceiling is the
# age floor: a process younger than that began after the deadline was already
# counting, which is what a tail step is.
now_ticks="$(uptime_ticks)" || now_ticks=""
if [ -n "$now_ticks" ]; then
  identify_step "$((now_ticks - min_step_age_s * clk_tck))"
else
  identify_step ""
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
# The one line that says why the deadline went the way it did. `roots=0` with
# candidates behind it is a refusal that needs reading; `roots=0` with none is a
# runner whose shape no longer matches either discovery route.
checkin "discovery: roots=${#step_roots[@]} engine_matched=${#pids[@]} ${discovery_counts}"
if [ "${#pids[@]}" -eq 0 ]; then
  # The deadline is only reached while the engine step is still running, so
  # matching nothing means either the engine never spawned — a wedge in one of
  # the step's earlier phases, the two npm installs or the proxy start — or the
  # pattern no longer names it. The captured tree is the evidence that tells
  # those apart afterwards; either way the step still has to end, and with no
  # engine to kill there is nothing to wait for, so the tree goes now.
  log "deadline reached but no process matches the engine; recording and ending the step"
  checkin "STOOD_DOWN: no process matched the engine"
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
  checkin "outcome: stood_down escalated_pids=${ended_pids:-none}"
  exit 0
fi

log "deadline reached with the engine still running (pids: ${pids[*]})"
checkin "FIRED: the engine was still running (pids: ${pids[*]})"
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
checkin "engine SIGTERM issued (pids: ${pids[*]})"
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
  checkin "engine survived SIGTERM; SIGKILL issued (pids: ${engine_survivors[*]})"
else
  checkin "engine ended on SIGTERM"
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
  checkin "step survivors after the engine kill: ${#survivors[@]}"
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
checkin "outcome: fired escalated_pids=${ended_pids:-none}"
