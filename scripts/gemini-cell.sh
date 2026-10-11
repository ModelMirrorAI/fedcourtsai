#!/usr/bin/env bash
# The gemini engine step of a cell (run-predict.yml, run-evaluate.yml, and
# integration-test.yml's engine-actions-smoke probe of that invocation): one
# headless gemini-cli turn, retried in place when the turn ends on a transient
# fault.
#
# Why in place. gemini-cli ends a turn whose model stream went bad — after its
# own mid-stream retries are spent — with an ordinary zero exit and an
# `INVALID_STREAM` error inside its JSON result, seconds into the cell while
# sibling cells on the same model run to completion. Nothing on the cell's side
# retries that: the next chance is a later scheduled run, by which time a
# fast-moving event may have resolved and the cell has turned retrospective.
# So the step itself takes up to `GEMINI_MAX_ATTEMPTS` fresh turns, each a new
# CLI process and a new session, under four rules:
#
#   * **Only a transient fault retries.** Each attempt is classified by
#     `fedcourts engine-attempt-class`, which is the local runner's own
#     classifier over the runner's own signature sets, so the step and the
#     runner cannot disagree on what a serving hiccup looks like. A permanent
#     fault (content filter, context length, auth), a spent quota and a fault
#     nothing recognizes all end the step on the attempt that met them.
#   * **Only inside the one engine deadline.** The step keeps its
#     `timeout-minutes` and its watchdog bracket, so no attempt can run past the
#     deadline whatever this script does; on top of that a retry starts only when
#     at least `GEMINI_RETRY_MIN_REMAINING_S` of the step's deadline would
#     remain after its backoff. That floor is measured against the step's
#     timeout and so includes the watchdog's three-minute margin; what is left
#     before the watchdog fires is still more than a whole cell of the longest
#     kind observed, so a retry is a fresh chance at the cell and not a cell the
#     deadline then kills.
#   * **Only from a clean output root.** Before the first attempt the cell's
#     output root is snapshotted (`fedcourts cell-output-snapshot`); before a
#     retry everything an attempt added under it is removed
#     (`fedcourts cell-output-reset`), so a half-written file from a failed turn
#     is never read — by the retry, the completion sentinel or the tail — as the
#     cell's output. An attempt that already produced the cell's judgment
#     artifact is never retried, since a retry would discard it; nor is one that
#     wrote the cell's flags.json, a disclosure (in a replay cell, of
#     outcome-revealing material) that a fresh session would know nothing of;
#     nor is one whose root cannot be snapshotted or reset.
#   * **Every attempt is accounted for.** The engine's telemetry log is left in
#     place across attempts: gemini-cli 0.49.0 opens it for append, so the
#     usage and retrieval captures behind this step read every attempt's model
#     calls and tool calls — the tokens a failed turn spent were really spent,
#     and what it retrieved was really retrieved. (Re-check on a CLI bump.)
#
# The step's exit status is the last attempt's, so the cell's tail reads it as
# the outcome of the turn that counted. Each attempt's stdout (the JSON result)
# and stderr stream into the job log as they are written, and are also kept
# under the runner temp dir, outside the workspace and the cell artifact.
#
# Usage: gemini-cell.sh <predict|evaluate> <actor>
#
# From the step's env: MODEL_ID and PROMPT (the invocation), COURT_ID,
# DOCKET_ID, EVENT_ID and RUN_ID (the cell), ENGINE_DEADLINE_MINUTES (the job's
# engine deadline, which is also the step's timeout), RUNNER_TEMP, and the
# engine's key. GEMINI_RESULT_FILE, when set, receives a copy of the last
# attempt's JSON result.
#
# Knobs, defaulted here and left unset by the workflows; they exist so a test
# can drive this against a stub engine on its own clock:
#   GEMINI_MAX_ATTEMPTS           total attempts, the first included
#   GEMINI_RETRY_MIN_REMAINING_S  deadline that must remain for a retry to start
#   GEMINI_RETRY_BACKOFF_S        the backoff unit: a retry after attempt N
#                                 waits N units plus up to one unit of jitter

# Not `-e`: a failed attempt, or a failed classification, must reach the
# decision below rather than end the step mid-loop.
set -uo pipefail

role="${1:?usage: gemini-cell.sh <predict|evaluate> <actor>}"
actor="${2:?usage: gemini-cell.sh <predict|evaluate> <actor>}"
max_attempts="${GEMINI_MAX_ATTEMPTS:-3}"
min_remaining_s="${GEMINI_RETRY_MIN_REMAINING_S:-1200}"
backoff_s="${GEMINI_RETRY_BACKOFF_S:-15}"

# Checked as digits before any arithmetic, and before the engine starts: a bad
# knob must fail loudly here rather than be read as zero further down.
for value in "$max_attempts" "$min_remaining_s" "$backoff_s" "${ENGINE_DEADLINE_MINUTES:-}"; do
  case "$value" in
    "" | *[!0-9]* | 0?*)
      echo "::error::the gemini step's attempt knobs and the engine deadline must be plain whole numbers"
      exit 1
      ;;
  esac
done
if [ "$max_attempts" -lt 1 ]; then
  echo "::error::the gemini step needs at least one attempt"
  exit 1
