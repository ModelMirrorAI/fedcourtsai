# Retrieval log — scotus/73363395 / evt-petition-disposition / claude-baseline / 20260718T000130Z

## Corpus lookups

- `uv run fedcourts query --court scotus --era modern --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No ranged corpus reads
  occurred. Fell back to the committed statpack per the degradation rule.

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", "Cert petitions by relist count", "Cert
  petitions by CVSG status", "Petitions by originating court (incl. state
  courts)", and the per-Term table. (This checkout's statpack carries no
  salience-band section.)

## CourtListener MCP

- None. Forward-mode cell; the snapshot is one day old and the petition's
  first conference (September 28, 2026) has not occurred, so live docket
  retrieval could not add signal to this call.

## Web searches

- None.
