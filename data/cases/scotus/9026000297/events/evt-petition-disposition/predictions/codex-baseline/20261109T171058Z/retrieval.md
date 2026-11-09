# Retrieval record

## Local inputs and reference material

Read `.github/prompts/predict.md`, the prediction, flags, and tooling schemas, the event definition, and the case-level context, dated snapshot, same-question list, document metadata, QPs, substantive petition sections, lower-court docket summary, and selected decision/appendix sections. Consulted the modern-cert disposition, originating-circuit, paid-segment relist/CVSG/amicus, and sal-v8 prior-Term reached-band tables in `metrics/statpack.md`. No other predictor's output, evaluator outcome, or QP-topic artifact was read.

## CLI calls and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000297 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help` initially failed before execution because the default `/home/codexcell/.cache/uv` was read-only. Neither printed a transfer line.
2. Retried both with `UV_CACHE_DIR=/tmp/uv-cache`. Paths resolved the case/event; query help described structured filters. Query help was also invoked a second time to read its remaining options. No corpus transfer lines for these administrative calls.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era roberts --decided-before 2026 --limit 4` failed input validation: `roberts` is not an accepted decade-token era. The error provided the valid vocabulary. No transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` succeeded. Returned Goldman Sachs Bank USA v. Brown, No. 25-1408; U.S. DOGE Service v. U.S. District Court for D.C., No. 25-1103; and Corey Duran Berry v. United States, No. 25-7026. Their recorded grants are November 6 and October 13, 2026, respectively. The Term filter admits prior docket Terms even when their grant dates fall in the current calendar year; all three dates precede the snapshot. These are procedural context only, not substantive analogues.

   `ranged corpus reads: 36 GET(s), 9437184 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '563 U.S. 493' --decided-before 2026 --limit 1` returned no row. It warned that only 200 scoped SCOTUS rows carry reporter citations, so absence is a coverage gap rather than evidence about Brown v. Plata. No broader retry was made.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## CourtListener MCP

1. `search(type="o", citation="978 F.2d 373", num_results=1)` returned Council 31 v. Ward, Seventh Circuit, October 28, 1992; opinion and cluster ID 593349. The result verified the petition's adverse-circuit authority.
2. `search_document(opinion_id=593349, query="invigorating", snippet_size=1400)` returned the passage explaining that reversal made the prevailing defendant adversely affected by certification and supported jurisdiction over its conditional cross-appeal. This independently supports the procedural conflict; it concerns a different case, not this petition's outcome. No direct CourtListener REST request was attempted.

## Web search attempts

1. One `web.run` call submitted two searches: `"Council 31" "978 F.2d 373" cross appeal` and `"Jonathan R." "178 F.4th" redressability`. The latter sought only the reported lower-court decision, not Supreme Court disposition. The tool returned no displayed results or usable source material.
2. One `web.run` call submitted `site.law.cornell.edu/rules/frcp/rule_23 "final judgment"` and `site.supremecourt.gov "Microsoft Corp. v. Baker" "Rule 23(f)"`. Again no displayed results or usable source material returned. No factual assertion relies on either web call; no own-case outcome surfaced.

## Validation

The required cell-scoped validation command is run after writing these outputs, using the same UV cache override. The final assistant response reports whether it prints `OK`.
