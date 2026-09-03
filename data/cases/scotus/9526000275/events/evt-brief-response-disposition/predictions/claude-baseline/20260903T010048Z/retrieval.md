# Retrieval log

Beyond the provisioned inputs (snapshot, `record/context.json`,
`record/documents/application.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --include-applications --text "injunction pending appeal ballot election" --limit 8`
   — rejected (no `--text` flag; `query` is a structured filter, not free-text
   search). No corpus reads.
2. `uv run fedcourts query --court scotus --include-applications --include-open --era 2020s --limit 12`
   — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned recent application
   rows, mostly time-extension grants; one useful substantive comparator (26A203,
   National Park Service v. National Trust: response requested, referred, 7 amici,
   granted).

No CourtListener MCP lookups and no web searches: the application's requested
disposition date is the day of this run, so any live search on the controversy
risked surfacing this case's own outcome. Explained in `reasoning.md`.
