# Retrieval log

## Provisioned material

Read the assigned event definition and case-level context, June 2, 2026 snapshot, document manifest, QP extract, petition excerpts including the opening questions and portions of the included majority opinion, and opposition excerpts. The malformed QP extract was replaced analytically by the questions on petition page I, not edited on disk.

## Additional sources

1. Local `metrics/statpack.md`: modern-cert disposition counts, paid-segment CVSG and relist cuts, and the sal-v4 per-Term reached-band table. Local `metrics/statpack.json`: matching exact high-band rates and weighted denominators for 2017-2024. An in-memory calculation produced 314/898 = 0.34966592427616927. No individual case rows or outcome records were read.
2. `git log -1 --format='%cI %h' -- metrics/statpack.md metrics/statpack.json` returned a September 14, 2026 commit timestamp. This dates the committed pack, not the underlying corpus's newest pull.
3. Web search: `site.supremecourt.gov opinions 2023 Macquarie Moab 22-1165 Section 11 pure omissions`. Search snippets identified the 2024 precedent and brief materials. An unrequested search-index snippet about the present petition reported only the June 1, 2026 CVSG already in the baseline; it was not opened and no outcome was disclosed. Other indexed brief snippets were not used as evidence.
4. Opened the official Supreme Court opinion at `https://www.supremecourt.gov/opinions/23pdf/22-1165_10n2.pdf`: Macquarie Infrastructure Corp. v. Moab Partners, L.P., decided April 12, 2024. Used the distinction between pure omissions and half-truths, the separate Section 11 required-disclosure language, and the opinion's express limitation of its holding. This is general preexisting legal context, not this petition's subsequent history.

No CourtListener MCP calls, `fedcourts query`, or `fedcourts open-events` calls were made. Consequently there are no ranged-corpus transfer lines. No current docket, present-case disposition, other predictor output, or QP-topic measurement artifact was consulted.

Final source verification repeated the same precedent search once and reopened the same official PDF twice, including its final page and footnote 2. Those repeat calls introduced no additional sources or present-case outcome information.

## Local contract tooling

Read the prompt and output schemas. Resolved paths using `fedcourts paths` and `fedcourtsai.paths.CasePaths`, and checked the canonical case identifier with `fedcourtsai.ids.case_id`. The initial `uv run` path command failed because its default cache directory was read-only; the same command succeeded with a writable temporary cache. These were local setup operations, not corpus retrieval.

All three JSON files passed their repository Pydantic models. The full `fedcourts validate data` run reported 30,328 valid artifacts and 42,046 consistent references.
