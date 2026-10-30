# Retrieval record

## Local inputs and reference materials

Read AGENTS.md, `.github/prompts/predict.md`, the prediction/tooling/flags schemas, the provisioned arrival event, context, and the sole snapshot `2026-10-30.json`. No documents or related snapshots were staged. Consulted committed `metrics/statpack.md` and `metrics/statpack.json`, and calculated the strictly-prior sal-v4 federal reached-rate pool with a local Python calculation: 151/206 = 0.7330097087378641. Read path/serialization helper definitions and the statistical-review checklist to check output conventions and denominator interpretation. No other cell's prediction/evaluation or topic-label artifact was read.

The first two CLI invocations below failed before retrieval because uv's default cache was read-only. Subsequent commands used the process-local prefix `UV_CACHE_DIR=/tmp/uv-cache`; no credentials were read or modified.

1. `uv run fedcourts paths --court scotus --docket 9026000572 --event evt-petition-arrival-disposition --role predictor` — failed at cache initialization; no corpus transfer line.
2. `uv run fedcourts query --help` — same cache failure; no corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000572 --event evt-petition-arrival-disposition --role predictor` — resolved the case and event paths; outcome path was marked evaluator-only and was not read.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — displayed structured filters. No corpus retrieval or transfer line.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --decided-before 2026 --limit 4` — rejected the era token `modern`; the CLI displayed accepted decade tokens. No corpus read-stats line was printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 4` — returned grant-conditioned, recency-ranked examples 25-1103, 25-7026, 25-1343, and 25-1131. This Term mask is not a calendar-date mask. No opinion hydration was requested. These examples were not used as a denominator or rate estimate.

   `ranged corpus reads: 34 GET(s), 8847360 byte(s)`

3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 25-1415 --limit 1` — companion petition on the same detention question, pending in the stored row with one distribution; last live-polled October 26, 2026.

   `ranged corpus reads: 9 GET(s), 2359296 byte(s)`

4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-104 --limit 1` — related government petition reports granted October 1, 2026; last live-polled October 25, 2026. This is another case's grant, not the target petition's outcome.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-43 --limit 1` — opposing-side companion petition, pending with one distribution in the stored row; last live-polled October 25, 2026.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` — failed: service backend has no client-side connection. No corpus-wide newest-pull or snapshot vintage was available, and no transfer line was printed. Did not attempt a local pull or change the service backend.

## CourtListener MCP

1. `search(type="o", court="ca7", docket_number="25-3127", filed_before="2026-10-30", num_results=5)` — returned two July 30, 2026 published-opinion records for Jaciel Rojas v. Samuel Olson, corresponding to the lower-court docket/date in the snapshot. Main combined opinion id 11404410, alternate record 11404409. Did not search SCOTUS for this petition's disposition.
2. `read_document(opinion_id=11404410, chunk_index=0, chunk_size=14000)` — read the beginning of the combined opinion: immigration detention under §§ 1225/1226, the circuit split, custody/mootness posture, and earlier petitions on the issue.
3. `search_document(opinion_id=11404410, query="dissent", snippet_size=900)` — returned dissent-related excerpts, including Judge Sykes's competing statutory construction and identification of the other petitions.
4. `read_document(opinion_id=11404410, chunk_index=[6,7], chunk_size=14000)` — read late portions of the same July 30 opinion, chiefly the dissent and its discussion of the existing circuit conflict. No Supreme Court disposition of the target case appeared.

## Web calls

1. One combined search call used two queries: `"Rojas" "Padula" "25-3127"` and `site.supremecourt.gov Rule 10 considerations governing review certiorari`. The exact lower-docket search yielded no matching result. The general search surfaced official Supreme Court rules, including the Rule 10 considerations concerning important conflicts. No target-case outcome appeared; no secondary commentary was used as evidence.
2. Opened the official Supreme Court public docket search page for **No. 26-104**. It showed the July filing, the October 1, 2026 cert grant, and a merits briefing schedule. The linked lower-court decision is Second Circuit No. 25-3141, June 11, 2026. Used the grant as pre-snapshot companion context only.
3. Repeated the same open of the **No. 26-104** official docket page. The response again showed the related petition's grant. No linked briefs, other linked records, or target-case docket page were opened.

The target petition's own disposition and subsequent history were never queried. All companion-status claims are limited to the observations described above.
