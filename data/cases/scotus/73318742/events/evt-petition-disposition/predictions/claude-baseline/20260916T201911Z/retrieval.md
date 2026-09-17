# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`,
`documents/questions-presented.txt`, `documents/petition.txt`,
`documents/brief-in-opposition.txt`, `documents/documents.json`) and the committed
`metrics/statpack.md`:

## Corpus tooling

- `uv run fedcourts query --court scotus --text "judicial immunity section 1983 state judge due process" --limit 8`
  Rejected by the CLI (`No such option: --text`; the command takes structured
  filters only). No corpus read occurred and no `ranged corpus reads` line was
  printed. Not retried: no available filter narrows on the legal question.

## CourtListener MCP

1. `search` type=`o`, q=`Wain Bunnell`, court=`ca6`, filed_after=`2026-01-01`,
   num_results=5. Result: 0 hits.
2. `search` type=`o`, docket_number=`25-5722`, court=`ca6`, num_results=5.
   Result: 0 hits.

Both sought the unpublished Sixth Circuit opinion below (decided February 13,
2026), not this petition's disposition. Neither surfaced any material about this
case.

## Web searches

None.
