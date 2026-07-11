# Retrieval log — ca11/68975767 evt-appeal-disposition-17 (claude-baseline, 20260711T091155Z)

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court ca11 --topic "3840 Trademark" --corpus-backend ranged`
   — returned no priors (no resolved ca11 trademark cases in the corpus).
   stderr: `ranged corpus reads: 99 GET(s), 25952256 byte(s)`
2. `uv run fedcourts query --court ca11 --corpus-backend ranged`
   — general ca11 resolved priors; dispositions almost uniformly `other`
   (one `denied` in the top 15), confirming the statpack's ca11 cut.
   stderr: `ranged corpus reads: 45 GET(s), 11796480 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md` (by-court cut: ca11 resolved —
  other 95.6%, denied 2.2%, granted 2.2%).

## CourtListener MCP

None. Although this is a `forward` cell, the provisioned snapshot's last
docket entry ("Opinion Issued", 2024-09-24) indicates the appeal has likely
already been decided, so any lookup on this docket or its opinion cluster
risked retrieving the case's own outcome, which the contract forbids. I
predicted from the provisioned snapshot plus the corpus context above.

## Web searches

None.
