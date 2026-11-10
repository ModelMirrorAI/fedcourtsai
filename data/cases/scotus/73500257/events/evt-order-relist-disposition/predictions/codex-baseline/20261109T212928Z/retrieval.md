# Retrieval record

## Local inputs and reference material

Read the prediction contract, prediction schema, event definition, case-level snapshot and context, document manifest, questions presented, relevant petition/BIO/reply sections, official amended opinion and en banc dissent in the appendix, and the staged lower-court opinion/docket excerpt. Consulted the committed paid-segment sections and prior-Term sal-v8 table in `metrics/statpack.md`, the relist bucket counts in `metrics/statpack.json`, and the tooling/flags schemas. No outcome, other prediction, evaluation, or `data/qp-topics/` file was read.

The initial local resolver attempt was:

`uv run fedcourts paths --court scotus --docket 73500257 --event evt-order-relist-disposition --role predictor`

It failed before resolving paths because uv's default cache was read-only (`/home/codexcell/.cache/uv/CACHEDIR.TAG`). Reissued with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync` and the same arguments; it returned the case and event paths and identified the outcome as evaluator-only without naming or opening it. No packages were installed. Subsequent CLI calls used this cache override and `--no-sync`.

## Corpus attempts

1. Read `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`; subsequently viewed the first 78 help lines again with `COLUMNS=120`. These were help-only calls, not corpus reads, and printed no transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '595 U.S. 1' --citation '595 U.S. 9' --limit 4`
   - Result: no rows. The coverage note said only 200 SCOTUS rows carried any own-reporter citation; this is not evidence that the precedents do not exist. Switched to CourtListener for the known precedent rather than retrying the sparse citation field.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 4`
   - Result: no rows; no inferred denial or grant pattern taken from the empty result. The call scanned substantially more corpus data than its four-row limit suggested, so it was not repeated.
   - `ranged corpus reads: 1076 GET(s), 281870336 byte(s)`

These were prior-only queries, not searches for this petition, and no `--full` opinion hydration was requested. Forward mode carries no replay clock; no `DECIDED_BEFORE` mask was required.

## Web attempts

1. One `web.run` search call with queries `site:supremecourt.gov/opinions "Zorn" "Linton"` and `site:supremecourt.gov/opinions "Rivas-Villegas" "Cortesluna"`. The tool returned no visible results or content. No information was taken from this call.
2. One `web.run` open of the official Rivas-Villegas PDF at `https://www.supremecourt.gov/opinions/21pdf/20-1539_09m1.pdf`, using the address supplied by CourtListener's result. The tool returned no visible content. The opinion text used came from CourtListener instead.

Neither web call searched for the pending North Las Vegas petition or its disposition.

## CourtListener MCP

1. `search(type="o", case_name="Rivas-Villegas v. Cortesluna", court="scotus", num_results=2)`: one result, cluster 5290447, opinion 5118993, 595 U.S. 1, decided October 18, 2021. This identifies a prior qualified-immunity summary reversal, not a disposition of the target petition.
2. `read_document(opinion_id=5118993)`: returned opinion text. Used its narrow precedent-comparison rationale, summary-reversal route, and reservation of whether circuit precedent can clearly establish law.
3. `search(type="o", case_name="Zorn v. Linton", court="scotus", num_results=1)`: one result, cluster 10813527, opinion 11280281, No. 25-297, decided March 23, 2026.
4. `search_document(opinion_id=11280281, query="SOTOMAYOR", snippet_size=650)`: returned the grant-and-reverse conclusion and excerpts identifying Sotomayor's dissent joined by Kagan and Jackson. Used only to assess this prior's route and possible separate authors, not to impute votes in the target case.
5. `read_document(opinion_id=11280281, chunk_index=1, chunk_size=8000)`: read the majority's specificity analysis, reservation in footnote 3, and summary-reversal conclusion. Both this prior and Rivas-Villegas predate the target cell.

## Output checks

The required cell validator is run locally after writing the forecast. Validation and schema inspection are output-contract checks, not retrieval of case outcomes. No current target-docket lookup was made.
