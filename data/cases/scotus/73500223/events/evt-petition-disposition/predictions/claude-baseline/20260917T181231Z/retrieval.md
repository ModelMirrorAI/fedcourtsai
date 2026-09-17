# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-17.json`,
`record/documents/documents.json`, `questions-presented.txt`, `petition.txt`,
`brief-in-opposition.txt`; `events/evt-petition-disposition/event.yaml`;
`metrics/statpack.md` (committed base rates).

## Corpus lookups (`fedcourts query`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned 8 recent granted SCOTUS rows, mostly OT2025 substantive applications
   (People Not Politicians v. Onder; NRCC v. Brown; National Park Service v. National
   Trust; Trump v. California) and Second Amendment / religion cert grants (Jouppi v.
   Alaska; Viramontes v. Cook County; Grant v. Higgins; Grand v. University Heights).
   None is a takings or speech-access analogue; used only as a sanity check that the
   corpus is live, not as a prior for this case.
2. `uv run fedcourts query --court scotus --citation "447 U.S. 74" --limit 3`
   stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)` plus a `note:` that only
   200 of 590919 scotus rows carry citation data. Empty result — PruneYard itself is not
   a cite-bearing row in the corpus. (This lookup was expensive for nothing; see
   `tooling.json`.)

## CourtListener MCP

Three calls attempted, all refused with HTTP 429 (`Rate limit exceeded: 300/hour`,
available again in ~6 minutes); not retried, per the budget etiquette:

1. `search` type=d court=scotus docket_number=25-1322 — live docket check for
   post-snapshot entries. **Not obtained.**
2. `search` type=o court=scotus q=`"PruneYard" "Cedar Point"` filed_after 2021-06-01 —
   post-Cedar Point SCOTUS opinions treating both. **Not obtained.**
3. `search` type=o q=`"PruneYard" shopping center "right to exclude" takings "expressive
   activity"` filed_after 2021-06-01 — lower-court treatment. **Not obtained.**

## Web searches

None.
