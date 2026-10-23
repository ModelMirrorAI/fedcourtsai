# Retrieval Log

## 1. Local Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "25-5930" --include-open`
   - Transfer: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Perttu v. Richards"`) — located *Perttu v. Richards*, 605 U.S. 460 (2025) (`cluster_id=10610021`, `opinion_id=11076609`), and Sixth Circuit decision *Richards v. Perttu*, 96 F.4th 911 (6th Cir. 2024).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="Maxwell v. Thomas"`) — located Fifth Circuit decision below, *Maxwell v. Thomas*, No. 23-40699, 2025 WL 1291952 (5th Cir. Apr. 3, 2025) (`cluster_id=10372389`, `opinion_id=10838977`).
3. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10610021`) and `mcp_courtlistener_read_document` (`opinion_id=11076609`, chunks 0, 1, 6, 7) — read Chief Justice Roberts's majority opinion in *Perttu v. Richards*, 605 U.S. 460 (2025) (5–4, joined by Sotomayor, Kagan, Gorsuch, Jackson, JJ.; Barrett, J., dissenting, joined by Thomas, Alito, Kavanaugh, JJ.).
4. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10372389`) and `mcp_courtlistener_read_document` (`opinion_id=10838977`, chunk 0) — read the Fifth Circuit's unpublished per curiam opinion in *Maxwell v. Thomas* (panel: Higginbotham, Jones, Oldham, JJ.).
5. `mcp_courtlistener_search` (`type="o"`, `case_name="Melot v. Bergami"`), `mcp_courtlistener_get_endpoint_item` (`item_id=4776325`), and `mcp_courtlistener_read_document` (`opinion_id=4556672`, chunks 0, 1) — read *Melot v. Bergami*, 970 F.3d 596 (5th Cir. 2020), the Fifth Circuit precedent relied on below.
6. `mcp_courtlistener_search` (`type="o"`, `case_name="Woodall v. Federal Bureau of Prisons"`), `mcp_courtlistener_get_endpoint_item` (`item_id=3014737`), and `mcp_courtlistener_read_document` (`opinion_id=3014737`, chunks 0, 1, 2) — read *Woodall v. Federal Bureau of Prisons*, 432 F.3d 235 (3d Cir. 2005), on 28 U.S.C. § 2241 challenges to BOP community-confinement placement decisions.
7. `mcp_courtlistener_search` (`type="o"`, `case_name="Pinson v. Carvajal"`), `mcp_courtlistener_get_endpoint_item` (`item_id=9405126`), and `mcp_courtlistener_read_document` (`opinion_id=9400602`, chunks 0, 8, 9, 10) — read *Pinson v. Carvajal*, 69 F.4th 1059 (9th Cir. 2023), on the circuit split over § 2241 execution-of-sentence claims.
8. `mcp_courtlistener_search` (`type="o"`, `case_name="Rodriguez v. Copenhaver"`) — verified citation to *Rodriguez v. Copenhaver*, 823 F.3d 1238 (9th Cir. 2016).
9. `mcp_courtlistener_search` (`type="o"`, `case_name="Nance v. Ward"`), `mcp_courtlistener_get_endpoint_item` (`item_id=6480697`), and `mcp_courtlistener_read_document` (`opinion_id=6352830`, chunk 0) — read *Nance v. Ward*, 597 U.S. 159 (2022) (Kagan, J., for 5–4 majority on habeas vs. § 1983 boundary).
10. `mcp_courtlistener_search` (`type="o"`, `case_name="Erickson v. Pardus"`) and `mcp_courtlistener_get_endpoint_item` (`item_id=145722`) — verified *Erickson v. Pardus*, 551 U.S. 89 (2007) (per curiam) on *pro se* prisoner Rule 8 liberal construction.
11. `mcp_courtlistener_search` (`type="o"`, `case_name="Johnson v. City of Shelby"`), `mcp_courtlistener_get_endpoint_item` (`item_id=2750101`), and `mcp_courtlistener_read_document` (`opinion_id=2750101`, chunk 0) — read *Johnson v. City of Shelby*, 574 U.S. 10 (2014) (per curiam) reversing Fifth Circuit pleading dismissal.
12. `mcp_courtlistener_search` (`type="o"`, `citation="540 U.S. 375"`), `mcp_courtlistener_get_endpoint_item` (`item_id=131151`), and `mcp_courtlistener_read_document` (`opinion_id=131151`, chunk 0) — read *Castro v. United States*, 540 U.S. 375 (2003) on recharacterization of *pro se* prisoner filings.
13. `mcp_courtlistener_search` (`type="o"`, `case_name="Millbrook v. United States"`) and `mcp_courtlistener_read_document` (`opinion_id=856345`, chunk 0) — read *Millbrook v. United States*, 569 U.S. 50 (2013) (9–0, per Thomas, J.) reversing dismissal of a *pro se* federal prisoner's FTCA suit.
14. `mcp_courtlistener_search` (`type="o"`, `case_name="Martin v. United States"`), `mcp_courtlistener_get_endpoint_item` (`item_id=10603452`), and `mcp_courtlistener_read_document` (`opinion_id=11070040`, chunks 0, 1) — read *Martin v. United States*, 605 U.S. 395 (2025) (9–0, per Gorsuch, J.) vacating and remanding an FTCA dismissal.
15. Additional CourtListener citation/case searches for *Preiser v. Rodriguez* (411 U.S. 475), *Wilkinson v. Dotson* (544 U.S. 74), *Skinner v. Switzer* (562 U.S. 521), *Bostock v. Clayton County* (590 U.S. 644), *Brownback v. King* (592 U.S. 209), *Santos-Zacaria v. Garland* (598 U.S. 411), *Lomax v. Ortiz-Marquez* (590 U.S. 595), and *Ali v. Federal Bureau of Prisons* (552 U.S. 214).

## 3. Web Searches

None.
