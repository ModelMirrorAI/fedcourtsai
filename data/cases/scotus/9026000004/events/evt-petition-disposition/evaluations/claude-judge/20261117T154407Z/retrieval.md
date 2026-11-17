# Retrieval log

Provisioned inputs read: the event, outcome, case-level `record/` (context, the 2026-11-16 snapshot, petition, brief in opposition, document manifest) and the three blinded candidates.

Corpus lookups, both to check priors a candidate cited (not for facts about this case):

- `uv run fedcourts query --court scotus --docket-number 25-1208` — Norfolk Southern Railway Co. v. Mallory row returned. `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 24-1190` — Syngenta Crop Protection v. Nemeth row returned. `ranged corpus reads: 1 GET(s), 262144 byte(s)`

No CourtListener MCP calls and no web searches. The statpack was not consulted.
