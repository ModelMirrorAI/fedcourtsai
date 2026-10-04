# Retrieval log

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   Returned eight recent OT2026 rows (mostly emergency applications plus three
   granted paid petitions, 25-1131, 25-1349 and 26-104). Used only to confirm
   that grants from the September 28, 2026 long conference have already been
   recorded; no row concerned this case.

## CourtListener MCP lookups

None.

## Web searches

None.

## Committed base rates

`metrics/statpack.md`: "Segment base rate by salience band (sal-v4)",
"Cert petitions by relist count (paid scored segment)", "Cert petitions by
CVSG status (paid scored segment)", "Petitions by originating court".
