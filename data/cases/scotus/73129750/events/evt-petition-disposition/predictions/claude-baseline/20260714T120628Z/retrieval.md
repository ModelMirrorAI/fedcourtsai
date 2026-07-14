# Retrieval log

No retrieval beyond the provisioned inputs and committed repo files. The
provisioned snapshot already contained the event's disposition (petition
GRANTED, Dec 5, 2025), so no CourtListener MCP calls, no REST calls, no
`fedcourts query` / `open-events` corpus reads, and no web searches were made
— retrieval about this case's outcome is barred anyway, and nothing else
could change the call.

Consulted (all local, committed or provisioned):

- `record/snapshots/2026-07-14.json` — provisioned baseline.
- `record/documents/brief-in-opposition.txt` + `documents.json` — provisioned
  filed-document text.
- `record/context.json`, `events/evt-petition-disposition/event.yaml`.
- `metrics/statpack.md` — committed base-rate roll-up (modern
  discretionary-cert disposition table); no ranged corpus reads issued.
