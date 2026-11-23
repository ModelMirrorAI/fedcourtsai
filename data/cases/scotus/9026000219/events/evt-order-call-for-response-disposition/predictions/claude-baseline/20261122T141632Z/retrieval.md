# Retrieval log

- `uv run fedcourts paths --court scotus --docket 9026000219 --event evt-order-call-for-response-disposition --role predictor` — resolved paths.
- `uv run fedcourts query --help` (twice) — read flags.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`modern` is not an era value); printed help.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — 5 generic granted priors (e.g., Robinhood Markets v. Sodha; Goldman Sachs Bank USA v. Brown; three government/state matters incl. two applications). Not informative for this case. stderr: `ranged corpus reads: 35 GET(s), 9043968 byte(s)`.
- `metrics/statpack.md` — relist-count, CVSG, amicus-count cuts and the sal-v8 salience band table.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-219.html` — the Court's live docket (forward mode). Showed, beyond the snapshot: Oct 9/13 extension of the response to Nov 13, 2026; Nov 5/6 further extension to Dec 7, 2026. No response filed and no disposition.
- No CourtListener MCP calls; no web searches.
