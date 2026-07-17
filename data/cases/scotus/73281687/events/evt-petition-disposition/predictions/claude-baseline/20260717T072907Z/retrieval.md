# Retrieval log — scotus/73281687, evt-petition-disposition, claude-baseline, 20260717T072907Z

Cell mode: `forward` (retrieval unrestricted; no outcome exists to leak).

## Corpus lookups (`fedcourts` CLI)

All four `query` attempts returned **zero rows**; each printed the same
ranged-read stats line.

1. `uv run fedcourts query --court scotus --topic "Fourth Amendment warrant oath probable cause hearsay overrule precedent" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows.
2. `uv run fedcourts query --court scotus --topic "Fourth Amendment search warrant" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows.
3. `uv run fedcourts query --court scotus --topic "Fourth Amendment" --limit 5` and
   `uv run fedcourts query --court scotus --topic "warrant" --include-open --limit 5`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` each — 0 rows.
4. `uv run fedcourts query --court scotus --topic "police officer civil rights" --disposition granted --limit 5`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows.

Base rates came from the committed `metrics/statpack.md` (modern
discretionary-cert disposition table, originating-circuit, relist, CVSG, and
per-Term cuts). The statpack build in the repo carries no "Segment base rate
by salience band" section, so no band anchor was available.

## CourtListener MCP lookups

1. `search` (opinions, scotus): `"Broken Fourth Amendment Oath" OR (Sacharoff AND oath)` — 0 results.
2. `search` (opinions, scotus, filed after 2015): `"oath or affirmation" AND "firsthand knowledge" AND warrant` — 0 results.

Both were checks for any Justice-level signal inviting reconsideration of
*Jones v. United States* (1960); none exists.

## Web fetches

1. `https://www.supremecourt.gov/DocketPDF/25/25-1205/416485/20260714161739468_2026.07.08%20Respondent%20Brief%20In%20Opposition%20to%20Cert.pdf`
   — the respondent's brief in opposition (filed Jul 14, 2026; on the docket
   snapshot but not provisioned under `record/documents/`). Downloaded and
   text-extracted locally (pypdf); used for the vehicle analysis in
   `reasoning.md`. This is the case's own pre-decision record, not outcome
   material.
