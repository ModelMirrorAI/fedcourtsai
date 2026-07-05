#!/usr/bin/env bash
# Configure read-only corpus access from user-scoped Codespaces secrets.
#
# Two credential flows share this hook, and either (or neither) may be present:
#   - Maintainer: IAM Identity Center secrets -> ~/.aws/config profiles whose
#     short-lived SSO session assumes the read-only corpus role.
#   - Contributor: a dedicated read-only IAM user's key pair, which boto3 reads
#     straight from the environment -- nothing to write for AWS.
# The DVC remote's URL is never committed (see SECURITY.md): every environment
# writes it out of band into the gitignored .dvc/config.local, exactly as the
# workflows do before any push/pull. Absent secrets, the hook notes it and
# succeeds anyway, because the offline fixture loop and the full gate need no
# remote at all.
#
# No corpus bytes are transferred here. Codespaces runs on Azure, so a full
# `dvc pull` is cross-cloud S3 internet egress — pulling is a deliberate
# command (`uv run dvc pull corpus/corpus.db.dvc`), never part of container
# creation; quick lookups use the ranged backend
# (`fedcourts query --corpus-backend ranged ...`) with no pull at all.
set -euo pipefail

# .dvc/ lives at the repo root, and the dvc CLI comes from the synced
# environment (`uv sync` runs in onCreateCommand, before this postCreate hook),
# so anchor on the script's location rather than the caller's cwd.
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# The application accepts the bare workflow variable name as an alias of the
# FEDCOURTS_-prefixed one (see fedcourtsai.config), so honor either here too.
remote_url="${DVC_REMOTE_URL:-${FEDCOURTS_DVC_REMOTE_URL:-}}"

if [[ -z "${AWS_SSO_START_URL:-}" && -z "${AWS_ACCESS_KEY_ID:-}" && -z "${remote_url}" ]]; then
  echo "Corpus remote access not configured (user-scoped Codespaces secrets absent); offline fixture work is unaffected."
  exit 0
fi

sso_configured=false
if [[ -n "${AWS_SSO_START_URL:-}" ]]; then
  # Maintainer flow: an SSO session (short-lived tokens; refresh with
  # `aws sso login --profile fedcourts-sso`) whose fedcourts-ro profile
  # assumes the read-only corpus role.
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
  # static-key flow (boto3 fails on a profile no config file defines). The
  # grep guard keeps container rebuilds from stacking duplicate lines.
  if ! grep -qx "export AWS_PROFILE=fedcourts-ro" "${HOME}/.bashrc" 2>/dev/null; then
    echo "export AWS_PROFILE=fedcourts-ro" >> "${HOME}/.bashrc"
  fi
  sso_configured=true
  echo "AWS SSO profiles written (fedcourts-sso -> fedcourts-ro); run 'aws sso login --profile fedcourts-sso' when the session expires."
elif [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
  # Contributor flow: nothing to configure — boto3 picks the key pair up from
  # the environment, and no profile must be set (see the remoteEnv note above).
  echo "Read-only corpus credentials found in the environment (IAM-user key pair)."
fi

# The remote's URL is independent of which credential flow is present.
if [[ -n "${remote_url}" ]]; then
  # -f keeps this idempotent across container rebuilds: it overwrites the
  # remote entry already present in .dvc/config.local instead of failing on it.
  uv run dvc remote add --local -d -f storage "${remote_url}"
  if [[ "${sso_configured}" == true ]]; then
    # dvc's boto3 must resolve the assumed-role profile, not ambient env creds.
    uv run dvc remote modify --local storage profile fedcourts-ro
  fi
  echo "Corpus remote configured in .dvc/config.local (read-only). Ranged queries work now; a full pull stays deliberate: uv run dvc pull corpus/corpus.db.dvc"
fi
