# Provisioned and local sources

Read the prediction prompt, prediction/tooling schemas, event definition, case-level November 9 snapshot and context, document manifest, questions presented, and relevant portions of the petition, opposition, reply, lower opinion, and lower-court docket. The appendix's truncation status was read; I did not rely on unseen appendix material. No other prediction, evaluation, outcome file, or topic-label artifact was read.

Beyond the provisioned record, consulted `metrics/statpack.md` and targeted JSON sections of `metrics/statpack.json`: modern discretionary-cert dispositions, salience/reached rates, relist counts, CVSG status, amici, originating court, and Terms. A jq calculation reproduced the frozen elevated anchor from Terms before 2025 as 460/1833. The relist pool from terminal buckets 1 and above is 726/3510. These are local aggregate context, not retrieval of this petition's disposition.

# Corpus calls

1. `uv run fedcourts paths --court scotus --docket 73539054 --event evt-order-relist-disposition --role predictor` failed because uv's default cache was read-only. No case data returned.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 73539054 --event evt-order-relist-disposition --role predictor` succeeded and confirmed the event path. The evaluator-only outcome was not opened. `--no-sync` prevents package installation; disabling the cache avoids the default-cache permission failure.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` succeeded; read the structured-filter interface.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` succeeded. Returned Roybal v. Griffith (25-442), Harrington v. Martin (25-1348), Cid v. United States (26-5123), Burford German Funding v. financialright claims (25-1269), and Roofing Designs v. Royal American Construction (25-1367). Displayed command output was truncated, so the lookup was repeated to retain a compact result and transfer accounting. These are other cases, not the target petition. No opinion bodies were requested.
5. Repeated the same query, piping the result through jq to retain identifiers, dispositions, grant dates, distribution counts, and originating courts. It returned the same five cases: the first two had three and two distributions, Cid one, and the final two two. The observed transfer line was **`ranged corpus reads: 0 GET(s), 0 byte(s)`**. The initial identical query's transfer line was not visible in the truncated display; the repeat explicitly captured it. These outcome-selected exemplars establish possibility, not a grant-rate estimate.

No replay clock is set: this is forward mode and `context.decided_before` is null. None of these lookups sought the target's outcome.

# Web attempts

1. `web.run` search query: `site.supremecourt.gov "FCC v. AT&T" "2026"`. No usable results or source text were returned in the tool response.
2. `web.run` open attempt: `https://www.supremecourt.gov/opinions/25pdf/608us2r43_m648.pdf`. No usable response text was returned. No proposition is attributed to this attempted URL, whose contents were not verified. This was an attempt to read the already-decided precedent, not the present petition's docket.

# CourtListener MCP

1. `search(type="o", court="scotus", q="\"FCC v. AT&T\"", filed_after="2026-01-01", filed_before="2026-11-10", num_results=3)`. Query id `1dec5d76`. Returned one published precedent, FCC v. AT&T, June 4, 2026, docket 25-406, cluster 10870061, opinion 11337518, with a Supreme Court opinion download reference. This is the case already cited in the provisioned filings, not Sprint's petition.
2. `search_document(opinion_id=11337518, query="misled", snippet_size=950)`. Returned one match in the concluding footnote, leaving the misleading-order contention, available relief, and appropriate proceeding unresolved. The surrounding conclusion reversed the Fifth Circuit judgment and affirmed the Second Circuit judgment. The snippet also identifies Thomas's dissent. No text about disposition of the target petition surfaced.

# Validation

The cell is validated with `UV_NO_CACHE=1 uv run --no-sync fedcourts validate data --cell data/cases/scotus/73539054/events/evt-order-relist-disposition/predictions/codex-baseline/20261109T212928Z`. Validation is a local contract check, not substantive retrieval.
