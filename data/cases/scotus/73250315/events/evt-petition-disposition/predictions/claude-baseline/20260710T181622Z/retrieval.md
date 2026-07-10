# Retrieval log — claude-baseline, run 20260710T181622Z

Beyond the provisioned inputs (snapshot `2026-07-10.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, `event.yaml`, `context.json`):

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --era 2020 --limit 8 --corpus-backend ranged`
   — no rows (wrong era token).
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --citation "875" --limit 8 --corpus-backend ranged`
   — no rows (citation filter matches case citations, not statutes).
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 8 --corpus-backend ranged`
   — 8 modern SCOTUS priors: 7 denied, 1 granted.
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md` (and inspected `metrics/statpack.json`):
  overall SCOTUS resolved base rate other 78.4% / dismissed 15.9% / denied 4.4% /
  granted 1.4%. The "Modern discretionary-cert petitions by disposition" section
  the prompt anchors on is absent from the committed artifact (flagged).

## CourtListener MCP

- Not available in this cell: the configured `courtlistener` server never
  surfaced any tools to tool search. No MCP calls were made; proceeded on the
  provisioned inputs per the degraded-upstream rule.

## Web searches

1. `Nformangum v. United States 25-7259 certiorari indictment structural error`
   — confirmed the petition is listed as pending (certpool.com, Fifth Circuit
   set); no substantive commentary found. No outcome exists (forward mode).
