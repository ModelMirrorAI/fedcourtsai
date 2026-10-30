# Retrieval Log

## Corpus CLI Queries (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000328" --event "evt-order-call-for-response-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --q "Protopapas" --limit 20 --json`
   - Failed (`No such option: --q`; `fedcourts query` takes structured flags only).
3. `uv run fedcourts query --court scotus --q "Whittaker" --limit 20 --json`
   - Failed (`No such option: --q`).
4. `uv run fedcourts query --court scotus --q "Atlas Turner" --limit 20 --json`
   - Failed (`No such option: --q`).
5. `uv run fedcourts query --court scotus --originating-court "Supreme Court of South Carolina" --limit 30 --json`
   - Failed (`No such option: --originating-court`).
6. `uv run fedcourts query --court scotus --docket-number 25-213 --include-open --full`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73275148` (*Atlas Turner, Inc. v. Donna B. Welch, et al.*, No. 25-213), originating from the Supreme Court of South Carolina (`2023-001096`), `disposition: "denied"` on `2026-01-12` after `distribution_count: 2`.
7. `uv run fedcourts query --court scotus --docket-number 26-159 --include-open --full`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/9026000159` (*Peter Protopapas v. Whittaker Clark & Daniels, Inc., et al.*, No. 26-159), originating from the Third Circuit (`24-2210, 24-2211, 25-1044`), filed `2026-08-03`, pending (`disposition: null`).
8. `uv run fedcourts query --court scotus --docket-number 26-263 --include-open --full`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000263` (*Official Committee of Talc Claimants v. Whittaker, Clark & Daniels Inc, et al.*, No. 26-263), originating from the Third Circuit (`24-2210, 24-2211, 25-1044`), filed `2026-09-08`, pending (`disposition: null`).
9. `uv run fedcourts query --court scotus --docket-number 26-350 --include-open --full`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned `scotus/9026000350` (*Altrad Investment Authority S.A.S, et al. v. Cape Intermediate Holdings Limited, et al.*, No. 26-350), companion Vide petition from the Supreme Court of South Carolina (`2025-002104`), filed `2026-09-15`, pending (`disposition: null`, `distribution_count: 1`).
10. `uv run fedcourts stats --court scotus --era 2020s`
    - Returned `"skipped": true` (`_No corpus present — run after fedcourts corpus-pull._`); used committed `metrics/statpack.md` for base rates as instructed.

## CourtListener MCP Lookups

- None attempted (the lower-court opinions, orders, and briefing excerpts were provisioned in full in `record/documents/appendix.txt` and `record/documents/petition.txt`).

## Web Searches

- None attempted.
