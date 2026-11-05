# Retrieval record

No search or lookup sought this petition's disposition, subsequent history, or another predictor's output. Provisioned case inputs and the event were read locally. Local contract/schema and tool-environment inspections were not substantive case retrieval.

## Local base-rate context

Read `metrics/statpack.md`: modern-cert dispositions, originating circuits, paid-segment relist/CVSG/amicus cuts, and the `sal-v7` reached-band table. Used the frozen anchor in provisioned `context.json`. No outcome or prediction artifacts were read.

## CLI attempts and results

Commands below use the authoritative literal cell identifiers. No packages were installed.

1. `uv run fedcourts paths --court scotus --docket 9026000111 --event evt-petition-arrival-disposition --role predictor`: failed before execution because `/home/codexcell/.cache/uv` was read-only. No corpus transfer line.
2. `uv run fedcourts query --help`: same cache failure. No corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000111 --event evt-petition-arrival-disposition --role predictor`: succeeded, resolving the case and event; explicitly did not open any evaluator-only outcome. No corpus transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --help`: succeeded; displayed structured filters. No corpus transfer line.
5. Repeated the successful `paths` command in item 3 to obtain untruncated path output. No corpus transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=150 uv run --offline fedcourts query --help | head -65`: inspected the filter descriptions in a wider layout. No corpus transfer line.
7. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --era modern --disposition granted --decided-before 2026 --limit 3`: rejected the unsupported era token and returned the accepted decade vocabulary. No corpus transfer line. Corrected immediately below.
8. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`: returned three granted Term-2025 priors: U.S. DOGE Service, Corey Duran Berry, and Todd Blanche v. Izuchukwu Ozurumba. Their recorded grants were October 13, 2026. The Term filter screens by docket-derived year, not by the snapshot day; this forward cell permits those records. They are broad selected examples, not topic-matched evidence or a rate estimate, and did not materially influence the forecast.

   `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

9. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --docket-number 25-417 --include-open --limit 1`: returned Francis Nielsen v. Kekai Watanabe, case `scotus/73278422`, cert granted June 22, 2026, four recorded distributions, no merits decision or judgment recorded, and merits-brief metadata dated September 23, 2026. This confirms the petition's identified lead case. Its live metadata is later than the provisioned baseline but permissible in forward mode. The grant, already stated in the petition, is the useful signal; no lead-case merits outcome was supplied.

   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`

## CourtListener MCP

1. `search(type="o", court="ca1", docket_number="23-1618", num_results=3, fields=["caseName", "dateFiled", "citation", "id", "opinions", "docketNumber"])`: one result, Arias v. Herzon, August 15, 2025, combined opinion ID **11121515**. Returned field warning: `id` is not a search-result field; the opinion's nested ID was available. The case, court, docket, and date match the petition's judgment below. This was a lower-court opinion search, not a Supreme Court disposition query.
2. `search_document(opinion_id=11121515, query="Logsdon", snippet_size=900)`: returned eight excerpts from the lower-court opinion, confirming disagreement over warrants/public locations and that Logsdon rejected relief on separate defendant/remedial grounds. Also supplied the majority's distinctions and Lynch's opposing analysis. Used as a check on the petition's split characterization.

## Web attempts

The following four `web.run` calls returned no usable source content to this session. They did not establish any additional fact, and the forecast does not rely on an unreturned page. Exact attempted searches/pages are recorded for completeness; URLs are shown as code, not as claims of successful retrieval.

1. Search queries: `site.supremecourt.gov "Goldey" "Fields" "2025"` and `site.supremecourt.gov "Nielsen" "Watanabe" "25-417"`. Purpose: official precedent and the cited lead case, not this petition's outcome.
2. Open request: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-417.html`, the lead case's docket.
3. Search queries: `Goldey Fields 24-809 per curiam supremecourt.gov opinions` and `Egbert Boule 21-147 opinion supremecourt.gov`.
4. Open request: `https://www.supremecourt.gov/opinions/24pdf/24-809_9o6b.pdf`, an attempted official Goldey opinion URL.

## Validation

The final cell-validation command is `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts validate data --cell data/cases/scotus/9026000111/events/evt-petition-arrival-disposition/predictions/codex-baseline/20261105T203825Z`. It checks output integrity, not substantive case history.

Result: `OK: 29861 artifact(s) valid, 71158 reference(s) consistent; cell complete`. Repeated after recording this result.
