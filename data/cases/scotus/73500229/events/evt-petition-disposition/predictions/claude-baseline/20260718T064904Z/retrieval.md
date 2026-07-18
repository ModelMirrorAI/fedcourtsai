# Retrieval log — scotus/73500229 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-18.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`,
`record/context.json` — mode `forward`) and the committed
`metrics/statpack.md` / `metrics/statpack.json` (paid-class, per-circuit,
relist, and CVSG base rates):

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   — recent granted-petition priors, to see what docket signals (distribution
   counts, counsel) accompany grants.
   stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`

## CourtListener MCP lookups

1. `search(type=d, court=scotus, case_name="Curtis v. Inslee")` — looked for a
   companion cert petition from the published Ninth Circuit companion case.
   0 results (SCOTUS dockets are not in the RECAP index).
2. `search(type=d, court=scotus, q="Inslee")` — same purpose, broader. 0 results.
3. `search(type=o, q="\"Curtis v. Inslee\" vaccine")` — confirmed the published
   companion: *Curtis v. Inslee*, 9th Cir. No. 24-1869, filed 2025-10-06;
   the other hits (10th Cir. *Sweeney*, *Timken*, Oct. 2025) are Title VII
   religious-exemption vaccine cases, not this EUA-preemption theory — i.e.
   no sign of a circuit split on the QPs.

No web searches. I did not seek this case's own disposition (none exists —
the petition is pending, response due 2026-08-13).
