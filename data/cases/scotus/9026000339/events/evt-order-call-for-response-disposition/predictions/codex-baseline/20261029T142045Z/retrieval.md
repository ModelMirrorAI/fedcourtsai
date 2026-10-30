# Retrieval account

## Provisioned and committed local material

Read AGENTS.md, .github/prompts/predict.md, the prediction/tooling/flags schemas, the cell's event, context, snapshot, document manifest, questions presented, petition passages, party letter, and appendix passages. A read-only assistant additionally reviewed the provisioned petition and appendix; no independent external retrieval was delegated. Read metrics/statpack.md and metrics/statpack.json, and computed the sal-v4 baseline reached pool over OT2017-2025: 660 / 12,913 = 5.1111%. A separate read-only reviewer verified this population choice, arithmetic, and claim consistency and reported no blockers. These local inputs are not live docket lookups.

Read the local path and serialization helpers and reviewer checklist for output handling and review. The initial `uv run fedcourts paths --court scotus --docket 9026000339 --event evt-order-call-for-response-disposition --role predictor` failed because uv's default cache location was read-only. Repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This was an environment/cache failure, not unavailable case evidence. All subsequent uv invocations used that temporary cache override.

## Corpus calls

1. `uv run fedcourts query --help` — succeeded; read the structured-filter interface before querying.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4` — succeeded. Returned 25-1103 (U.S. DOGE Service), 25-7026 (Berry), 25-1343 (Blanche), and 25-1131 (Missionaries of Saint John the Baptist). They had distribution counts 2, 5, 2, 2 and no opinion bodies. The displayed combined command output was truncated, so its initial transfer-count line was not available to transcribe; I do not infer that count from the repeat below.
3. Repeated that exact query, projecting the same rows to identifiers, grant dates, distribution counts, and opinion availability to avoid output truncation — same four results. Exact stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`. This is the warm-cache repeat, not a claim that the initial query cost zero reads.
4. `uv run fedcourts corpus-info --help` — succeeded; checked how corpus vintage is reported.
5. `uv run fedcourts corpus-info` — failed: `ValueError: the service backend has no client-side connection; fedcourts query and open-events forward to the corpus query service`. No corpus vintage was obtained. No corpus pull, mutation, stats scan, or unsupported backend workaround was attempted.

The returned grants are examples selected on disposition, not comparable jurisdiction cases or an empirical grant-rate denominator. No query targeted this petition or its outcome.

## CourtListener MCP

One `search` call: `type="o", citation="348 F.3d 244", num_results=3`, seeking the preexisting Tango Music opinion. Failed with HTTP 429, daily limit 1,400/day, approximately 12,186 seconds until availability. No opinion text or case results were returned. No direct CourtListener REST fallback was attempted.

## Web attempts

All four web tool invocations returned no usable displayed results, source references, or page content. None contributed evidence:

1. Search batch: `"Tango Music" "348 F.3d 244" diversity`; `site.uscode.house.gov 28 1332 citizens additional parties`.
2. Attempted open: `https://caselaw.findlaw.com/court/us-7th-circuit/1482106.html`.
3. Search batch: `"Tango Music" "2003" "additional parties"`; `site.uscode.house.gov "1332" "additional parties"`.
4. Attempted open: `https://caselaw.findlaw.com/court/us-7th-circuit/1330358.html`.

These four invocations contained four search queries and two attempted page opens. The page addresses were attempted locations, not verified citations; no page identity was established and neither was relied on. No search or page open sought FS Medical Supplies' disposition, later history, or current docket.
