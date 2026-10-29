# Retrieval record

## Provisioned and committed inputs

Read the event definition, case-level context and dated snapshot, document manifest, questions presented, and petition with its appendix. Read `metrics/statpack.md` and corresponding fields of `metrics/statpack.json` for the committed base rates. No other cell's output, outcome record, or QP-topic artifact was read. The reference population is the committed pack's shown 2017–2025 strictly-prior window, not a fresh live-corpus count.

## Corpus tooling and setup

1. `uv run fedcourts paths --court scotus --docket 9026000023 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache was read-only. It made no corpus retrieval. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`, it resolved the case and event paths successfully and explicitly withheld the evaluator-only outcome path.
2. `uv run fedcourts query --help` initially failed on the same read-only uv cache. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. A later `COLUMNS=180 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` displayed the structured options more widely. These were help requests, not corpus queries.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` succeeded.

   Exact transfer report: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`.

   It returned U.S. DOGE Service v. U.S. District Court (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343), all marked granted and each with a recorded grant date of October 13, 2026. The `--decided-before` option masks by derived Term/year, not an exact calendar cutoff. This is a forward cell, and these unrelated docket records are not this petition's outcome; nonetheless, they were not used as as-of-August comparators or evidence for the grant adjustment. No opinion bodies were requested. No other corpus lookup or open-events call was made.

## CourtListener MCP

- `search(type="o", citation="396 F.3d 348", num_results=1)` attempted to retrieve Harper v. Public Service Commission. It returned HTTP 429, stating the daily rate limit was exceeded and availability was expected in 810 seconds. No opinion content was returned. There was no REST fallback or token access.

## General web searches

The following searches sought only pre-existing legal context, not this petition's outcome. All returned no usable source content in this session; none supplied evidence used in the prediction.

1. `site.supremecourt.gov opinions 12pdf Sprint Communications Jacobs 571 69 2013 Younger`
2. One search call containing both `Sprint Communications Inc Jacobs 2013 Supreme Court 12-815 opinion` and `Harper Public Service Commission 396 F.3d 348 2005 Younger opinion`.
3. `"Harper" "396 F.3d 348" "ca4"`

No search queried TMX's disposition or the subsequent history of TitleMax or Suncor. The companion discussion comes solely from the provisioned petition. A bounded read-only consistency review was requested from a subagent; it was instructed not to research cases or inspect outcomes or other cells. It found no blockers in the supplied forecast plan. Its caution about per-Justice marginals prompted clarification that no statistical independence of writing events is assumed.
