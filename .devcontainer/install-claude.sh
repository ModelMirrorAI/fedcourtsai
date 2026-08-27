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
# on; the CLI's own auto-updater keeps the version current either way, so
# pinning here would not hold past first launch.
#
# Deliberately advisory, like the corpus session check: no `set -e`, always
# exits 0. A container without Claude Code is a valid state, and a failed
# create is a far worse outcome than a missing CLI — the command below is safe
# to re-run by hand in a terminal.
set -uo pipefail

if curl -fsSL https://claude.ai/install.sh | bash; then
  echo "Claude Code installed under \$HOME/.local (native layout)."
else
  echo "Claude Code install failed — re-run by hand:" \
    "curl -fsSL https://claude.ai/install.sh | bash"
fi
exit 0
