# Retrieval log — scotus/73281630, evt-petition-disposition, claude-baseline, 20260717T000329Z

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing exists yet —
the petition is pending, distributed for the 2026-09-28 conference).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "Tinker v. Des Moines" --citation "Bethel Sch. Dist. No. 403 v. Fraser" --citation "Mahanoy Area Sch. Dist. v. B.L." --limit 8`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - 0 rows — no citation-matched student-speech priors in the corpus.
2. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - 5 recent-era rows (Monsanto pair granted 2026-06-30, Petersen, McCoy,
     WV Citizens Defense League denied 2026-06-30) — used only as loose context
     on current-Term grant/deny flow; none topically similar.

## Base rates

- Committed `metrics/statpack.md` and `metrics/statpack.json`: modern
  discretionary-cert disposition split, originating-circuit cut (ca6),
  relist/CVSG cuts, and Term-2025 per-fee-class detail (paid est. grant rate
  5.4%, IFP 1.1%). No salience-band table is present in the committed statpack.

## CourtListener MCP lookups

1. `search(type=d, q="Tri County Area Schools", court=scotus)` — 0 results
   (SCOTUS e-docket not in RECAP; expected). Pendency instead confirmed from
   the provisioned snapshot fetched 2026-07-16.
2. `search(type=o, q='"L.M." "Town of Middleborough" student speech shirt')` —
   0 results; could not confirm the *L.M. v. Middleborough* cert denial via
   CourtListener, so `reasoning.md` cites it as carried from training
   knowledge (it predates this petition; forward-legitimate context).

## Web searches

None.
