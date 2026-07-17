# Retrieval log — scotus/73275185 · evt-petition-disposition · claude-baseline · 20260717T180352Z

## Corpus lookups (fedcourts CLI)

Both attempts failed — the cell's corpus query sidecar was unreachable, so no
transfer lines were printed:

- `uv run fedcourts query --court scotus --citation "599 U.S. 1"` →
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`
- `uv run fedcourts query --court scotus --disposition gvr` →
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", "Modern cert petitions by originating circuit",
  "Cert petitions by relist count", and "Cert petitions by CVSG status". (No
  salience-band table is present in the committed statpack.)

## CourtListener MCP

None. The cell is a mis-provisioned forward cell whose snapshot already
contains the disposition (see `flags.json`); live retrieval about this case
could only surface more outcome material, so I deliberately made no MCP
calls.

## Web searches

None.
