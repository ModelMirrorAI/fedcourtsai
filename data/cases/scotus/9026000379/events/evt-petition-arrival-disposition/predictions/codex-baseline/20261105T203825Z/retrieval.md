# Retrieval log

## Local inputs and reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json`; the event definition; the complete provisioned snapshot `2026-09-21.json`; `record/context.json`; and `record/same-question.json`. No `record/documents/` files were present. Consulted the committed `metrics/statpack.md`, particularly modern-cert dispositions, originating court, paid-segment relist/CVSG cuts, and prior-Term sal-v7 federal-band rates. No other prediction, evaluation, realized-outcome file, or QP-topic labeling artifact was read.

The first `uv run fedcourts paths --court scotus --docket 9026000379 --event evt-petition-arrival-disposition --role predictor` failed because its default uv cache was read-only. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`. Read `uv run fedcourts query --help` with the same cache override. A directory-level instruction-file search found no AGENTS.md. Read the PDF command help and located its implementation symbol; no code was changed.

## Structured corpus calls

All successful CLI calls used `UV_CACHE_DIR=/tmp/uv-cache`. No replay environment clock was set; these calls nevertheless used a strictly earlier Term filter.

1. `uv run fedcourts query --court scotus --era roberts --disposition granted --decided-before 2026 --limit 3` — refused because eras are decade tokens, not Chief Justice names. No transfer line was emitted. Corrected immediately.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` — returned U.S. DOGE Service, 25-1103; Corey Duran Berry, 25-7026; and Todd Blanche v. Izuchukwu Ozurumba, 25-1343. These are grant-selected reference rows, not a random denominator; no opinion bodies requested.

   `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

3. `uv run fedcourts query --court scotus --docket-number 25-886 --decided-before 2026 --limit 1` — returned Genalo v. Carol Williams Black, with a June 15, 2026 cert grant and distribution_count=3. This is a different petition's pre-arrival grant, not this case's outcome.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

## CourtListener MCP calls

1. `search(type="r", court="ca2", docket_number="26-1396", num_results=5)` — one matching lower-court docket, C. v. Noem, docket ID 73412762, with D. C. and the government officials as parties. Returned document examples were unavailable as text.
2. `get_endpoint_schema(endpoint_id="docket-entries")` — inspected supported entry filters and fields.
3. `call_endpoint("docket-entries", docket=73412762, date_filed__lt="2026-09-22", order_by="entry_number", fields=["entry_number","date_filed","description","recap_documents"], num_results=30)` — 20 pre-arrival entries; output was verbose and truncated. Embedded document records showed no available text.
4. Repeated the preceding endpoint call with only `entry_number`, `date_filed`, and `description` — all 20 entries readable. Identified the March 20 district order and September 2 government motion for summary affirmance, with subsequent September correspondence. No appellate judgment appeared in this bounded set.
5. `search(type="o", case_name="C. v. Noem", filed_after="2026-03-19", filed_before="2026-03-21", num_results=10)` — zero matching opinions. This is a retrieval coverage result, not a conclusion that no district opinion exists.
6. `get_endpoint_item("dockets", 73412762, fields=["id","case_name","docket_number","court","originating_court_information"])` — rejected the final field name, suggesting `original_court_info`.
7. Repeated that item request with `original_court_info` — confirmed the lower-court docket identity; originating-court details were empty. No separate district opinion was recovered.

## Web calls and official petition

Searches attempted, with exact query strings:

1. `""Genalo" "D. C." "26-1396"` and `"Genalo" "D. C." "Second Circuit"`.
2. `"Genalo" "D.C." detention petition` and `"D. C." "Noem" "March 20"`.
3. `site.justice.gov "Z. F." "25-178"` and `site.supremecourt.gov "25-178" "September 11, 2026"`. This tentative companion lead produced no verified relevant authority and was not used in the forecast.
4. `Genalo D C petition September 2026 immigration detention` and `"d.c._pet_final.pdf"`. Located the official DOJ petition. No search requested this petition's own disposition or subsequent history.

Attempted six `web.open` reads of the official petition URL, grouped before and after the latter searches. The forecast's verified text ultimately came from the independent extraction below rather than relying on search snippets or incomplete web rendering.

Official primary source: `https://www.justice.gov/sites/default/files/2026-09/d.c._pet_final.pdf` — Petition for a Writ of Certiorari Before Judgment, Genalo v. D.C. Used cover, QP page I, introduction, and reasons for review. Source citations in the reasoning refer to the petition's printed pagination. The petition identifies itself as a replacement for Black, not for the unverified Z. F. lead.

Fetched the same URL once using Python's standard-library `urllib.request`; the 1,294,068-byte PDF was held in a Linux memory file, without creating an extra output artifact. Read it using the required `uv run fedcourts pdf-text /proc/self/fd/<descriptor>` command, passing the open memory descriptor. Extractor report: `pdf-text: 174 page(s), 296524 character(s)`. The extractor completed successfully without a character-limit truncation; terminal display excerpts were truncated, so I do not claim to have individually read all appendix pages. The QPs and core petition text were readable.

No current Supreme Court docket page or subsequent disposition of this case was fetched. No CourtListener REST fallback, paid PACER retrieval, package installation, or credential access was attempted.
