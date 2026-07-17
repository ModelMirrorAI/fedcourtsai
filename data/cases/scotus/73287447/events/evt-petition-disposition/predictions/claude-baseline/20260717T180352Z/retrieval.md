# Retrieval log — scotus/73287447 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Beyond the provisioned inputs (snapshot, questions-presented.txt, petition.txt,
documents.json, event.yaml, context.json), I consulted:

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  originating-circuit, relist, CVSG, and per-Term tables.
- `metrics/statpack.json` — per-fee-class Term detail (Term 2025 paid
  est. grant rate 5.4%; Term 2024 paid 6.9%). No salience-band section exists
  in this statpack build.

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
   (recent granted-petition priors; sanity check on grant-side docket patterns —
   granted cases show multiple distributions/relists before grant).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`
   — `ranged corpus reads: 145 GET(s), 37879808 byte(s)`
   (full-row field inspection of the same priors).
3. `uv run fedcourts query --court scotus --era 2020s --limit 500`
   — `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
   (attempted lookup of this case's own corpus row for its salience score; not
   in the top-500 ranking, abandoned rather than re-queried).

## CourtListener MCP

4. `search(type=o, court=ca2, q="DirecTV Nexstar antitrust standing")` —
   confirmed the decision below: *DirecTV, LLC v. Nexstar Media Group, Inc.*,
   No. 24-981 (2d Cir.), filed 2025-12-16, published. One result; no
   disposition-revealing material for the pending petition (forward mode).

## Web searches

None.
