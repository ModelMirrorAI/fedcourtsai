# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1223`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned `scotus/73253921` (*Kevin Isaac Montoya Palacios v. Vernon Liggins, Acting Field Office Director, Baltimore, Maryland, Immigration and Customs Enforcement, et al.*, No. 25-1223, filed `2026-04-28`, `date_cert_granted: "2026-06-29"`, `disposition: "granted"`, originating from `ca4` No. 26-6251).

2. `uv run fedcourts query --court scotus --docket-number 25A1300`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73383704` (*Warden, Moshannon Valley Correctional Center, et al. v. Adolph Michelin, et al.*, No. 25A1300, `application_kind: "extension"`, filed `2026-05-22`, `date_decided: "2026-06-22"`, `disposition: "granted"`).

3. `uv run fedcourts query --court scotus --judge Ambro --judge Restrepo --judge McKee --limit 10`
   - `ranged corpus reads: 641 GET(s), 167837696 byte(s)`
   - Returned 0 matching SCOTUS rows (SCOTUS `--judge` filters match Supreme Court Justices on historical rows rather than lower-court panel judges).

4. `uv run fedcourts query --court scotus --docket-number 26-146`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned `scotus/9026000146` (*Juan Baltazar, Warden, et al. v. Eva Daley*, No. 26-146, companion SG hold petition from the Tenth Circuit's decision in *Daley v. Ceja*, No. 24-1191, filed `2026-07-31`, distributed for the `2026-10-09` conference).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Daley v. Ceja", fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "cluster_id"])`
   - Failed with HTTP 429 (`Rate limit exceeded: 1400/day`).

2. `mcp_courtlistener_search(type="d", case_name="Montoya Palacios v. Liggins", fields=["caseName", "court_id", "dateFiled", "docketNumber", "docket_id"])`
   - Failed with HTTP 429 (`Rate limit exceeded: 1400/day`).

## 3. Other Local Lookups

- Read `metrics/statpack.md` for base rates and salience band tables.
- Ran `grep_search` on `metrics/` (`pattern: "Montoya|Daley|Michelin|25-1223|26-145"`) and `data/cases/scotus/` (`pattern: "Montoya Palacios|Daley|Ceja"`) to identify the docket number of the companion Tenth Circuit case (*Baltazar v. Daley*, No. 26-146); disclosed the incidental match of earlier `evt-petition-disposition` forecast summaries in `flags.json` (`leakage-disclosure`, `info`) and disregarded them.
