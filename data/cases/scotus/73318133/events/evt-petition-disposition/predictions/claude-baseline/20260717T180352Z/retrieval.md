# Retrieval log — scotus/73318133 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Mode: `forward` (`record/context.json`); no `DECIDED_BEFORE` clock.

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
   - Purpose: recent resolved SCOTUS priors for context. The granted rows returned
     (e.g. Monsanto v. Salas, Petersen v. Doe, Viramontes v. Cook County) are all
     counseled, multi-distribution/relisted, high-salience petitions — a profile
     this pro se, single-distribution petition does not share. Denied rows at
     distribution_count 3 with prominent counsel reinforce how selective grants are.

## CourtListener MCP lookups

1. `get_endpoint_item(endpoint_id="dockets", item_id=73318133, fields=[id, case_name, docket_number, court_id, date_filed, date_terminated, date_last_filing])`
   - Result: docket 25-1270, `date_terminated: null` — the petition remains
     pending, confirming the forward-mode premise. No disposition was surfaced.

## Other

- Committed `metrics/statpack.md` for base rates (relist-count, CVSG, circuit,
  and per-Term cert tables).
- No web searches.
