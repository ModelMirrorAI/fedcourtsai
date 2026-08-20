# Retrieval log — claude-baseline, run 20260820T181919Z

Beyond the provisioned inputs (snapshot, event.yaml, context.json,
questions-presented.txt, petition.txt, documents.json) and the committed
`metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — stderr: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`.
  Pulled recent granted SCOTUS priors for shape (distribution counts and
  cert-stage amicus/counsel profiles of recent grants). The query surface is
  structured-filter only, so no military-commission-specific prior set could
  be targeted.

## CourtListener MCP lookups

- `search` (opinions, court=cadc, q="mandamus military commission plea
  agreement Mohammad", filed after 2025-01-01) — confirmed the decision below,
  *In re: United States of America*, No. 25-1009 (D.C. Cir., published July
  11, 2025), exists as described in the petition. One call.

## Web searches

None.
