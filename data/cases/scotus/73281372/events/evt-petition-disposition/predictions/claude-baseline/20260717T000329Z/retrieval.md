# Retrieval log — scotus/73281372 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Mode: `forward` (record/context.json). Retrieval beyond the provisioned inputs
was limited to corpus tooling and the committed statpack; no CourtListener MCP
calls and no web searches were made — the provisioned petition, brief in
opposition, and full docket snapshot were sufficient, and the case's own
outcome does not yet exist (conference set for 2026-09-28).

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "583 U.S. 366" --citation "561 U.S. 247" --citation "601 F.3d 319" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --topic bankruptcy --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --citation "11 U.S.C. 546" --limit 5`
   → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

No similar resolved priors surfaced; the prediction anchors on the committed
`metrics/statpack.md` base rates instead (Term-2025 paid-class grant rate,
relist/CVSG cuts, originating-circuit cut).
