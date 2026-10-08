# Retrieval record

## Provisioned and stable local materials

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flag schemas for the output contract.
- Read this event's `event.yaml` and this case's `record/context.json`, `record/snapshots/2026-10-08.json`, and `record/documents/documents.json`.
- Read the questions-presented extract, substantive petition sections, and selected included district-court opinion passages. The petition manifest reports truncation; I did not treat the available text as the entire 219-page filing.
- Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and the sal-v4 per-Term baseline reached rates. A local arithmetic calculation pooled the 2017–2025 displayed baseline rows: denominator 12,720, approximate rate 5.0109% using rounded published percentages. No live corpus was queried or pulled.

## External retrieval

1. Web search: `site.supremecourt.gov Rule 11 petition writ certiorari before judgment imperative public importance`. The tool returned no usable content.
2. Web open attempt: official Supreme Court `ctrules/2023RulesoftheCourt.pdf`. The tool returned no usable content. No rules PDF was read through this attempt.
3. CourtListener MCP `search`, type `o`, query `citation:("534 F.3d 1245")`, one result. Returned Colorado Christian University v. Weaver, decided July 23, 2008; opinion 171011.
4. CourtListener MCP `search_document`, opinion 171011, literal phrase `two features`, context 1,700 characters per side. Read the passage at reporter page 1256 distinguishing Locke on discrimination among religions and intrusive governmental religious judgments. This checked the general precedent only; it did not retrieve this petition or Hall's disposition.

## Operational commands

- `uv run fedcourts paths --court scotus --docket 9026000240 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded.
- No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines to report.
- No current docket, subsequent history, other predictor output, realized outcome, or QP-topic artifact was consulted.
