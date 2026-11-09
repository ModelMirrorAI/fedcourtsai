# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 20`
   - Stderr/transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 20 recent 2020s SCOTUS cert priors.

2. `uv run fedcourts query --court scotus --docket-number 22-240`
   - Stderr/transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned `scotus/72475563` (*Jim Justice, Governor of West Virginia, et al. v. Jonathan R., Minor, By Next Friend Sarah Dixon, et al.*, No. 22-240), confirming certiorari was denied on `2022-10-11` in the earlier interlocutory appeal in this same litigation.

3. `uv run fedcourts query --court scotus --docket-number 25-165`
   - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/73274852` (*Sault Ste. Marie Tribe of Chippewa Indians v. Michigan, et al.*, No. 25-165), confirming certiorari was denied on `2026-01-12`.

4. `uv run fedcourts query --court scotus --attorney "Michael R. Williams" --limit 20`
   - Stderr/transfer: Failed usage check (`No such option: --attorney`).

5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 20`
   - Stderr/transfer: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Result: Returned 20 recent 2020s SCOTUS granted cases.

6. `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 10`
   - Stderr/transfer: `ranged corpus reads: 1028 GET(s), 269484032 byte(s)`
   - Result: Returned 0 rows matching `summary-reversal` in the 2020s slice.

7. `uv run fedcourts query --court scotus --docket-number 19-765`
   - Stderr/transfer: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: Returned `scotus/66727435` (*Michael Faust, Director, Arizona Department of Child Safety v. B. K., By Her Next Friend Margaret Tinsley, et al.*, No. 19-765), confirming certiorari was denied on `2020-03-23` in the Ninth Circuit foster-care structural-reform class action cited in the petition.

## CourtListener MCP Lookups

None attempted (provisioned `decision-below.txt`, `lower-court-docket.txt`, `petition.txt`, `appendix.txt`, and `questions-presented.txt` were complete).

## Web Searches

None attempted.
