# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   Returned four substantive interim applications (election-law and agency
   stay matters) and one pending petition (Jouppi v. Alaska). Not analogous;
   did not inform the number.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Returned five substantive interim applications. Not analogous; did not
   inform the number.

An initial attempt with a free-text `--text` flag was rejected by the CLI (no
such option) and made no corpus read.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Modern cert petitions by originating circuit" (`fla` bucket), "Cert
  petitions by relist count (paid scored segment)", "Cert petitions by CVSG
  status (paid scored segment)", "Cert petitions by salience band", "SCOTUS
  cert petitions by Term", and "Segment base rate by salience band (sal-v4)"
  (pooled the `baseline` bracketed `reached` rate over OT2017-OT2024).

## CourtListener MCP lookups (forward mode)

1. `search` (type `o`, court `fladistctapp`, q "Campo v. Uber Technologies"):
   one hit, cluster 10306598, Yesit Campo, Etc. v. Uber Technologies, Inc.,
   filed 2025-01-02, No. 3D2023-0802.
2. `get_endpoint_item` dockets/73363395: docket 25-1292, filed 2026-05-19,
   `date_terminated` null, last modified 2026-06-17. Confirms the petition is
   pending; no disposition surfaced.
3. `get_endpoint_item` clusters/10306598: sub-opinion 10773186, published.
4. `read_document` opinion 10773186, chunks 0 and 1 (12,000-char chunks;
   15,905 chars total): the Third DCA's affirmance of summary judgment for
   Uber on state-law scope-of-employment grounds. No federal question
   addressed.

## Web searches

None.
