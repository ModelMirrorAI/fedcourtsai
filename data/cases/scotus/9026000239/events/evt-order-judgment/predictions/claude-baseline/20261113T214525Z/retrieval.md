# Retrieval log

Beyond the provisioned record and the committed `metrics/statpack.md`:

**Corpus (`fedcourts`)**
1. `uv run fedcourts paths --court scotus --docket 9026000239 --event evt-order-judgment --role predictor` — resolved the case, corpus and event paths.
2. `uv run fedcourts query --help` — read the filter surface.
3. `uv run fedcourts query --court scotus --citation "585 U.S. 667" --limit 3` — empty; note line said only 195 SCOTUS rows carry a citation. `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
4. `uv run fedcourts query --court scotus --citation "596 U.S. 543" --limit 3` — empty, same note. `ranged corpus reads: 0 GET(s), 0 byte(s)`
5. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`modern` is not an era token); no rows.
6. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — five rows, the first being this docket's own row (I saw only its caption and counsel fields in truncated output), the others unrelated recent grants. Not used in the forecast. `ranged corpus reads: 30 GET(s), 7798784 byte(s)`

**CourtListener MCP**
1. `search` (opinions, scotus, case_name "Al Otro Lado") — one result, *Mullin v. Al Otro Lado*, decided 2026-06-25, opinion 11347762.
2. `read_document` opinion 11347762, chunk 0 — syllabus: an alien standing in Mexico has not "arrive[d] in the United States"; Ninth Circuit reversed.
3. `search_document` opinion 11347762, "delivered the opinion" — lineup: Alito for the Court, joined by Roberts, Thomas, Gorsuch, Kavanaugh, Barrett; Thomas concurring; Sotomayor dissenting joined by Kagan and Jackson; Jackson dissenting.
4. `search` (opinions, scotus, `"1252(f)(1)" OR "1182(f)"`, filed after 2025-06-01) — zero results.
5. `search` (opinions, scotus, `"Aleman Gonzalez" immigration`, filed after 2025-06-01) — one result, *Al Otro Lado* again.

No web searches. No lookup of this case's docket beyond the snapshot.
