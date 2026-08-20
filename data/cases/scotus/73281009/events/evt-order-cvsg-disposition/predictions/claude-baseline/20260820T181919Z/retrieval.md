# Retrieval log

Beyond the provisioned inputs (snapshot `2026-06-30.json`, `event.yaml`,
`record/context.json`, `record/documents/` petition / questions-presented /
brief-in-opposition, and the committed `metrics/statpack.md`):

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --limit 5`
   — recent granted-petition priors (shape check on distribution counts and
   grant timing).
   stderr: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
2. `uv run fedcourts query --court scotus --limit 40` (rows filtered locally
   for non-null `cvsg_date`; none of the 40 recency-ranked rows carried one).
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)

## Web searches (forward mode, unrestricted)

1. "Baxter v. Philadelphia Board of Elections Pennsylvania Supreme Court
   decision mail ballot date requirement" — companion state-case status (the
   BIO's lead vehicle argument). Results: cert. allowed Jan 2025, argued
   September 2025; no decision surfaced.
2. "Pennsylvania Supreme Court Baxter undated mail ballots ruling 2026" —
   confirming no 2026 Baxter decision has issued; results were pre-argument
   coverage and unrelated 2024 rulings.

No CourtListener MCP calls. No search touched this petition's own
disposition, which cannot exist yet (CVSG issued 2026-06-29; the SG has not
filed).
