# Retrieval log

- WebFetch: supremecourt.gov PDF of appellees' Motion to Dismiss (26-118, filed 2026-09-18). The fetch tool could not read the PDF, so I extracted the saved copy with `uv run fedcourts pdf-text` (27 pages). It argues mootness (the PI was limited to the 2026 elections) and opposes summary reversal.
- WebFetch: supremecourt.gov docket page for 26-118. The entries match the snapshot; the last is DISTRIBUTED for Conference of 11/13/2026.
- Bash `curl` + `uv run fedcourts pdf-text`: Alabama's response to the motion to dismiss (2026-09-29). It argues the appeal is not moot, asks for summary reversal, and requests Munsingwear vacatur in the alternative.
- `uv run fedcourts query --court scotus --docket-number 25-273` → `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Prior Allen v. Singleton appeal; disposition `gvr`.
- `uv run fedcourts query --court scotus --docket-number 26-116` → `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Caster companion; pending.
- `uv run fedcourts query --court scotus --era modern --disposition gvr --limit 3` → usage error (bad era token); no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 3` → `ranged corpus reads: 1066 GET(s), 279445504 byte(s)`; no rows printed.
- Read `metrics/statpack.md`: the modern-cert, relist-count, CVSG, amicus and salience-band (sal-v8) sections.
