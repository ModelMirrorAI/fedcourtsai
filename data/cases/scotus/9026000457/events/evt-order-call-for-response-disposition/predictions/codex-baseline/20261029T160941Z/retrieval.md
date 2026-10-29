# Retrieval record

## Local reference material

- Read the committed `metrics/statpack.md` modern-cert disposition, relist, CVSG, amicus, and prior-Term salience-band tables, with exact baseline-band risk-set counts from `metrics/statpack.json`. Pooled 2017–2025 only: 660 / 12,913 = 0.0511112832. No live aggregate count was inferred from the small query samples.
- Read the output schemas and repository path/serialization helpers to construct and validate this cell's files. Read no other cell's prediction or evaluation, no outcome file, and nothing under `data/qp-topics/`.

## Corpus calls

Commands use `UV_CACHE_DIR=/tmp/uv-cache` because the default cache is read-only in this runner.

1. `uv run fedcourts query --help` initially failed before retrieval: uv could not open its default cache's `CACHEDIR.TAG` on a read-only filesystem. No corpus response or transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; inspected structured filters and the clock contract. No corpus retrieval or transfer line. Repeated with `COLUMNS=140` and displayed its opening options for readability; again no retrieval or transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2010s --citation '563 U.S. 110' --limit 3` returned no rows. It warned that only 200 SCOTUS rows in scope carry any reporter citation and that missing coverage is more likely than a nonexistent case. Did not retry the sparse citation filter.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. City of Chicago (25-1098), each denied October 19, 2026. Their recorded distribution counts were 2, 2, and 4. These are not substantive 340B analogues, and an outcome-filtered sample cannot estimate the chance of denial. No opinion bodies requested or read.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

The local `fedcourts paths --court scotus --docket 9026000457 --event evt-order-call-for-response-disposition --role predictor` command initially had the same cache failure, then succeeded with the cache override and was repeated successfully. It resolved locations only and withheld the evaluator-only outcome path; no outcome was read.

## CourtListener MCP

- `search(type="o", citation="563 U.S. 110", num_results=2, fields=["caseName", "citation", "dateFiled", "absolute_url", "cluster_id", "snippet"])`: HTTP 429; daily rate limit exhausted, expected availability in 8,679 seconds. No opinion or case result returned. No token extraction, direct REST call, or retry.

## Web attempts

- General-context search batch: `site.supremecourt.gov Astra USA Santa Clara 563 110 2011 340B` and `site.supremecourt.gov Rutledge Pharmaceutical Care Management 2020 preemption cost regulation`. The tool returned no visible result content; no search result informed the forecast.
- Open attempted for the Court's historical Astra opinion PDF at `https://www.supremecourt.gov/opinions/10pdf/09-1273.pdf`. No visible document content returned; no externally obtained opinion text informed the forecast.

Neither attempt sought this petition's disposition or subsequent history. No live docket lookup was attempted. All substantive case facts used came from the provisioned snapshot, party filings, and opening appellate decision in the appendix.
