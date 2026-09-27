# Retrieval log

## Local sources beyond the provisioned case inputs

- Read the task contract and applicable schemas; inspected `fedcourtsai.paths` and `fedcourtsai.serialize` only to resolve output paths and serialize authorized artifacts.
- Read `metrics/statpack.md`, especially the interim-docket counts, ask totals, escalation totals, and coverage caveats. Inspected `metrics/statpack.json` top-level metadata for a build timestamp; none was established. Computed the eligible pooled rate locally as `(17 + 14) / (226 + 70)`.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `96ebdd342 2026-09-26T12:03:37Z`. This dates the committed artifact, not the underlying corpus refresh.
- Ran `uv run fedcourts paths --court scotus --docket 9526000370 --event evt-motion-disposition --role predictor`. The initial invocation failed because the default uv cache was read-only; it succeeded with a writable temporary cache. No outcome file was opened.
- No `fedcourts query`, `open-events`, or live corpus lookup was used; no ranged-corpus transfer line was emitted.

## General legal authorities only

1. Web search batch: `site.supremecourt.gov opinions Nken Holder 556 418 stay` and `site.supremecourt.gov opinions 2025 Trump CASA equitable relief founding`. No usable results were returned.
2. Web open: Supreme Court PDF path `/opinions/24pdf/24a884_8n59.pdf`. No usable text was returned; it did not supply authority or case facts for the forecast.
3. CourtListener MCP `search`, type `o`, citation `556 U.S. 418`, one result requested, with case metadata fields. Returned Nken v. Holder, decided April 22, 2009, opinion path `/opinion/145884/nken-v-holder/`. Some requested fields were unavailable; the case metadata was usable.
4. CourtListener MCP `search_document`, opinion ID `145884`, query `most critical`, context 500 characters. Returned one passage identifying likelihood of success and irreparable injury as the most important stay factors, and rejecting a merely negligible chance of success.

No search requested Thornell/Jensen's outcome, live docket, later filings, or subsequent history. No outcome-revealing material was surfaced. The supplied lower-court decisions predate this application and were read as part of its pre-decision appendix.
