# Retrieval log

Beyond the provisioned inputs (snapshot `2026-10-06.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 6`
   stderr: `ranged corpus reads: 24 GET(s), 6160384 byte(s)`
   Returned six recent SCOTUS GVR rows (election-law and federal criminal petitions); none analogous to this case; used only as a sanity check on the GVR label's presence in the modern slice.
2. `uv run fedcourts query --court scotus --citation '577 U.S. 411' --limit 3`
   stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)` followed by a `note:` line that the citation column is sparse (200 rows in scope) — no rows returned. Caetano's content was taken from the petition and general knowledge instead.

## CourtListener MCP

None. The MCP search tool was loaded but not called; the petition appendix carried the Second Circuit summary order in full, and the companion-case status was answered by web search.

## Web searches (engine-surfaced, forward mode)

1. `Viramontes v. Cook County 25-238 certiorari granted June 30 2026 question presented argument` — confirmed grant on June 30, 2026, consolidation with *Grant v. Higgins* (No. 25-566), limited QP on AR-15-platform rifles "in common use," argument set for December 2, 2026 (scotusblog.com, oyez.org, supremecourt.gov docket 25-238, jurist.org, saf.org).
2. `Calce v. City of New York 26-46 Supreme Court stun gun petition response requested` — commentary on the September 8 call for a response after the City's waiver (jonathanturley.org, dailycaller.com, theoutdoorwire.com, usacarry.com, westernjournal.com, thegunmag.com). No disposition surfaced; the petition is reported as pending.
3. `Wolford v. Lopez Supreme Court decision June 25 2026 holding Hawaii plain text "arms" Barrett concurrence` — confirmed the June 25, 2026 decision striking Hawaii's private-property default rule, Alito majority, Barrett concurrence joined in part by Thomas and Gorsuch (supremecourt.gov opinion 24-1046, scotusblog.com, everytown.org, oyez.org).

Total: 2 corpus queries, 3 web searches, 0 MCP calls.
