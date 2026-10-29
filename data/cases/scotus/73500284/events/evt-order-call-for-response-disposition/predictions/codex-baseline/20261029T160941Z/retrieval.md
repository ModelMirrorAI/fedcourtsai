# Retrieval record

## Baseline and local reference material

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling schemas, the event definition, the provisioned July 27 snapshot, document manifest, QP, selected petition passages, appendix appellate-opinion passages, and `record/context.json`. A read-only sidecar examined only the provisioned petition and QP, without retrieval or writes; its factual points used in the forecast were checked against the supplied text. Consulted `metrics/statpack.md` and selected fields in `metrics/statpack.json`. The exact prior-Term reached-baseline pool was computed from the latter as 607 / 11,599 = 0.0523320976 across OT2017–OT2024, all sal-v4. No other cell's output, outcome file, or topic-label artifact was read.

## Corpus calls and helpers

1. `uv run fedcourts paths --court scotus --docket 73500284 --event evt-order-call-for-response-disposition --role predictor` failed initially because uv's default cache was on a read-only filesystem. No corpus read occurred.
2. `uv run fedcourts query --help` failed initially for the same uv cache reason. This was help only, not a data query.
3. Retried both helper commands with `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. The paths helper identified the case and event and explicitly withheld the evaluator-only outcome path. Query help described structured filters and clocks. Subsequent help-only invocations used `COLUMNS=140 ... query --help | head -65` and `COLUMNS=110 ... query --help | sed -n '27,90p'` to inspect the options after console output truncation. The paths helper was also repeated successfully alongside the first of those help invocations. None of these helpers retrieved priors.
4. Actual filtered prior retrieval:

   ```text
   UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 3
   ranged corpus reads: 73 GET(s), 18939904 byte(s)
   ```

   Returned RiseandShine Corporation v. PepsiCo, No. 24-1016; Devin Chaney v. United States, No. 24-6543; and Monsanto Company v. Durnell, No. 24-1068. They are not this case. The Term screen selects earlier docket-number Terms and is not proof that every returned disposition predates the baseline date; the returned grant dates were all before July 27, 2026. These grant-selected examples were not used to estimate grant rates or assert substantive similarity. No `--full` opinion hydration was requested. No current corpus-freshness claim is based on this query.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --help | head -35` inspected freshness-command documentation only; no `corpus-info` data read or census was attempted. Local path/serialization implementation was inspected to keep artifact handling consistent with the repository. Schema and validation commands are local checks, not case retrieval.

## CourtListener MCP

- `search(type="o", q='"Setty" "Shrinivas"', court="ca9", filed_before="2026-07-28", num_results=3)` sought a historical lower-court split authority, not this petition's history. It returned **HTTP 429**, the 1,400/day limit exhausted, with a reported wait of 6,844 seconds. No opinion or search result was received. No REST fallback, credential access, or retry was attempted.

## Web

- Search: `site.supremecourt.gov opinions 2020 GE Energy Outokumpu 18-1048 equitable estoppel which body of law`. Intended to verify only the 2020 precedent. The tool returned no usable result or source content.
- Search: `GE Energy Outokumpu 2020 18-1048 Supreme Court opinion`. Same historical-authority purpose; again no usable result or source content was returned.

No current docket, later filing, disposition, or subsequent coverage of Indian Harbor v. Town of Vinton was sought. The failed independent-authority retrieval did not supply evidence; substantive discussion rests on the provisioned documents, with advocacy identified as such.
