#!/usr/bin/env bash
# Install the Claude Code CLI via its native installer, as the container user.
#
# The native layout keeps each version as its own executable under
# ~/.local/share/claude/versions/ and flips a ~/.local/bin/claude symlink to
# switch, so an auto-update interrupted by a container stop leaves the
# previous binary in place instead of no binary at all — a guarantee an
# in-place install into a shared npm prefix cannot make. It also needs no
# root and no ownership repair afterwards.
#
# Trust posture: the installer script and the binaries it fetches come from
# the same publisher, over TLS, and the CLI's own auto-updater keeps the
# version current in any install design, so a pin here would not hold past
# first launch. What this costs relative to a lockfile-governed feature is
# the tracked-diff property of the *build input*: the fetch below resolves
# latest at create time and no committed file records it — accepted, because
# the running binary floats identically either way.
#
# Deliberately advisory, like the corpus session check: no `set -e`, always
# exits 0. A container without Claude Code is a valid state, and a failed
# create is a far worse outcome than a missing CLI — on any failure below,
# re-run this same script by hand in a terminal.
set -uo pipefail

retry_hint="re-run by hand: bash .devcontainer/install-claude.sh"

# Download to a file, then execute: `-f` cannot stop a body that already began
# flowing, so piping to bash would run a truncated script on a dropped
# connection. The proto flags keep a redirect from leaving HTTPS, and
# --tlsv1.2 floors the protocol version.
if ! tmp="$(mktemp)"; then
  echo "Claude Code install skipped (mktemp failed) — ${retry_hint}"
  exit 0
fi
if curl -fsSL --proto '=https' --proto-redir '=https' --tlsv1.2 \
    https://claude.ai/install.sh -o "${tmp}"; then
  if bash "${tmp}"; then
    echo "Claude Code installed under \$HOME/.local (native layout)."
  else
    echo "Claude Code install failed — ${retry_hint}"
  fi
else
  echo "Claude Code installer download failed — ${retry_hint}"
fi
rm -f "${tmp}"
exit 0
