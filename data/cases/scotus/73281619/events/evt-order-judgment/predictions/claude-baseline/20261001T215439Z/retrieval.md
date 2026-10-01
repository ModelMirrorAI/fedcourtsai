# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-10-01.json`, `record/context.json`, `record/documents/{questions-presented,petition,brief-in-opposition}.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   Returned this case's own row first, then recent granted stay applications (DHS v. D.V.D., People Not Politicians v. Onder, NRCC v. Brown, Nelsen v. Pike). No doctrinal neighbors; not used in the number.

## CourtListener MCP

2. `search` (type `o`, court `ca3`, q `Anash "Borough of Kingston" RLUIPA`) — found Anash Inc v. Borough of Kingston, No. 25-1097, filed 2026-07-30, cluster 10936715, opinion 11404291.
3. `search` (type `o`, q `"Missionaries of Saint John the Baptist" Frederic`) — found the Kentucky Supreme Court opinion below, 2024-SC-0006, filed 2025-12-18, cluster 10760784, opinion 11227369.
4. `search` (type `d`, court `scotus`, q `"University Heights" Grand`) — 0 results for the related petition No. 25-965 the BIO cites.
5. `read_document` (opinion 11227369, chunk 0 of 10) — caption and factual background of the opinion below.
6. `read_document` (opinion 11404291, chunk 0) — error: no text available for the Anash opinion.
7. `read_document` (opinion 11227369, chunks 4 to 8) — the RLUIPA merits section, the equal-terms holding, the conclusion, and the opening of Justice Thompson's state-law dissent.

No web searches. Seven retrieval calls in total. Everything read predates the 2026-10-01 grant, and nothing concerning this case's own merits disposition exists yet to surface.
