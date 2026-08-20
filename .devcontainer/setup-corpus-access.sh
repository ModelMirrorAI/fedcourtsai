#!/usr/bin/env bash
# Configure read-only corpus access from user-scoped Codespaces secrets.
#
# Two credential flows share this hook, and either (or neither) may be present:
#   - Maintainer: IAM Identity Center secrets -> ~/.aws/config profiles whose
#     short-lived SSO session assumes the read-only corpus role.
#   - Contributor: a dedicated read-only IAM user's key pair, which boto3 reads
#     straight from the environment -- nothing to write for AWS.
# The corpus remote's URL is never committed (see SECURITY.md): it rides in
# out of band as an environment variable, exactly as the workflows supply it.
# Absent secrets, the hook notes it and succeeds anyway, because the offline
# fixture loop and the full gate need no remote at all.
#
# Shell state goes to one generated file, ~/.fedcourts-env.sh, sourced from
# .bashrc by a single guarded line. Regenerating that file wholesale is what
# makes reruns idempotent, so no per-line grep guards are needed, and it gives
# the post-start session check one thing to source.
#
# No corpus bytes are transferred here. Codespaces runs on Azure, so a full
# pull is cross-cloud S3 internet egress — pulling is a deliberate command
# (`uv run fedcourts corpus-pull`), never part of container creation; quick
# lookups use the ranged backend
# (`fedcourts query --corpus-backend ranged ...`) with no pull at all.
set -euo pipefail

# Anchor on the script's location rather than the caller's cwd.
cd "$(dirname "${BASH_SOURCE[0]}")/.."

env_file="${HOME}/.fedcourts-env.sh"
: > "${env_file}"

# The application accepts the bare workflow variable names as aliases of the
# FEDCOURTS_-prefixed ones (see fedcourtsai.config); the DVC_* pair is the
# legacy spelling, honored until the Codespaces secret is renamed.
remote_url="${CORPUS_REMOTE_URL:-${FEDCOURTS_CORPUS_REMOTE_URL:-${DVC_REMOTE_URL:-${FEDCOURTS_DVC_REMOTE_URL:-}}}}"

if [[ -z "${AWS_SSO_START_URL:-}" && -z "${AWS_ACCESS_KEY_ID:-}" && -z "${remote_url}" ]]; then
  echo "Corpus remote access not configured (user-scoped Codespaces secrets absent); offline fixture work is unaffected."
  exit 0
fi

if [[ -n "${AWS_SSO_START_URL:-}" ]]; then
  # Maintainer flow: an SSO session (short-lived tokens) whose fedcourts-ro
  # profile assumes the read-only corpus role.
  mkdir -p "${HOME}/.aws"
  cat > "${HOME}/.aws/config" <<EOF
[sso-session modelmirror]
sso_start_url = ${AWS_SSO_START_URL}
sso_region = ${AWS_REGION}
sso_registration_scopes = sso:account:access

[profile fedcourts-sso]
sso_session = modelmirror
sso_account_id = ${AWS_SSO_ACCOUNT_ID}
sso_role_name = ${AWS_SSO_ROLE_NAME}

[profile fedcourts-ro]
role_arn = ${AWS_RO_ROLE_ARN}
source_profile = fedcourts-sso
region = ${AWS_REGION}
EOF
  # remoteEnv is static JSON and cannot depend on which secrets exist, so
  # profile selection happens here instead: SSO shells need AWS_PROFILE to
  # resolve the assumed role, while a dangling profile would break the
  # static-key flow (boto3 fails on a profile no config file defines).
  cat >> "${env_file}" <<'EOF'
export AWS_PROFILE=fedcourts-ro
EOF
  # A convenience name for interactive terminals; the committed script is the
  # definition, and the one spelling that also resolves where .bashrc
  # functions are not inherited (a coding agent's per-call shells).
  printf 'corpus-login() {\n  %q "$@"\n}\n' "$(pwd)/scripts/corpus-login" >> "${env_file}"
  echo "AWS SSO profiles written (fedcourts-sso -> fedcourts-ro); run scripts/corpus-login when the session expires."
elif [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
  # Contributor flow: nothing to configure — boto3 picks the key pair up from
  # the environment, and no profile must be set (see the remoteEnv note above).
  echo "Read-only corpus credentials found in the environment (IAM-user key pair)."
fi

# The remote's URL is independent of which credential flow is present. The
# tooling reads it from the environment (any accepted alias), so all that is
# needed is the preferred name in every shell; the SSO flow's AWS_PROFILE
# export above already routes boto3 through the assumed-role profile.
if [[ -n "${remote_url}" ]]; then
  printf 'export CORPUS_REMOTE_URL=%q\n' "${remote_url}" >> "${env_file}"
  echo "Corpus remote URL exported as CORPUS_REMOTE_URL (read-only). Ranged queries work now; a full pull stays deliberate: uv run fedcourts corpus-pull"
fi

# The staging pair's URLs need no translation — the STAGING_* secrets are
# already the names scripts/corpus-env reads — so presence is just worth a
# pointer to the switcher, and a half-configured pair a warning (the switcher
# refuses one URL without the other).
if [[ -n "${STAGING_CORPUS_REMOTE_URL:-}" && -n "${STAGING_CASESTORE_URL:-}" ]]; then
  if [[ -n "${STAGING_CORPUS_POINTER:-}" ]]; then
    echo "Staging corpus pair configured (read-only, index included): scripts/corpus-env staging <cmd>, or eval \"\$(scripts/corpus-env staging)\" for the shell."
  else
    echo "Staging corpus pair configured (read-only, content store only): index reads need STAGING_CORPUS_POINTER (the seed run's published pointer JSON) or they fail on the committed production digest."
  fi
elif [[ -n "${STAGING_CORPUS_REMOTE_URL:-}${STAGING_CASESTORE_URL:-}" ]]; then
  echo "Staging corpus pair half-configured: set both STAGING_CORPUS_REMOTE_URL and STAGING_CASESTORE_URL (scripts/corpus-env refuses one without the other)."
fi

source_line='if [ -f "$HOME/.fedcourts-env.sh" ]; then . "$HOME/.fedcourts-env.sh"; fi'
if ! grep -qxF "${source_line}" "${HOME}/.bashrc" 2>/dev/null; then
  printf '%s\n' "${source_line}" >> "${HOME}/.bashrc"
fi
