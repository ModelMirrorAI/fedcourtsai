# Retrieval Log: `scotus/9026000218` (`evt-petition-disposition`)

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. **`uv run fedcourts query --court scotus --docket-number 25-1`**
   - Transfer: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Purpose: Retrieve the docket and disposition record for *James Skinner v. Louisiana*, No. 25-1 (`scotus/73110505`), cited in the Petition (pp. 32–33) as presenting the identical question presented last Term. Confirmed that *Skinner* had 7 amicus briefs, was distributed 9 times, and was `denied` on `2026-03-30`.

2. **`uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`**
   - Transfer: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Purpose: Inspect recent 2020s SCOTUS cert grants (`26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`) and compare their distribution counts, party/counsel profiles, and amicus activity against *Matthews v. Louisiana*.

3. **`uv run fedcourts query --court scotus --citation "607 U.S. 213"`**
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Purpose: Check corpus citation index for *Klein v. Martin*, 607 U.S. 213 (2026) (returned note to use CourtListener MCP server for single-case citation lookup).

4. **`uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`**
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached from prior ranged reads)
   - Purpose: Inspect recent 2020s SCOTUS GVR dispositions (`25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`, `25-7462`, `25-7532`, `26-48`) to compare procedural posture and distribution counts.

5. **`uv run fedcourts query --court scotus --docket-number 22-77`**
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Retrieve the docket and disposition record for *David Brown v. Louisiana*, No. 22-77 (`scotus/67123792`), another recent Louisiana *Brady* materiality petition cited in the Petition (pp. 3, 21, 32). Confirmed that *Brown* was a capital case with multiple amici, distributed 7 times, and `denied` on `2023-04-03`.

6. **`uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`**
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached)
   - Purpose: Sample recent 2020s denied SCOTUS dockets.

---

## 2. CourtListener MCP Lookups

1. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Klein v. Martin"`) & `mcp_courtlistener_read_document` (`opinion_id=11246089`, `chunk_index=0`)**
   - Retrieved *Klein v. Martin*, No. 25-51, 607 U.S. ___ (decided Jan. 26, 2026) (per curiam) (`cluster_id: 10779476`, `opinion_id: 11246089`), cited on page 33 of the Petition. Confirmed that the Court summarily reversed the Fourth Circuit's grant of habeas relief on a *Brady* materiality claim where the state court had found no reasonable probability of a different result in light of strong trial evidence.

2. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Skinner v. Louisiana"` / `docket_number="25-1"` / `q="Skinner Louisiana Brady"`)**
   - Checked whether any dissent or statement respecting the denial of certiorari was published when the Court denied *James Skinner v. Louisiana*, No. 25-1, on March 30, 2026; no separate opinion was published.
