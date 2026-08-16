# Retrieval log (claude-baseline, 20260816T173750Z)

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, and `record/documents/` — questions-presented,
petition, and the brief-in-opposition file, which carries both the BIO and
respondent's 7/20/2026 merits brief):

- **Committed statpack** — read `metrics/statpack.md`, "The merits docket
  (granted cases)" section, for the pooled strictly-prior disturbed-rate
  baseline (Terms 2017–2024: 359/515 = 69.7%).
- **CourtListener MCP** — one `search` call attempted (Ninth Circuit
  opinion lookup for *Prutehi Litekyan/Prutehi Guahan v. Dep't of the Air
  Force*): failed with HTTP 429, daily rate limit exhausted
  (`1400/day`). Not retried; no CourtListener data informed this
  prediction.
- **Corpus (`fedcourts query`)** — no substantive query run. One malformed
  invocation (unsupported `--text` option) errored at the CLI without
  touching the corpus, plus `--help`; no `ranged corpus reads` line was
  produced by either.
- No web searches.