fi
deadline_s=$((ENGINE_DEADLINE_MINUTES * 60))

cell="${role} ${actor} ${COURT_ID}/${DOCKET_ID} ${EVENT_ID}"
attempts_dir="${RUNNER_TEMP:?}/gemini-attempts"
rm -rf "$attempts_dir"
mkdir -p "$attempts_dir"
coords=(--role "$role" --court "$COURT_ID" --docket "$DOCKET_ID" --event "$EVENT_ID"
  --actor "$actor" --run-id "$RUN_ID")

# The harness commands run without the engine's key because they need none.
# Hygiene, not a boundary: the agent runs as this same uid with the run of the
# workspace and the runner temp dir, so it could already read the key from the
# engine process — and the copy of this script the step runs is no more out of
# its reach than the workspace is; the copy guards against a mid-turn edit to
# `scripts/`, not against a hostile agent.
harness() { env -u GEMINI_API_KEY uv run fedcourts "$@"; }

snapshot="$attempts_dir/outputs-before.json"
can_reset=true
if ! harness cell-output-snapshot "${coords[@]}" --out "$snapshot"; then
  echo "::warning::gemini (${cell}): the output root could not be snapshotted, so a failed attempt will not be retried"
  can_reset=false
fi

attempt=0
status=0
out=""
while :; do
  attempt=$((attempt + 1))
  out="$attempts_dir/attempt-${attempt}.json"
  err="$attempts_dir/attempt-${attempt}.stderr"
  status_file="$attempts_dir/attempt-${attempt}.status"
  # The invocation the cells and the smoke share, flag for flag. Both streams
  # reach the job log live — on a turn the watchdog ends, the stderr already
  # streamed is the diagnostic that survives — and are captured for the
  # classifier as they go.
  {
    gemini --yolo --model "$MODEL_ID" --prompt "$PROMPT" --output-format json | tee "$out"
    echo "${PIPESTATUS[0]}" > "$status_file"
  } 2> >(tee "$err" >&2)
  # The stderr capture is complete before anything reads it.
  wait "$!" 2> /dev/null || true
  status=$(cat "$status_file" 2> /dev/null || true)
  case "$status" in
    "" | *[!0-9]*) status=1 ;;
  esac

  verdict=$(harness engine-attempt-class --exit-code "$status" \
    --stdout-file "$out" --stderr-file "$err") || verdict=""
  case "$verdict" in
    ok | transient | permanent | terminal_quota) ;;
    *) verdict=unclassified ;;
  esac
  echo "gemini attempt ${attempt}/${max_attempts}: exit ${status}, ${verdict}"
  [ "$verdict" = ok ] && break

  # The fault's own name for the log, shape-screened: it lands in a workflow
  # annotation, and a result file is the agent's turn's to shape.
  fault=$(jq -r '.error.type? // empty' "$out" 2> /dev/null | head -c 64 || true)
  case "$fault" in
    *[!A-Za-z0-9_]*) fault="" ;;
  esac
  wait_s=$((backoff_s * attempt + RANDOM % (backoff_s + 1)))

  reason=""
  if [ "$verdict" = unclassified ]; then
    reason="the attempt could not be classified"
  elif [ "$verdict" != transient ]; then
    reason="the fault is not a transient one"
  elif [ "$attempt" -ge "$max_attempts" ]; then
    reason="all ${max_attempts} attempts are spent"
  elif [ "$can_reset" != true ]; then
    reason="there is no snapshot to reset the output root to"
  elif [ "$(harness finalize-produced "${coords[@]}" 2> /dev/null)" != "false" ]; then
    # Anything but a clear "false" — including a check that could not run —
    # keeps the attempt's output rather than wiping it.
    reason="the attempt produced the cell's output, which a retry would discard"
  elif [ $((SECONDS + wait_s + min_remaining_s)) -gt "$deadline_s" ]; then
    reason="under ${min_remaining_s}s of the ${ENGINE_DEADLINE_MINUTES}-minute engine deadline would remain"
  fi
  if [ -n "$reason" ]; then
    echo "::warning::gemini (${cell}): attempt ${attempt}/${max_attempts} ended ${verdict}${fault:+ (${fault})}; not retried: ${reason}"
    break
  fi
  harness cell-output-reset "${coords[@]}" --snapshot "$snapshot"
  reset_status=$?
  if [ "$reset_status" -ne 0 ]; then
    # Exit 3 is the reset declining on purpose: the attempt wrote the cell's
    # flags.json, a disclosure a fresh session would know nothing of.
    if [ "$reset_status" -eq 3 ]; then
      reason="the attempt wrote the cell's flags.json, whose disclosure a retry would discard"
    else
      reason="the output root could not be reset"
    fi
    echo "::warning::gemini (${cell}): attempt ${attempt}/${max_attempts} ended ${verdict}${fault:+ (${fault})}; not retried: ${reason}"
    break
  fi
  echo "::warning::gemini (${cell}): attempt ${attempt}/${max_attempts} ended transient${fault:+ (${fault})}; retrying from a clean output root in ${wait_s}s"
  sleep "$wait_s"
done

if [ -n "${GEMINI_RESULT_FILE:-}" ]; then
  cp "$out" "$GEMINI_RESULT_FILE"
fi
exit "$status"
