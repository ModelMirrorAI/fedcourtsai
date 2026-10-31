# Retrieval record

No search sought this petition's disposition or subsequent history. This is a forward cell. Beyond the provisioned record, I consulted the committed `metrics/statpack.md`, specifically the modern-cert disposition/circuit tables, paid-segment relist/CVSG/amicus cuts, and sal-v4 reached-band table. The frozen anchor in context, not the current-Term table row, supplies the numerical starting point.

## Corpus commands

The first tooling command, `uv run fedcourts paths --court scotus --docket 9026000394 --event evt-petition-disposition --role predictor`, failed because the default uv cache was read-only. Retrying with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000394 --event evt-petition-disposition --role predictor` succeeded. This resolved paths only; no outcome file was read. All subsequent uv commands used that temporary cache and `--no-sync`, which uses the existing environment without installing packages.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — read the structured-filter interface. Help was displayed again with `COLUMNS=160` and piped through `head -55`; no corpus retrieval in either help call.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era modern --limit 4` — refused: `modern` is not an era token. The CLI supplied the closed decade vocabulary. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '603 U.S. 204' --limit 3` — no matching rows; the CLI warned that only 200 SCOTUS rows in scope carried reporter citations, so this was a coverage limitation rather than evidence that Purdue Pharma does not exist.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --limit 3` — returned recent grant-side records, including the Scanlan substantive interim application and Association for Education Fairness. This broad sample was not a set of comparable bankruptcy cert petitions; it supplies no numerical adjustment.

   `ranged corpus reads: 17 GET(s), 4456448 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 23-124 --limit 1` — returned Harrington v. Purdue Pharma, cert granted August 10, 2023, no hydrated opinion. Output was projected with jq onto identity, disposition, dates, distribution count, CVSG, and opinion availability. General subject-matter comparator, not a matched probability estimate.

   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`

6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-1013 --limit 1` — returned the earlier Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC petition: denied June 1, 2026, one distribution, no CVSG. The petition itself had already disclosed this prior denial. Output was projected with jq onto the same limited fields.

   `ranged corpus reads: 1 GET(s), 262144 byte(s)`

## CourtListener MCP

1. Opinion search with citation `64 F.4th 84`, limit 2, requesting caseName/dateFiled/citation/absolute_url/opinions — zero results. Not treated as disproof of the citation.
2. Opinion search with query `"LTL Management"`, court `ca3`, filed before January 1, 2024, limit 3, requesting caseName/dateFiled/citation/absolute_url/opinions/snippet — returned January 30, 2023 versions and the March 31, 2023 amended Third Circuit opinion, cluster 9388617, opinion 9384093. Search metadata supplied the official court PDF location. No search concerned this petition's outcome.

## Web

1. Search: `site.ca3.uscourts.gov "LTL" "64 F.4th" "financial distress"`. The surfaced result was a different 2025 bankruptcy opinion discussing LTL; it was not relied on. No credential-bearing result URL was copied into an artifact.
2. Opened the official Third Circuit amended opinion identified by the MCP search, court-hosted file `opinarch/222003pa1.pdf`. Its opening describes the § 1112(b) dismissal, and its concluding discussion makes the financial-distress requirement and uncapped funding backstop central while declining to categorically reject every two-step bankruptcy. This primary authority informed the distinction between dismissal and stay relief.
3. Searched within that PDF for `We do not lay down`; no match. No inference was drawn from the unsuccessful literal search.

Local prompt/schema/source reads, git status, artifact creation, and schema/data validation are operational checks rather than additional legal retrieval.
