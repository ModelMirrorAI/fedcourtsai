# Retrieval log

## Corpus

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5 --corpus-backend service`
  - stderr: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
  - Returned five recent granted SCOTUS priors (Jouppi v. Alaska 25-246;
    Viramontes v. Cook County 25-238; Grant v. Higgins 25-566; Grand v.
    University Heights 25-965; Apple v. Epic 25-1311). General context on
    recent grant shapes only — none is a close comparator (the query surface
    has no filter for petitioner class or statute-invalidation posture).

## CourtListener MCP

- `search` (type=d, court=scotus, docket_number=26-199) — 0 results. The
  Authority's companion petition is not in the RECAP docket index.
- `search` (type=d, court=scotus, docket_number=25-1325) — 0 results. The
  Oklahoma challengers' petition likewise absent.

Current SCOTUS paid dockets are evidently not indexed there; the companion
posture used in the prediction comes from the provisioned petition's own
related-proceedings statement instead.

## Committed references (not live retrieval)

- `metrics/statpack.md` — federal-band segment table (sal-v3), modern-cert
  base rates, relist and CVSG cuts.

No web searches. No retrieval touching this petition's own disposition (none
exists; the case is pending).
