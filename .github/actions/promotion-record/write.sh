#!/usr/bin/env bash
# The promotion-record writer's plumbing, one subcommand per workflow step, so
# no step that holds the write token ever plans: every decision is a tested
# `fedcourts` command (`promotion-record`, `assert-promotion-record-diff`); this
# file only orders them and moves bytes.
#
#   prepare <merge> — holds no credential. Fetch origin/main, origin/staging and
#                     every tag; check out the fetched main tip detached (its
#                     code is the code that runs, its tree the base); plan;
#                     create the planned annotated tags locally with the plan's
#                     messages; apply; commit with exactly one parent, the
#                     fetched tip; jail that commit. Any refusal exits non-zero.
#                     Writes base and head to its state file.
#   validate        — holds no credential. Re-reads the state file and refuses
#                     anything but a 40-hex base and an empty or 40-hex head
#                     whose only parent is the base; writes both to
#                     $GITHUB_OUTPUT for the push step.
#   push <merge>    — the only subcommand that reads WRITE_TOKEN. Push each
#                     planned tag by explicit refspec (a remote tag holding
#                     another object is refused, never replaced), then the
#                     jailed commit as `<sha>:refs/heads/main` with a lease on
#                     the base. It never re-plans: where `main` advanced it
#                     exits 3, and the workflow's next attempt group prepares
#                     again from the new tip, under a freshly minted token.
#
# `prepare` is anonymous (the repository is public). `push` passes the token to
# git as a header for that one command, after blanking any ambient header,
# with hooks disabled — never into a URL or a config file.
#
# Environment: GITHUB_REPOSITORY, RUNNER_TEMP, GITHUB_OUTPUT; push also reads
# WRITE_TOKEN, BASE and HEAD_SHA. PROMOTION_RECORD_REMOTE points the writer at
# another remote (a local bare repository) for the tests; the workflow never
# sets it.
set -euo pipefail

repo_url="${PROMOTION_RECORD_REMOTE:-https://github.com/${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}.git}"
work="${RUNNER_TEMP:?RUNNER_TEMP must be set}/promotion-record"
state="${work}/state"
plan="${work}/plan.json"
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
  local merge="$1" kind name message
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
  jq -r '[.promotion_tag, .prereg_tag] | map(select(. != null) | .name) | .[]' "$plan"
}

prepare() {
  local merge="$1" applied="${work}/applied.json" base head
  rm -f "$state"
  fetch
  base=$(git rev-parse --verify "origin/main^{commit}")
  git checkout --quiet --detach "$base"
  uv run --locked fedcourts promotion-record --merge "$merge" "${refs[@]}" >"$plan"
  tag_locally "$merge"
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
  # Written last: a state file exists only once every step above succeeded.
  printf 'base=%s\nhead=%s\n' "$base" "$head" >"$state"
}

validate() {
  local base head
  [ -f "$state" ] || { echo "::error::no prepared record to push"; return 1; }
  base=$(sed -n 's/^base=//p' "$state")
  head=$(sed -n 's/^head=//p' "$state")
  if ! [[ "$base" =~ ^[0-9a-f]{40}$ ]]; then
    echo "::error::the prepared base is not a commit SHA"
    return 1
  fi
  if [ -n "$head" ]; then
    if ! [[ "$head" =~ ^[0-9a-f]{40}$ ]]; then
      echo "::error::the prepared record commit is not a commit SHA"
      return 1
    fi
    if [ "$(git rev-list --parents -n 1 "$head")" != "${head} ${base}" ]; then
      echo "::error::the prepared record commit's only parent is not the base"
      return 1
    fi
  fi
  {
    echo "base=${base}"
    echo "head=${head}"
    echo "plan=${plan}"
  } >>"${GITHUB_OUTPUT:-/dev/null}"
  echo "validated base ${base}, record commit ${head:-none}"
}

git_push() {
  # The write token reaches git as a header for this one command — after any
  # ambient header is blanked, with hooks off — never into a URL or a config
  # file a later command could read.
  local header
  header="AUTHORIZATION: basic $(printf 'x-access-token:%s' "${WRITE_TOKEN:?WRITE_TOKEN must be set}" | base64 -w0)"
  git -c core.hooksPath=/dev/null -c http.extraHeader= \
    -c "http.https://github.com/.extraheader=${header}" push --no-verify "$@"
}

push() {
  local base="${BASE:?BASE must be set}" head="${HEAD_SHA:-}" name log
  while IFS= read -r name; do
    # A plain push of a tag never replaces one: an existing remote tag on
    # another object is rejected ("already exists"), and the record ruleset
    # blocks the update besides. That rejection is final — an operator
    # investigates; nothing retries past it.
    git_push --quiet "$repo_url" "refs/tags/${name}:refs/tags/${name}"
    echo "pushed ${name}"
  done < <(planned_tags)
  if [ -z "$head" ]; then
    echo "no record commit to push"
    return 0
  fi
  log=$(mktemp)
  if git_push --force-with-lease="refs/heads/main:${base}" "$repo_url" \
    "${head}:refs/heads/main" >"$log" 2>&1; then
    cat "$log"
    echo "pushed the record commit ${head} onto ${base}"
    return 0
  fi
  cat "$log"
  if grep -qiE 'stale info|non-fast-forward|fetch first|\[rejected\]' "$log"; then
    echo "::warning::main advanced past ${base}; the record commit was not pushed"
    return 3
  fi
  echo "::error::the record commit push failed for a reason other than main advancing"
  return 1
}

case "${1:-}" in
  prepare) prepare "${2:?the merge sha}" ;;
  validate) validate ;;
  push) push ;;
  *)
    echo "usage: write.sh prepare <merge> | validate | push" >&2
    exit 2
    ;;
esac
