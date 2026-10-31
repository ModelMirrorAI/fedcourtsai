# Retrieval record

## Local reference material and command setup

Read the prediction prompt, prediction schema, tooling and flags schemas, and relevant tables in metrics/statpack.md, including sal-v4 reached-band rates, terminal relist counts, CVSG status, and amicus counts. The case facts came from the provisioned event and record. No other cell's output, evaluator outcome, or qp-topics artifact was read.

Initial attempts to run `uv run fedcourts paths --court scotus --docket 9026000394 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` failed before application startup because uv's default cache location was read-only. Both were rerun successfully with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`. No packages were installed. Query help was also read a second time through a line-range filter to see options hidden by display truncation. The paths command returned the case and event locations, not an outcome input.

## Corpus lookups

All commands below used the environment prefix `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`.

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 5`
   - `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned five selected grants, including U.S. DOGE Service, Berry, Ozurumba, and Missionaries of Saint John the Baptist. These are not bankruptcy analogues and were not used to estimate a rate. The cutoff is the docket-Term cutoff, not a calendar-day assertion.
2. `uv run fedcourts query --court scotus --citation '603 U.S. 204' --citation '602 U.S. 268' --decided-before 2026 --limit 3`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - No matching rows. The command warned that only 200 scoped rows carried reporter citations and that citation lookup coverage was sparse. No inference about the existence or holdings of the authorities was drawn.
3. `uv run fedcourts query --court scotus --docket-number 25-1013 --limit 1`
   - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC, denied June 1, 2026, with one distribution. This is the separate prior petition expressly discussed at page 20 of the provisioned petition, not Herlihy's outcome. Used as modest negative context, not as an adjudication of this question or evidence of a current hold.

## Web attempts

The following were attempts to locate general primary-source legal context, not this petition's disposition. Early calls yielded no usable visible response and supplied no factual basis for the forecast. Repeated calls are recorded rather than silently omitted.

1. Search batch: `site.ca3.uscourts.gov "LTL" "financial distress" "2023"`; `site.supremecourt.gov "Harrington" "Purdue" "524(g)" "2024"`. No usable visible response.
2. Open attempt: `https://www.govinfo.gov/content/pkg/USCOURTS-ca3-22-02006/pdf/USCOURTS-ca3-22-02006-0.pdf`. No usable visible response.
3. Malformed find attempt, empty reference and pattern `524`. No usable result; no source consulted successfully.
4. Search batch: `site.ca3.uscourts.gov "64 F.4th 84" "financial distress"`; `site.supremecourt.gov opinions 23pdf 23-124 Purdue Pharma 524`. No usable visible response.
5. Repeat open attempt of the same govinfo PDF. No usable visible response.
6. Further repeat open attempt of the same govinfo PDF. No usable visible response.
7. Find attempt on the same govinfo PDF for `financial distress`. No usable visible response.
8. Search: `site.ca3.uscourts.gov "LTL Management" "financial distress"`. Returned an official Third Circuit 2024 nonprecedential LTL opinion, captioned Nos. 23-2971, 23-2972, and 23-2973, discussing the earlier financial-distress rule, plus a separate precedential Boy Scouts bankruptcy opinion. Search results only; no substantive proposition from these later opinions was used to supplement the provisioned record.

No CourtListener MCP lookup was attempted. No live search for this petition's outcome or subsequent history was made.
