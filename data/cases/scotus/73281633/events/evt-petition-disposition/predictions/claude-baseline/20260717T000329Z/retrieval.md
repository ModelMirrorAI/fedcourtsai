# Retrieval log — scotus/73281633 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Mode: `forward` (record/context.json). Retrieval beyond the provisioned inputs:

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "447 U.S. 557" --era 2020s`
  — searched for resolved SCOTUS priors citing *Central Hudson*; returned no
  rows. Run twice (once to capture stdout, once stderr); each invocation
  reported: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`.
- Committed base rates: `metrics/statpack.md` (modern discretionary-cert
  sections) and `metrics/statpack.json` (per-Term per-fee-class detail — paid
  est. grant rate 5.4% for Term 2025, 6.9% for Term 2024).

## CourtListener MCP

- `search` (type=o): `"dietary supplement" "weight loss" minors "First
  Amendment" sale` — 3 results: the Second Circuit decision below (CRN v.
  James, 2025-11-13) and two unrelated *Metabolife v. Wornick* defamation
  opinions (1999/2001). Confirmed no parallel litigation over comparable
  supplement age-restriction statutes in other circuits; surfaced nothing
  about this petition's disposition (none exists — conference is 2026-09-28).

## Web

- None.
