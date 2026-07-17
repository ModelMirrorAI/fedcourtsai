# Retrieval log — scotus/73281674, evt-petition-disposition, claude-baseline, 20260717T072907Z

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "Loper Bright Enterprises v. Raimondo" --citation "SEC v. Jarkesy" --citation "NLRB v. Starbucks Corp." --limit 8`
   — no rows returned.
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --citation "29 U.S.C. 158" --citation "NLRB" --limit 8`
   — no rows returned.
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", originating-circuit cut (ca3), relist-count cut,
  CVSG cut, and the per-Term table (Terms 2023–2025). No salience-band table
  present in this statpack.

## CourtListener MCP lookups

1. `get_endpoint_item(endpoint_id="dockets", item_id=73281674, fields=[case_name, docket_number, date_terminated, date_filed, date_last_filing, court_id])`
   — confirmed the docket is not terminated (`date_terminated: null`), i.e.
   the case is genuinely pending; forward-mode sanity check only. No search
   for the case's outcome was made (none exists).

## Web searches

None.
