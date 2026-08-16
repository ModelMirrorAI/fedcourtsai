# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, event.yaml,
record/context.json, petition.txt, brief-in-opposition.txt,
questions-presented.txt, documents.json) and the committed
`metrics/statpack.md`:

1. **Corpus query** (priors lookup, empty result):

   ```
   uv run fedcourts query --court scotus --citation "596 U.S. 482" --limit 5
   ```

   stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   plus a `note:` line reporting the citation column's coverage gap
   (161 of 590339 scotus-scope rows carry citation data), so the empty
   result reflects sparse coverage, not absence of the precedent. I did not
   retry other sparse filters.

2. **CourtListener MCP** (failed, degraded): one `search` call for
   post-June-2025 SCOTUS opinions mentioning Bivens (opinion search,
   court=scotus, filed_after=2025-06-01) — returned HTTP 429
   (daily rate limit exceeded, retry window ~100 minutes). Per the
   degraded-upstream rule I proceeded on the provisioned inputs and the
   statpack; no further MCP calls were attempted.

No web searches were surfaced by the engine. No other retrieval.
