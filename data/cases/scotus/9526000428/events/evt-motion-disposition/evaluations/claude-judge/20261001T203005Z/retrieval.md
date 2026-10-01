# Retrieval log — claude-judge, scotus/9526000428 evt-motion-disposition, run 20261001T203005Z

Beyond the provisioned inputs (`event.yaml`, `outcome.json`, `record/context.json`,
`record/snapshots/2026-10-01.json`, `record/documents/application.txt` and its
manifest, and the three blinded candidate directories including each
`retrieval_log.json`), I read only the committed `metrics/statpack.md`, section
*The interim docket (applications)*, to understand the baseline the harness
will stamp. No `fedcourts query` or `open-events` call was made, so no
`ranged corpus reads` line exists. No CourtListener MCP lookup and no web search.
`record/opinion/` is absent, as expected on an interim cell, and nothing was
fetched to stand in for it.
