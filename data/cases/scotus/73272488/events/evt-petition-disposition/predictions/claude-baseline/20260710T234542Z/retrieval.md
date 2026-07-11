# Retrieval log — claude-baseline / 20260710T234542Z

Mode: `forward` (retrieval unrestricted; no outcome exists to leak).

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "Jackson v. Virginia" --citation "In re Winship" --limit 5`
   - stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Returned no rows (citation overlap found no resolved SCOTUS priors).
2. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Returned 8 recent resolved cert dockets (7 denied, 1 granted —
     consistent with the low modern grant base rate; none on the Rule 29
     preservation question).

## Base rates

- Read the committed `metrics/statpack.md`. Used the overall SCOTUS resolved
  base rate (granted 1.4%, denied 4.4%, other 78.4%). Note: the "Modern
  discretionary-cert petitions by disposition" section the task prompt points
  to is not present in the committed statpack (flagged in `flags.json`); I
  used the prompt's own characterization that the modern cert grant rate is a
  few percent.

## CourtListener MCP

- Attempted `mcp__courtlistener__search` (docket lookup for the companion
  petition *Tovar v. United States*, No. 25-6344) twice; both calls failed
  server-side with `REDIS_URL is not set; cannot access session store`. No
  CourtListener data was retrieved; proceeded on the provisioned inputs.

## Web searches

- None.
