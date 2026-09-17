# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   Returned four substantive stay applications (26A326, 26A274, 26A203, 26A124) and one relisted paid petition (25-246 Jouppi v. Alaska, distribution count 3). Not comparable to this petition; used only to confirm the tool path worked.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned five denied stay applications (26A332, 26A353, 26A305, 26A306, 26A296). Not comparable; no case-level prior taken from them.

(An initial invocation with a free-text argument was rejected by the CLI, which is a structured filter and takes no search phrase; it made no corpus read.)

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (ca11 row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (baseline column, OT2017 through OT2024 pooled).

## CourtListener MCP lookups

1. `search` type `o`, court `ca11`, q `Foley "Orange County" "60(b)(4)"`, filed after 2025-01-01: 0 results.
2. `search` type `o`, court `ca11`, docket number `24-14143`: 0 results.

Neither search sought or surfaced this petition's disposition. No web searches.
