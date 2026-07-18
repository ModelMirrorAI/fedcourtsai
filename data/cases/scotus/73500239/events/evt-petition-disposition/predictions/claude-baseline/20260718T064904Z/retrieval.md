# Retrieval log — scotus/73500239 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Mode: `forward` (pending petition; retrieval unrestricted).

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
   - Returned 8 recent resolved SCOTUS priors (mix of granted/denied/dismissed).
     No topic filter exists for SCOTUS rows, so the results were generic and
     did not materially shape the forecast; base rates were taken from the
     committed statpack instead.

## Committed base rates

2. `metrics/statpack.md` — "Modern discretionary-cert petitions by
   disposition", originating-circuit (ca6), relist-count, CVSG, and per-Term
   tables.
3. `metrics/statpack.json` — Term 2025 per-fee-class detail (paid grant rate
   5.4%, IFP 1.1%). No salience-band section is present in the current
   statpack.

## CourtListener MCP

4. `search(type=o, court=scotus, q='Garcetti "academic freedom" certiorari
   professor', filed_after=2024-01-01)` — 0 results. Confirms no recent
   SCOTUS merits decision and no obvious pending vehicle on the
   Garcetti/academic-freedom question (bears on hold/GVR probability, which I
   set to negligible).
5. `search(type=o, court=ca6, q='Pesta')` — 0 results. The unpublished Sixth
   Circuit opinion (2025 WL 3094128) is not in CourtListener's opinion index;
   I relied on the petition's account of the decision below.

No web searches were performed. Nothing retrieved surfaced this case's own
disposition (the petition is undecided, distributed for the 9/28/2026
conference).
