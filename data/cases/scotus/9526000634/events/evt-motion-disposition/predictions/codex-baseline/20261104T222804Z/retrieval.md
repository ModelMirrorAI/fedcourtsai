# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-11-04.json`, `record/documents/documents.json`, and the full `record/documents/application.txt`. No other cell's output, evaluator outcome, current case docket, or subsequent history was consulted.

## Repository context and commands

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; checked applicable descendant instruction-file locations.
- Attempted `uv run fedcourts paths --court scotus --docket 9526000634 --event evt-motion-disposition --role predictor`. It failed before execution because the default uv cache was read-only.
- Retried with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9526000634 --event evt-motion-disposition --role predictor`. It returned the case id, corpus path, and event path, and explicitly withheld the evaluator-only outcome path. No outcome file was opened.
- Read the interim section of `metrics/statpack.md` and the corresponding keys and per-Term rows in `metrics/statpack.json`. Used jq to pool Terms 2016–2025: finer_granted 0, finer_resolved 0, finer_unread 1,366, substantive 1,380, unparsed 16. No `fedcourts query` or `open-events` corpus retrieval was attempted; consequently there was no ranged-corpus-reads stderr line.

## External retrieval

1. One `web.run` call attempted two general-precedent searches: `site.supremecourt.gov opinions Bucklew Precythe 2019 isolated mishaps protocol Baze` and `site.supremecourt.gov Hill McDonough 547 573 584 stay execution not matter of right`. The tool returned no visible results or source text. No factual proposition relies on this attempt.
2. CourtListener MCP `search`, type `o`, citation `547 U.S. 573`, two results requested. Returned *Hill v. McDonough*, decided June 12, 2006, opinion 145647, plus an irrelevant citation-token match, *United States v. Hurwitz*. Only Hill was used.
3. CourtListener MCP `search_document`, opinion 145647, literal query `stay`, context 650 characters. Returned the discussion that section 1983 litigation does not automatically entitle an applicant to a stay, the merits requirement, and equitable timing considerations. Some long tool excerpts were display-truncated; the relevant principles were visible.
4. CourtListener MCP `search`, type `o`, court `scotus`, case_name `Baze v. Rees`, one result requested. Returned the April 16, 2008 decision, 553 U.S. 35, with its lead and separate opinion identifiers. Selected lead opinion 9435238 rather than a dissent.
5. CourtListener MCP `search_document`, opinion 9435238, literal query `isolated`, context 450 characters. Returned the plurality's distinction between an isolated mishap and substantial risk of serious harm.
6. CourtListener MCP `search_document`, opinion 9435238, literal query `stay of execution`, context 500 characters. Returned a background reference and the plurality's requirement of a demonstrated severe-pain risk substantial relative to known and available alternatives.

All external substantive material used concerns general precedents decided well before this application. No search sought Guardado's disposition, the linked petition's disposition, or subsequent events in either proceeding. No own-case outcome surfaced.

## Validation

The required cell validation is run with a writable uv cache and environment synchronization disabled to use the already provisioned tools: `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts validate data --cell data/cases/scotus/9526000634/events/evt-motion-disposition/predictions/codex-baseline/20261104T222804Z`. Validation is local and is not a case-outcome retrieval.
