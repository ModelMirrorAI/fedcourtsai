# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, event.yaml, context.json,
and the three provisioned documents: questions-presented.txt, petition.txt,
brief-in-opposition.txt) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "554 U.S. 570" --limit 8`
  — returned no rows.
  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  stderr note: citations filter: 161 of 590339 rows in scope (scotus) carry
  citation data, and the column holds a case's OWN reporter cites — an empty
  result here usually means missing data, not no match.
  Not retried (sparse-filter guidance in the prompt).

## Web searches (forward mode, unrestricted)

- `Supreme Court No. 25-238 cert granted June 30 2026 assault weapons consolidated 25-566`
  — identified the lead consolidated case as Viramontes v. Cook County,
  No. 25-238 (CA7), and the limited QP. Sources surfaced:
  [SAF](https://saf.org/supreme-court-grants-cert-in-saf-assault-weapons-cases/),
  [Shooting News Weekly](https://www.shootingnewsweekly.com/gun-control/finally-supreme-court-grants-cert-in-two-assault-weapons-ban-cases/),
  [scotus2a.com](https://scotus2a.com/).
- `Viramontes v. Cook County Supreme Court merits brief August 2026 argument date`
  — merits calendar: petitioners' brief due 2026-08-28, respondents'
  2026-10-21; no argument date set (December 2026 sitting projected); merits
  briefs not yet filed as of the snapshot. Sources surfaced:
  [SCOTUSblog case page](https://www.scotusblog.com/cases/viramontes-v-cook-county/),
  [supremecourt.gov docket 25-238](https://www.supremecourt.gov/docket/docketfiles/html/public/25-238.html),
  [Wikipedia](https://en.wikipedia.org/wiki/Viramontes_v._Cook_County).

Neither search surfaced any disposition of the consolidated cases (none
exists — the event is genuinely pending). No CourtListener MCP calls were made.
Background context on the June 2025 Snope v. Brown / Ocean State Tactical
denials and their separate writings is from training knowledge and predates
the snapshot.
