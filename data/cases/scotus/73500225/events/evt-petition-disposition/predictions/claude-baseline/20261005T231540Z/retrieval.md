# Retrieval log

## Corpus (`fedcourts`, local service / ranged reads)

- `uv run fedcourts query --court scotus --citation "597 U.S. 1" --limit 5` — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; returned the citation-coverage `note:` (only 200 SCOTUS rows carry reporter cites), no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6` — `ranged corpus reads: 25 GET(s), 6422528 byte(s)`; six recent granted rows (none Second Amendment), used only for the shape of recent grants.
- `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 6` — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`.
- `uv run fedcourts query --court scotus --era 2020s --include-open --limit 400` — `ranged corpus reads: 0 GET(s), 0 byte(s)`; name-filtered for Kipke / Novotny / Schoenthal, no matches.
- `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 80` — `ranged corpus reads: 55 GET(s), 14417920 byte(s)`; caption scan for Second Amendment GVRs after *Wolford*, no matches.
- `uv run fedcourts open-events --court scotus --docket 73281690` (Maryland's companion petition No. 25-1206) — no output.
- `uv run fedcourts open-events --court scotus --docket 73278986` (Schoenthal, No. 25-541) — no output.
- `uv run fedcourts conference-set` — failed: `no corpus at corpus/corpus.db` (needs a pulled corpus; not available in the cell).

## CourtListener MCP

- `search` (opinions, scotus, "Wolford v. Lopez", filed after 2026-01-01) — found *Wolford v. Lopez*, No. 24-1046, decided 2026-06-25, opinion id 11347760.
- `read_document` opinion 11347760, chunks 0–1 and 2 (syllabus and lineup): Hawaii's private-property default rule held unconstitutional; Alito, J., for a 6-3 Court; Barrett concurrence; Kagan and Jackson dissents; Ninth Circuit reversed and remanded.
- `search` (dockets, scotus, docket_number 25-1206) — no results.
- `search` (dockets, scotus, docket_number 25-541) — no results.
- `search` (opinions, ca3, Koons en banc, filed after 2025-06-01) — only the September 2025 Koons orders and an unrelated July 2026 en banc decision; no Koons en banc merits decision.
- `call_endpoint` dockets (scotus, docket_number 25-1206) — docket id 73281690, *Wes Moore, Governor of Maryland v. Susannah Warner Kipke*, filed 2026-04-22, not terminated.
- `search` (opinions, scotus, "Schoenthal Raoul", filed after 2026-01-01) — no results (order-list denials are not indexed as opinions).
- `search` (dockets, scotus, Kipke / Novotny / Frey / "sensitive places", filed after 2026-01-01) — no results.
- `call_endpoint` docket-entries (docket 73281690) — no entries held.
- `call_endpoint` dockets (scotus, docket_number 25-541) — docket id 73278986, *Schoenthal v. Raoul*, filed 2025-11-04, `date_terminated` null in CourtListener (the petition itself reports the April 6, 2026 denial).

No web searches. Nothing retrieved concerned this petition's own disposition.
