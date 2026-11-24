# Retrieval log

Beyond the provisioned inputs:

1. `uv run fedcourts paths --court scotus --docket 9026000078 --event evt-petition-disposition --role predictor` — resolved paths.
2. `metrics/statpack.md` — read the modern-cert disposition table, the relist-count, CVSG, amicus-count, capital-marking and salience-band cuts, the per-Term table, the sal-v8 band table, and the originating-court row for the Supreme Court of Florida.
3. `uv run fedcourts query --help` — flag reference.
4. `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 8` — refused: `roberts` is not an era token (usage text returned). No rows.
5. `uv run fedcourts query --court scotus --docket-number 25-6623 --include-open` — Kian v. Florida: disposition granted, cert granted 2026-06-15, distribution count 5. `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Run a second time to extract fields (transfer line not captured on the second run).
6. `uv run fedcourts query --court scotus --docket-number 26-76 --include-open` — Jackson v. Florida: open, capital, distribution count 3. `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Run a second time to extract fields (transfer line not captured).
7. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — five recent granted rows, none on point (Robinhood v. Sodha, two Mullin matters, Goldman Sachs v. Brown, Scanlan v. Coalition for Open Democracy). `ranged corpus reads: 31 GET(s), 7995392 byte(s)`.
8. Web search (standard): "Kian v. Florida 25-6623 Supreme Court certiorari granted question presented oral argument" — confirmed cert granted June 15, 2026 on whether the Sixth Amendment requires a 12-person jury for serious felonies (overruling Williams v. Florida), and that Florida has asked the Court to hold other six-person-jury petitions for Kian. No argument date found. No forecast of Hunt or Jackson surfaced.

No CourtListener MCP calls.
