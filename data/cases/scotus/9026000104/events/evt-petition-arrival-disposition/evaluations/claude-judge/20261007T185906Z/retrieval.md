# Retrieval — claude-judge / 20261007T185906Z

Beyond the provisioned inputs (event.yaml, outcome.json, the record snapshot
of 2026-10-04, the three blinded candidate directories, the committed
`metrics/statpack.md`, and the schemas):

## CourtListener MCP

1. `search` (type=o, q="Barbosa da Cunha", filed_before=2026-08-16, fields
   caseName/court/dateFiled/citation/docketNumber, 10 results) — to confirm
   that the sister-circuit opinions claude-baseline cited as establishing the
   split exist. Returned 12 hits including *Rojas v. Olson* (CA7,
   2026-07-30), *Rodriguez Vazquez v. Bostock* (CA9, 2026-07-30), *Quiroz v.
   Mullin* (CA10, 2026-06-30), *Guerrero Orellana v. Moniz* (CA1,
   2026-08-13), and *Ohindo v. Ball* (CA2, 2026-07-29). Used only to check a
   cited authority's existence for the reasoning-quality grade; not for new
   case facts.

## Corpus tooling

No `fedcourts query` or `open-events` call was made.

No web searches.
