# Retrieval log — claude-baseline, 20260816T173750Z

Beyond the provisioned inputs (snapshot `2026-08-16.json`; documents:
`petition.txt`, `brief-in-opposition.txt`, `questions-presented.txt`, all
with clean text) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --citation "586 U.S. 146"` (Timbs
  as a would-be prior) — **0 rows returned**; the tool's own note explains
  the citation column is sparse (161 of 590,339 scotus-scope rows).
  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`.
  Not retried.

## Web (forward cell — retrieval unrestricted)

- WebSearch: `Jouppi v. Alaska Supreme Court cert granted excessive fines
  airplane` — confirmed the grant (7/20/2026, without comment), argument
  expected December 2026, and general coverage (SCOTUSblog, Reason,
  NBC News, Constitution Center, Jones Day, IJ case page,
  supremecourt.gov QP report).
- WebFetch: https://www.scotusblog.com/cases/jouppi-v-alaska/ — procedural summary
  (hold after the 12/12/2025 conference; supplemental brief 6/25/2026;
  grant 7/20/2026). No argument date posted yet.

No CourtListener MCP calls were made. Nothing retrieved concerns this
case's own judgment, which does not yet exist; all retrieved material
predates or reports the cert grant, which is settled history for this
merits cell.
