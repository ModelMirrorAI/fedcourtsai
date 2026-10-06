# Retrieval log

Mode: forward (no retrieval clock). Roughly 10 retrieval calls.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 48 GET(s), 12451840 byte(s)` — 20 rows, used for shape
  only (one capital grant in the sample, Nelsen v. Pike, ca6, 2026-09-30).
- `metrics/statpack.md` (committed): "Modern discretionary-cert petitions by
  disposition", "by originating circuit", "by relist count", "by CVSG status", "by
  capital-case marking", "by salience band", "SCOTUS cert petitions by Term", and
  "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

- `search` type=o, court=ca5, q="Vasquez Guerrero successive 2244 diligence",
  filed 2025-11-01 to 2026-01-15 — 0 results.
- `search` type=o, court=ca5, docket_number=25-70005 — 0 results.

## Web fetches (this docket's own filings and the companion docket)

- Motion to defer consideration (Aug 14, 2026) — supremecourt.gov DocketPDF; text
  extracted locally with pypdf.
- Response in opposition to the motion to defer (Aug 24, 2026) — fetched; the PDF has no
  text layer, so only the fetch tool's thin summary was available (it asks that the motion
  be denied).
- Letter from petitioner's counsel to the Clerk (Sep 17, 2026) — text extracted locally.
- Reply brief (Aug 11, 2026) — text extracted locally.
- Docket page for No. 26-353 (companion petition): docketed Sep 16, 2026; response due
  Oct 16, 2026; no other entries.

No search touched this petition's disposition; no `data/qp-topics/` path was read.
