# Retrieval log

Beyond the provisioned inputs (snapshot, petition.txt, brief-in-opposition.txt,
questions-presented.txt, documents.json, record/context.json) and the committed
`metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "594 U.S. 482"` — known-case
  lookup for PennEast v. New Jersey. Returned no rows;
  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)` and a `note:`
  line stating only 161 of 590,339 in-scope SCOTUS rows carry citation data
  (a coverage gap, not a no-match). Not retried — sparse-filter guidance.

## Web retrieval (forward mode — unrestricted)

- WebSearch: `Hoffmann v. WBI Energy Transmission Solicitor General brief
  certiorari Natural Gas Act just compensation state law`. Result summaries
  (pgjonline.com, akingump.com, mcguirewoods.com, eenews.net, oyez.org,
  scotusblog.com, washingtonexaminer.com) reported that the SG's invited
  brief urged grant while endorsing the Eighth Circuit's view that the Fifth
  Amendment, not state law, supplies the compensation standard, and that the
  underlying dispute is ~$383,300 in attorney's fees. This was the decisive
  retrieval for my below-baseline adjustment.
- WebFetch: `https://www.akingump.com/en/insights/blogs/speaking-energy/us-supreme-court-set-to-interpret-natural-gas-act-section-7`
  — HTTP 403, no content retrieved.
- WebFetch: `https://www.scotusblog.com/cases/hoffmann-v-wbi-energy-transmission-inc/`
  — confirmed grant date (2026-06-29), argument date (2026-11-09, OT2026), and
  the QP as granted; the page did not state the SG brief's substantive position.

No CourtListener MCP lookups were made — the provisioned snapshot already
carried the full docket through 2026-08-16.
