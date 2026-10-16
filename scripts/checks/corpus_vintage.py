"""Report the pulled corpus's vintage to the corpus-check summary.

The smallest corpus check, and the template for a real one. Declared in a pull
request's description as

    ```corpus-check
    uv run python scripts/checks/corpus_vintage.py
    ```

it runs `fedcourts corpus-info` over the corpus the lane pulled and appends what
it prints — the blob's row count and its freshness line — to the file named by
`CHECK_SUMMARY`, the only output the lane posts back to the PR. A real check
does the same with its own figure: compute it, write what it means to report
to `CHECK_SUMMARY`, and exit non-zero when the check itself failed. Write
counts and identifiers, never stored snapshot text: the summary is posted
publicly (docs/corpus-check.md).

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
