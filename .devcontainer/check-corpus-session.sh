#!/usr/bin/env bash
# Report corpus credential state on every container start. Deliberately
# advisory: no `set -e`, always exits 0. A codespace with no corpus access is a
# valid state (the offline fixture loop and the full gate need no remote), and
# a failed start would be a far worse outcome than a stale banner.
set -uo pipefail

env_file="${HOME}/.fedcourts-env.sh"
[[ -f "${env_file}" ]] || exit 0
# shellcheck source=/dev/null
. "${env_file}"

# Only the SSO flow expires; the contributor key pair is static.
[[ -n "${AWS_PROFILE:-}" ]] || exit 0

if aws sts get-caller-identity >/dev/null 2>&1; then
  echo "Corpus credentials live (${AWS_PROFILE})."
else
  echo "AWS SSO session expired or absent — run: corpus-login"
fi
exit 0
