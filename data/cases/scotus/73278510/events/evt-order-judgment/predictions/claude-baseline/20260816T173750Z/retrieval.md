# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, `event.yaml`,
`record/context.json`, and the three `record/documents/` texts), I consulted:

- **Committed statpack** (`metrics/statpack.md`), "The merits docket (granted
  cases)" section — pooled the per-Term disturbed rates for grant Terms
  2017–2024 (359/515 ≈ 69.7%) as the scored baseline.
- **`fedcourts query`** — one attempted call
  (`uv run fedcourts query --court scotus --era modern --disposition granted "<free text>"`)
  failed on usage (the command takes structured filters only, no free-text
  argument), followed by `fedcourts query --help`. No query executed, so no
  `ranged corpus reads:` line was printed and no corpus rows were retrieved.
  None of the available structured filters fit better than the statpack
  anchor, so I did not retry.
- **`fedcourts paths`** — path resolution for this cell only.

No CourtListener MCP calls and no web searches. Petitioner's merits brief and
the merits amicus briefs (listed on the docket) were **not** retrieved; the
respondent's merits response brief text was already provisioned inside
`brief-in-opposition.txt`.
