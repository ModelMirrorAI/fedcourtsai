# Retrieval log

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-10-14.json`, and the document manifest. Read the questions-presented text and petition's reasons for review; examined the relevant appellate and district-court portions of the supplied appendix, especially the due-weight analysis and preservation footnote. These were local provisioned inputs, not live retrieval.

## Additional local context

- Read `metrics/statpack.md`: modern discretionary-cert section, circuit cut, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. Inspected the matching entries in `metrics/statpack.json` and calculated the baseline pool for all displayed prior Terms 2017–2025: 643 grant equivalents / 12,877 weighted resolved petitions.
- Ran `git log -1 --format='%cI %h' -- metrics/statpack.md` for artifact provenance: October 13, 2026 at 19:17:46 UTC, commit `cf9ae960e`. No case history was retrieved through git.
- Read task instructions and the prediction/tooling schemas. Ran the role-scoped `fedcourts paths` command. The first invocation failed because the default uv cache directory was read-only; retrying with a writable temporary cache succeeded.

## Web attempts

The following general legal-context calls returned no usable content, result snippets, or source text. Nothing from them informed the forecast:

1. Search: `site.supremecourt.gov Rule 10 considerations governing review certiorari`.
2. Search, in the same call: `site.govinfo.gov 20 USC 1415 additional evidence request party`.
3. Open attempted: the Supreme Court's `filingandrules/2023RulesoftheCourt.pdf`.
4. Find attempted in that PDF: `A petition for a writ of certiorari is rarely granted`.

No case-specific web search was made. No disposition, subsequent history, other predictor output, or outcome-labeled topic artifact was consulted.

## Corpus and CourtListener

No `fedcourts query` or `open-events` calls; therefore no ranged-corpus transfer lines. No CourtListener MCP calls. No live-corpus freshness assertion is made.
