#!/usr/bin/env bash
# Give the container user ownership of the globally installed Claude Code
# package, so the CLI's in-place auto-update succeeds instead of failing with
# EACCES.
#
# The claude-code feature installs into the shared nvm prefix as root, which
# leaves the `@anthropic-ai` scope directory owned by root without group write.
# Only the owner is reset — the group comes from the prefix's setgid bit and
# must stay as the node feature set it.
#
# Deliberately advisory, like the corpus session check: no `set -e`, always
# exits 0. A container whose Claude Code lives outside this prefix, or which
# has none at all, is a valid state, and a failed create would be a far worse
# outcome than a package that cannot self-update.
set -uo pipefail

# A project-level `.npmrc` can steer this value: npm refuses to install against
# such a prefix but still prints it. Require an absolute path rather than
# trusting whatever comes back.
prefix="$(npm config get prefix)"
[[ -n "${prefix}" && "${prefix}" == /* ]] || exit 0

scope="${prefix}/lib/node_modules/@anthropic-ai"
[[ -d "${scope}" ]] || exit 0

if ! sudo chown -R "$(id -un)" "${scope}"; then
  echo "Could not take ownership of ${scope} — Claude Code auto-update will fail."
fi
exit 0
