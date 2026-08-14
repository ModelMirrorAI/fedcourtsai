# Retrieval log

Beyond the provisioned inputs (snapshot, `record/context.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`,
`documents.json`) and the committed `metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --citation "556 U.S. 868" --limit 5`
   — looking for resolved SCOTUS priors sharing the petition's lead authority
   (Caperton). Returned no rows.
   - `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
   - Printed coverage note: only 161 of 590,020 scotus rows carry citation
     data, and the column holds a case's own reporter cites, so the empty
     result reflects missing coverage, not the absence of such priors.

No CourtListener MCP lookups and no web searches were made for this cell:
the snapshot is same-day (2026-08-14), the filed petition text was
provisioned in full, and the forecast rests on the statpack base rates plus
the provisioned record.
