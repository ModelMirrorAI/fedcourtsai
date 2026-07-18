# Retrieval log — scotus/73358594 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Cell mode: `forward` (record/context.json).

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — sampled recent granted SCOTUS priors for context.
   stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
2. Committed base rates: `metrics/statpack.md` (modern discretionary-cert
   disposition split, originating-circuit table, relist/CVSG cuts, per-Term
   table) and `metrics/statpack.json` (Term 2025 per-fee-class detail:
   paid ≈ 5.4% grant, IFP ≈ 1.1%).

(A first `fedcourts query` attempt used an unsupported `--query` flag and
errored without reading the corpus; rerun with structured filters only.)

## CourtListener MCP

1. `search` (type=o): `"2302(b)(8)" "gross mismanagement" MSPB "failed to
   consider" disclosure categories` — 4 results (two MSPB precedential
   decisions, two nonprecedential Fed. Cir. dispositions); no evidence of a
   circuit split on the failure-to-adjudicate-both-categories question.

## Web searches

None.

All other inputs were the provisioned snapshot (`record/snapshots/2026-07-17.json`),
`record/documents/questions-presented.txt`, `record/documents/petition.txt`,
`record/documents/documents.json`, and the event definition. No retrieval
touched this case's own disposition (still pending; distributed for the
2026-09-28 conference).
