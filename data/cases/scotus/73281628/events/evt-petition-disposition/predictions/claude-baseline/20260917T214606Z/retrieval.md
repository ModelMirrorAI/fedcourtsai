# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-17.json`, `record/documents/documents.json`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, the event definition, `metrics/statpack.md` (modern-cert disposition, relist, CVSG, salience-band, per-Term, and sal-v4 segment tables), `docs/salience.md` (band feature definitions).

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 12`
  - stderr: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
  - Returned 12 recent GVR priors (mostly merits GVRs against the United States); distribution counts of 2–4 at GVR, used only for the shape of the relist claim.

## CourtListener MCP lookups

1. `search` type=o court=scotus q="Munsingwear vacatur moot" filed_after=2022-10-01 — 2 results (Acheson Hotels v. Laufer, twice).
2. `search` type=o court=scotus q="Munsingwear" filed_after=2018-01-01 — 21 results: the Court's recent Munsingwear orders and opinions (West Virginia v. B.P.J. 2026, Acheson, Arizona v. San Francisco, Beers v. Barr, NYSRPA v. NYC, Bank of America v. Miami, Gray v. Wilkie, Azar v. Garza, and several 2018–2019 vacatur orders). Titles only; no body read.
3. `search` type=o courts=ca1–ca11,cadc q="Jones v. Hendrix" AND "Suspension Clause" AND "saving clause" AND constitutional filed_after=2023-06-22 published — 0 results.
4. `search` type=o courts=ca1–ca11,cadc q=Hendrix "Suspension Clause" 2255(e) 2241 filed_after=2023-06-22 — 0 results.
5. `search` type=o court=ca4 case_name="Bell v. Streeval" — 1 result (published, 2025-08-06, No. 22-6189); confirmed the decision below is indexed. Not opened.

No web searches. Nothing retrieved concerned this petition's disposition, which does not yet exist.
