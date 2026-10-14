#!/usr/bin/env bash
# The promotion-record writer's plumbing: plan a promotion merge's record, tag
# it, apply it, commit it and jail the commit (`prepare`); then push the tags
# and the jailed commit to `main` (`push`). Every decision is a tested
# `fedcourts` command (`promotion-record`, `assert-promotion-record-diff`); this
# file only orders them and moves bytes.
#
# The order is the writer requirements' (docs/process-version.md):
#   prepare — fetch origin/main, origin/staging and every tag; check out the
#             fetched main tip detached (its code is the code that runs, and
#             its tree is the base); plan; create the planned annotated tags
#             locally with the plan's messages; apply; commit with exactly one
#             parent, the fetched main tip; jail that commit.
#   push    — push each planned tag by explicit refspec (a remote tag holding a
#             different object is refused, never replaced), then push the
#             jailed commit as `<sha>:refs/heads/main` with a lease on the base.
#             A rejected commit push re-runs `prepare` from the new tip, with
#             the write token removed from its environment, and pushes again —
#             never a rebase of a jailed commit.
#
# `prepare` holds no credential: the repository is public, so the fetch is
# anonymous. `push` alone reads WRITE_TOKEN, the data App token the workflow
# mints after the first jail passed, and passes it to git as a per-command
# header, never into the remote URL or a config file.
#
# Usage:
#   write.sh prepare <merge-sha>   # writes base, head, record to $GITHUB_OUTPUT
#   write.sh push <merge-sha>      # needs WRITE_TOKEN; re-prepares on rejection
#
# Environment: GITHUB_REPOSITORY, RUNNER_TEMP, GITHUB_OUTPUT,
# GITHUB_STEP_SUMMARY; PUSH_MAX_ATTEMPTS (default 3) bounds the re-plans.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PROMOTION_RECORD_REMOTE points the writer at another remote (a local bare
# repository) for the simulation the tests run; the workflow never sets it.
repo_url="${PROMOTION_RECORD_REMOTE:-https://github.com/${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}.git}"
work="${RUNNER_TEMP:?RUNNER_TEMP must be set}/promotion-record"
mkdir -p "$work"

refs=(--main-ref origin/main --staging-ref origin/staging)

fetch() {
  # Remote-tracking refs, never local branches, and every tag: the plan reads
  # the tags to name and adopt its own, and a missing tag reads as a free name.
  git fetch --quiet --force --tags "$repo_url" \
    "+refs/heads/main:refs/remotes/origin/main" \
    "+refs/heads/staging:refs/remotes/origin/staging"
}

tag_locally() {
  # Each planned tag the plan does not adopt is created here, annotated, on the
  # merge, with the plan's message byte for byte (`--cleanup=verbatim` keeps
  # git from editing it). An adopted tag already names the merge as planned;
  # the jail re-checks both.
  local merge="$1" plan="$2" kind name message
  for kind in promotion_tag prereg_tag; do
    if [ "$(jq -r --arg k "$kind" '.[$k] == null' "$plan")" = "true" ]; then
      continue
    fi
    name=$(jq -r --arg k "$kind" '.[$k].name' "$plan")
    if [ "$(jq -r --arg k "$kind" '.[$k].adopt' "$plan")" = "true" ]; then
      echo "adopting ${name}"
      continue
    fi
    message="${work}/${kind}.msg"
    jq -j --arg k "$kind" '.[$k].message' "$plan" >"$message"
    git tag --annotate --cleanup=verbatim --file "$message" "$name" "$merge"
    echo "tagged ${name} on ${merge}"
  done
}

planned_tags() {
  jq -r '[.promotion_tag, .prereg_tag] | map(select(. != null) | .name) | .[]' "$1"
}

prepare() {
  local merge="$1" plan="${work}/plan.json" applied="${work}/applied.json" base head
  fetch
  base=$(git rev-parse --verify "origin/main^{commit}")
  git checkout --quiet --detach "$base"
  uv run --locked fedcourts promotion-record --merge "$merge" "${refs[@]}" >"$plan"
  tag_locally "$merge" "$plan"
  uv run --locked fedcourts promotion-record --merge "$merge" "${refs[@]}" --apply >"$applied"
  head=""
  if [ "$(jq '.applied | length' "$applied")" -gt 0 ]; then
    git add -- src/fedcourtsai/process_registry.json docs/freeze-record.md
    git commit --quiet --no-verify \
      -m "promotion: record $(jq -r '.promotion_tag.name' "$plan") (${merge:0:9})" \
      -m "Fills and stamps the placeholders and pending registrations promotion merge ${merge} added, as \`fedcourts promotion-record\` plans them."
    head=$(git rev-parse HEAD)
    uv run --locked fedcourts assert-promotion-record-diff \
      --merge "$merge" --base "$base" --head "$head" "${refs[@]}"
  else
    echo "the merge adds no placeholder the key set fills and no pending registration: tags only"
  fi
  {
    echo "base=${base}"
    echo "head=${head}"
    echo "plan=${plan}"
  } >>"${GITHUB_OUTPUT:-/dev/null}"
  echo "$base $head"
}

git_auth() {
  # The write token reaches git as a header for this one command, never into a
  # URL or a config file a later command could read.
  local header
  header="AUTHORIZATION: basic $(printf 'x-access-token:%s' "${WRITE_TOKEN:?WRITE_TOKEN must be set}" | base64 -w0)"
  git -c "http.https://github.com/.extraheader=${header}" "$@"
}

push() {
  local merge="$1" plan="${work}/plan.json" base head attempt name log
  base="${BASE:?BASE must be set}"
  head="${HEAD_SHA:-}"
  max="${PUSH_MAX_ATTEMPTS:-3}"
  for attempt in $(seq 1 "$max"); do
    while IFS= read -r name; do
      # A plain push of a tag never replaces one: an existing remote tag on
      # another object is rejected ("already exists"), and the record ruleset
      # blocks the update besides. That rejection is final — an operator
      # investigates, the writer never retries past it.
      git_auth push --quiet "$repo_url" "refs/tags/${name}:refs/tags/${name}"
      echo "pushed ${name}"
    done < <(planned_tags "$plan")
    if [ -z "$head" ]; then
      echo "no record commit to push"
      return 0
    fi
    log=$(mktemp)
    if git_auth push --force-with-lease="refs/heads/main:${base}" "$repo_url" \
      "${head}:refs/heads/main" >"$log" 2>&1; then
      cat "$log"
      echo "pushed the record commit ${head} onto ${base}"
      return 0
    fi
    cat "$log"
    if ! grep -qiE 'stale info|non-fast-forward|fetch first|\[rejected\]' "$log"; then
      echo "::error::the record commit push failed for a reason other than main advancing"
      return 1
    fi
    if [ "$attempt" -ge "$max" ]; then
      break
    fi
    echo "::warning::main advanced past ${base}; re-planning from the new tip (attempt ${attempt}/${max})"
    # Re-plan from scratch on the new base, the write token out of the
    # planner's environment.
    read -r base head < <(env -u WRITE_TOKEN bash "${here}/write.sh" prepare "$merge" | tail -n 1)
  done
  echo "::error::main kept advancing; the record commit was not pushed after ${max} attempts"
  return 1
}

case "${1:-}" in
  prepare) prepare "${2:?the merge sha}" ;;
  push) push "${2:?the merge sha}" ;;
  *)
    echo "usage: write.sh prepare|push <merge-sha>" >&2
    exit 2
    ;;
esac
