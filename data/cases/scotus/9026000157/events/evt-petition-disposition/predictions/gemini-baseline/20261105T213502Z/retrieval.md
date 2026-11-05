# Retrieval Log: `scotus/9026000157` (`evt-petition-disposition`)

## 1. Corpus Priors (`uv run fedcourts query`)

All corpus queries executed during this run and their exact transfer lines reported on stderr:

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Purpose: Retrieve recent granted SCOTUS petitions in the 2020s era to check for any pending or recently granted First Amendment / church-autonomy companion cases (spotted `scotus/73281619`, *Missionaries of Saint John the Baptist, Inc. v. Joel Frederic, et ux.*, No. 25-1131, granted Oct. 1, 2026).

2. `uv run fedcourts query --court scotus --docket-number 25-1131 --full`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Purpose: Inspect docket metadata for No. 25-1131 (*Missionaries of Saint John the Baptist, Inc. v. Frederic*) from the Supreme Court of Kentucky (`2024-SC-0006`) to determine whether it overlaps with the church-autonomy question in No. 26-157.

3. `uv run fedcourts query --court scotus --docket-number 25-849`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Inspect the corpus record for *United States Conference of Catholic Bishops v. David O'Connell*, No. 25-849 (`scotus/73280351`), cited in the petition (Pet. 11, 29–30). Confirmed that No. 25-849 was denied on May 26, 2026 after 4 distributions despite extensive amicus support (including overlapping amici Sharon Fast Gustafson / Rachel N. Morrison via Erika Lauren Maley and the Anglican Church in North America).

4. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 20 --judge "Parraguirre"`
   - Transfer: `ranged corpus reads: 681 GET(s), 178323456 byte(s)`
   - Purpose: Check for any other SCOTUS petitions from opinions authored by Justice Parraguirre of the Supreme Court of Nevada.

5. `uv run fedcourts query --court scotus --citation "591 U.S. 732" --limit 10`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Purpose: Probe citation lookup on `591 U.S. 732` (*Our Lady of Guadalupe*).

6. `uv run fedcourts query --court scotus --docket-number 25A1307`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Purpose: Inspect the linked time-extension application (`25A1307`, `scotus/73389315`) granted by Justice Kagan on May 26, 2026.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Missionaries of Saint John the Baptist v. Joel Frederic"`) and `mcp_courtlistener_read_document` (`opinion_id=11227369`, chunk 0):
   - Verified the Kentucky Supreme Court's December 18, 2025 opinion (`2024-SC-0006-DG`), confirming that *Missionaries of Saint John the Baptist* is a RLUIPA land-use / conditional-use-permit zoning case regarding a religious grotto, not a church-autonomy or *Jones v. Wolf* neutral-principles case.

2. `mcp_courtlistener_search` (`type="o"`, `q=""Lutheran Church" "Christian" "neutral principles""`) and `mcp_courtlistener_read_document` (`opinion_id=11337673`, chunk 0):
   - Verified the Fifth Circuit's June 4, 2026 opinion in *The Lutheran Church—Missouri Synod v. Christian*, No. 25-50130 (`178 F.4th 193`), authored by Judge Edith Jones, which reversed a district court's secular corporate-law reading of church governance documents and held that the neutral-principles property exception does not permit civil courts to adjudicate church hierarchy and internal governance.

3. `mcp_courtlistener_search` (`type="o"`, `q=""McRaney" "North American Mission Board" "church autonomy""`) and `mcp_courtlistener_search` (`type="o"`, `case_name="Singh v. Second Judicial District Court"`):
   - Checked Fifth Circuit *McRaney* opinions and confirmed that the Nevada Supreme Court opinion below (`586 P.3d 858`, reproduced in full in `record/documents/appendix.txt` at App. 1a–16a) is fully provisioned in the local record.
