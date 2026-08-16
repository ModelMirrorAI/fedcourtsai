# Retrieval log

Beyond the provisioned inputs (snapshot, `record/context.json`, and the
provisioned document texts under `record/documents/`), I consulted:

- Committed base rates: `metrics/statpack.md`, "The merits docket (granted
  cases)" section — pooled grant Terms 2017–2024 for the disturbed-rate
  baseline (359/515 ≈ 69.7%).
- One corpus lookup:
  - Command: `uv run fedcourts query --court scotus --citation "415 U.S. 361"
    --citation "598 U.S. 175" --citation "567 U.S. 1" --citation "510 U.S. 200"
    --limit 5`
  - Transfer line: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  - Result: empty, with the tool's `note:` naming the citation-coverage gap
    (161 of 590,339 SCOTUS rows carry citation data). Contributed nothing to
    the forecast.

No CourtListener MCP calls and no web searches were made. The forecast rests
on the provisioned record, the petition and SG merits-brief texts, the
statpack baseline, and general legal knowledge of the cited precedents
(*Johnson v. Robison*, *Thunder Basin*, *Elgin*, *Axon*).
