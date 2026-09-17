# Retrieval and source key

All retrieval occurred September 17, 2026. This is a forward cell. No search sought this petition's disposition, subsequent history, or decision coverage.

## Provisioned inputs

- **S1:** `record/snapshots/2026-09-17.json`, including dated proceedings and fixed filing URLs. Read the snapshot's case and filing information, not a live docket page.
- **S2:** `record/context.json` and `events/evt-petition-disposition/event.yaml`.
- **S3:** `record/documents/documents.json`, `questions-presented.txt`, and selected sections of `petition.txt`, especially printed pp. i, 1, 6-8. Petition and QP text were fetched July 18, 2026 according to the manifest; no BIO or reply text was provisioned.

## Committed aggregate context

- **S4:** `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit sections; paid-segment relist and CVSG cuts; `sal-v4` per-Term band table. Read `metrics/statpack.json` top-level keys to check for freshness metadata. Computed the n-weighted mean of displayed baseline reached percentages for all eight displayed Terms 2017-2024 using a local Python calculation: n=11,580, approximately 0.0512025. No individual corpus cases were read.
- Ran `uv run fedcourts corpus-info` with a writable temporary uv cache. It failed because the service backend has no client-side corpus connection. No freshness stamp or transfer line was returned. No `fedcourts query` or `open-events` calls were made, so there are no ranged-read stderr lines to report.

## Direct pre-decision filing retrieval

The URLs below came exclusively from S1. PDFs were fetched into memory with Python `urllib.request` and text-extracted with installed `pypdf`; no extra input copies were written. Page selections were based on relevant procedural and vehicle terms. Some long terminal results were truncated, so the forecast relies only on the excerpts actually shown, not an assertion that every page was reviewed.

1. **S5, State BIO**, filed August 24, 2026, 33 PDF pages. Attempted `web.run open` on its exact URL twice; both returned empty output. One subsequent direct official-site fetch succeeded. Consulted printed pp. 1-2 and 22-24, among selected excerpts, for asserted absence of a split, preservation, immunity, and the related Curtis denial.
   `https://www.supremecourt.gov/DocketPDF/25/25-1327/419919/20260824133500295_FergusonBIO.pdf`
2. **S6, Shriners BIO**, filed August 24, 2026, 30 PDF pages. One direct official-site fetch. Consulted introduction and vehicle excerpts, especially printed pp. 1-2 and 18-20. The introduction reports Curtis's June 1, 2026 denial; this is a different case and predates this baseline. Its state-action and immunity positions were treated as advocacy.
   `https://www.supremecourt.gov/DocketPDF/25/25-1327/419907/20260824125547235_260814a%20BIO%20for%20efiling.pdf`
3. **S7, petitioners' reply**, submitted September 14, 2026, 18 PDF pages. One direct official-site fetch. Consulted the contents, argument excerpts, and printed pp. 10-12, including the response to forfeiture, state-action, and immunity arguments, and the consolidation request. Extraction emitted a missing-fontTools warning, but the relied-on passages were readable; no dependency was installed.
   `https://www.supremecourt.gov/DocketPDF/25/25-1327/424204/20260914221929644_Roberts%20Reply.pdf`

No general web search, CourtListener MCP lookup, direct CourtListener REST request, or related-case docket search was made. The two empty web opens and three successful direct official-PDF requests are the complete external retrieval list. The reported Curtis denial was used as legitimate related-case context and is flagged transparently; no disposition of Roberts was surfaced.

## Contract and validation tooling

Read `AGENTS.md`, `.github/prompts/predict.md`, the three output schemas, and path/serialization helper definitions. Ran `fedcourts paths` for the supplied identifiers; the first invocation failed because the default uv cache was read-only, and retry with a temporary cache succeeded. The output directory was resolved with `CasePaths(...).event(...).prediction_dir(...)`. These were operational reads, not additional legal evidence.
