# Retrieval log — scotus/73281654 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Beyond the provisioned inputs (snapshot, questions-presented, petition text)
and the committed `metrics/statpack.md`, I consulted:

## Corpus lookups (`fedcourts` CLI)

All `query` calls returned **zero rows**; only the read-stats line printed.

1. `uv run fedcourts query --court scotus --topic "Indian tribe breach of trust water rights Tucker Act money-mandating" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --topic "Indian tribe breach of trust" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --topic "water rights" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --topic "tribe" --limit 10`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
5. `uv run fedcourts query --court scotus --topic "Federal Circuit" --limit 5`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`

## CourtListener MCP lookups

1. `search` (type=o, court=cafc, q="Winnemucca Indian Colony v. United States
   breach of trust water") — confirmed the Federal Circuit opinion below:
   No. 24-1108, decided 2025-10-16. Used only to verify the decision below;
   I did not retrieve or seek anything about this petition's own (nonexistent,
   forward-mode) disposition.

## Web searches

None.
