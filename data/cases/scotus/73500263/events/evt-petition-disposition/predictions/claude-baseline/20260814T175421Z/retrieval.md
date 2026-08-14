# Retrieval log

Beyond the provisioned inputs (snapshot, event, `record/documents/`
petition and questions-presented text, `record/context.json`) and the
committed `metrics/statpack.md`:

1. **Corpus query** —
   `uv run fedcourts query --court scotus --citation "555 U.S. 285" --limit 3`
   (known-case lookup for Kennedy v. Plan Administrator for DuPont Sav. &
   Inv. Plan). Returned no rows; the tool printed a coverage note (161 of
   590,020 in-scope rows carry citation data). Transfer line:
   `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`.
   Not retried — sparse-filter guidance followed.
2. **CourtListener MCP `search`** — opinions, court `ca4`, query
   "Gasper EIDP". One hit: *David Gasper v. EIDP, Inc.*, No. 24-1959,
   filed 2025-12-08, status "Published", no reporter citation. This is the
   decision below (pre-dating the petition), not outcome material for the
   cert event being predicted.
3. **CourtListener MCP `read_document`** — opinion id 10750028, chunk 0.
   Returned mismatched text (an unrelated D. Or. opinion, *Northwest
   Investment Holdings v. PacWest Funding*), so the publication status
   could not be verified against the opinion text. Not pursued further.

No web searches. No lookup touched this petition's own disposition; the
event is pending (`forward` mode) and no disposition surfaced anywhere.
