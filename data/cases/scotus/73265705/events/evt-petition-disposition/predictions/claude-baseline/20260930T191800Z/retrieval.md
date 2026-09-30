# Retrieval log

## Corpus tooling
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` — stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`. Returned recency-ranked 2026 grants (immigration and election applications), none topical to this petition; used only to confirm the surface was live.
- `metrics/statpack.md` (committed): Modern discretionary-cert base rate; relist-count and CVSG cuts (paid scored segment); "Segment base rate by salience band (sal-v4)" — pooled the `elevated` bracketed `reached` figures for Terms 2017–2024 (484.4/2810 = 17.2%).

## CourtListener MCP
- `search` (type `o`, court `cafc`, q `"settled expectations" "inter partes review" mandamus institution`, filed after 2025-06-01) — 0 results.

## Web fetches (forward mode; this case is undecided, conference set for 2026-10-16)
- supremecourt.gov docket 25-1230 — confirmed entries match the snapshot through the 9/30 distribution; obtained the URL of Google's 9/29 reply brief.
- Google's reply brief PDF (supremecourt.gov DocketPDF/25/25-1230/425930) — extracted locally with pypdf and read in full.
- supremecourt.gov docket 26-73 (Intel Corp. v. Squires) — petition filed 7/13/2026, seven amicus briefs, government response due 10/14/2026.
- supremecourt.gov docket 26-198 (Kahoot! AS v. Interstellar Inc.) — petition filed 7/24/2026, six amicus briefs, government response due 10/16/2026.
- fedcircuitblog.com petition page for Google v. VirtaMove — status and amicus list only; no grant commentary.

## Web searches
- "Google v. VirtaMove Supreme Court cert petition "settled expectations" 25-1230" — SCOTUSblog case page, Fed Circuit Blog, practitioner commentary; no disposition (petition pending).
- "Intel v. Squires 26-73 ... Apple v. Squires Federal Circuit 2026" — Intel petition QP (whether § 314(d) bars review of PTO institution rules), Apple v. Squires (Fed. Cir. Feb. 13, 2026) holding the Fintiv framework exempt from notice-and-comment.
