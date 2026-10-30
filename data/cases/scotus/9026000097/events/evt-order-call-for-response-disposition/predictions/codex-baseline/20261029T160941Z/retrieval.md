# Retrieval record

No lookup sought this petition's own disposition or subsequent docket history. The snapshot, context, event definition, questions presented, petition, appendix passages and document manifest were provisioned inputs. Repository instructions, prediction/feedback schemas, CLI help and path resolution were consulted as task-contract material. External attempts are all listed below, including failures.

## Committed historical context

- Read the cert sections of `metrics/statpack.md`: modern discretionary-cert dispositions, circuit, relist, CVSG, amicus and salience cuts, and the full displayed per-Term sal-v4 table.
- Read `metrics/statpack.json` term/segment fields and calculated the baseline reached rate across every displayed strictly prior Term, 2017–2025: 660 / 12,913 = 0.0511112832. No current-Term row entered that anchor.

## Corpus tooling

1. `uv run fedcourts query --help` initially failed before execution because uv's default cache was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; help succeeded. Several later help reads used `COLUMNS=120` or `COLUMNS=160` for legibility. These made no corpus queries and printed no transfer lines.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000097 --event evt-order-call-for-response-disposition --role predictor` confirmed the case and event paths and marked the outcome evaluator-only. No outcome was opened. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`
   - `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   - Returned U.S. DOGE Service v. United States District Court, docket 25-1103; Corey Duran Berry v. United States, docket 25-7026; and Todd Blanche v. Izuchukwu Ozurumba, docket 25-1343. These are unrelated prior-Term grant examples, not matched education cases, and supplied no substantive adjustment. This is a forward cell; the year filter limits docket-Term populations, not necessarily the calendar dates of those grants.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '570 U.S. 595' --limit 1`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - No rows. The tool warned that only 200 in-scope rows carry reporter citations and that an empty citation lookup often reflects coverage rather than absence of precedent. I did not interpret the result as negative legal evidence.

## CourtListener MCP

- `search(type="o", citation="185 N.W.2d 9", num_results=3, fields=["caseName", "dateFiled", "citation", "absolute_url", "id", "opinions"])` attempted to locate the Michigan Traverse City prior cited in the petition. It returned HTTP 429, reporting the daily rate limit. No opinion or search results were returned. No direct REST fallback was attempted.

## Web attempts: general precedent only

1. One `web.run` call submitted two searches: `site.supremecourt.gov opinions Koontz unconstitutional conditions benefit constitutional right 2013` and `site.supremecourt.gov opinions Espinoza 2020 private schools religious education subsidies`. The tool returned no visible results or usable text.
2. Opened `https://www.supremecourt.gov/opinions/19pdf/18-1195_g314.pdf` for the general Espinoza precedent. The tool returned no visible content.
3. Opened `https://www.govinfo.gov/content/pkg/USREPORTS-570/pdf/USREPORTS-570-595.pdf` for the general Koontz precedent. The tool returned no visible content.

No external precedent text was obtained from those attempts. Legal assessment rests on the staged petition and lower-court opinion rather than an asserted independent verification of their cited authorities.

## Independent input review

A sidecar reviewer initially read only the provisioned appendix to assess the lower court's holding and vehicle limitations. I checked the cited Appendix A passages concerning the logistical-burden rationale and absence of a Free Exercise claim before relying on them. The same reviewer then checked this cell's completed artifacts against the stats-reviewer checklist and committed statpack, independently reproduced the anchor, and reported no blockers. It performed no outside retrieval and wrote no files.
