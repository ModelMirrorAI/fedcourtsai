#!/usr/bin/env bash
# Install the Claude Code CLI via its native installer, as the container user.
#
# The native layout keeps each version in its own directory under
# ~/.local/share/claude and flips a ~/.local/bin/claude symlink to switch, so
# an auto-update interrupted by a container stop leaves the previous binary in
# place instead of no binary at all — a guarantee an in-place install into a
# shared npm prefix cannot make. It also needs no root and no ownership
# repair afterwards.
#
# Trust posture: the installer script and the binaries it fetches come from
# Anthropic over TLS, the same trust root a registry install of the CLI relies
# on, and the CLI's own auto-updater keeps the version current either way, so
# pinning here would not hold past first launch. What this costs relative to a
# lockfile-governed feature is the tracked-diff property of the *build input*:
# the fetch below resolves latest at create time and no committed file records
# it — accepted, because the running binary floats identically in both designs.
#
# Deliberately advisory, like the corpus session check: no `set -e`, always
# exits 0. A container without Claude Code is a valid state, and a failed
# create is a far worse outcome than a missing CLI — the commands below are
# safe to re-run by hand in a terminal.
set -uo pipefail

# Download to a file, then execute: `-f` cannot stop a body that already began
# flowing, so piping to bash would run a truncated script on a dropped
# connection. The proto flags keep a redirect from leaving HTTPS.
tmp="$(mktemp)" || exit 0
if curl -fsSL --proto '=https' --proto-redir '=https' --tlsv1.2 \
    https://claude.ai/install.sh -o "${tmp}"; then
  if bash "${tmp}"; then
    echo "Claude Code installed under \$HOME/.local (native layout)."
  else
    echo "Claude Code install failed — re-run by hand:" \
      "curl -fsSL https://claude.ai/install.sh | bash"
  fi
else
  echo "Claude Code installer download failed — re-run by hand:" \
    "curl -fsSL https://claude.ai/install.sh | bash"
fi
rm -f "${tmp}"
exit 0
