#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${AWS_SSO_START_URL:-}" ]]; then
  echo "AWS Codespaces secrets not set; skipping AWS profile setup."
  exit 0
fi

mkdir -p ~/.aws
cat > ~/.aws/config <<EOF
[sso-session modelmirror]
sso_start_url = ${AWS_SSO_START_URL}
sso_region = ${AWS_REGION:-us-east-1}
sso_registration_scopes = sso:account:access

[profile fedcourts-sso]
sso_session = modelmirror
sso_account_id = ${AWS_SSO_ACCOUNT_ID}
sso_role_name = ${AWS_SSO_ROLE_NAME}

[profile fedcourts-ro]
role_arn = ${AWS_RO_ROLE_ARN}
source_profile = fedcourts-sso
region = ${AWS_REGION:-us-east-1}
EOF

if [[ -n "${FEDCOURTS_DVC_REMOTE_URL:-}" ]] && [[ ! -f .dvc/config.local ]]; then
  uv run dvc remote add --local -d storage "${FEDCOURTS_DVC_REMOTE_URL}"
  uv run dvc remote modify --local storage profile fedcourts-ro
fi
