# Retrieval log

## Corpus lookups (`fedcourts`, via the cell's corpus service)

1. `uv run fedcourts paths --court scotus --docket 73500214 --event evt-order-cvsg-disposition --role predictor` (path resolution only; no transfer line).
2. `uv run fedcourts query --court scotus --citation "602 U.S. 205"` — attempted known-case lookup of the 2024 Cantero decision. Returned no rows with a `note:` that only 200 scotus rows carry any reporter citation. stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted` — recent granted priors for shape (not case-specific; mostly OT2026 grants and substantive applications). stderr: `ranged corpus reads: 45 GET(s), 11665408 byte(s)`.

## CourtListener MCP

4. `search` type `d`, court `scotus`, docket_number `25-1350` (Flagstar v. Kivett) — 0 results.
5. `search` type `d`, court `scotus`, docket_number `25-1004` (Citizens Bank v. Conti) — 0 results.
6. `call_endpoint dockets` court `scotus` docket_number `25-1350` — HTTP 429, daily rate limit exceeded.
7. `call_endpoint dockets` court `scotus` docket_number `25-1004` — HTTP 429.
8. `get_endpoint_item dockets 73500214` — HTTP 429.

After the 429s I made no further CourtListener calls and fell back to the provisioned inputs and the repo's committed event registry.

## Repo-side reads beyond this cell's inputs

- `metrics/statpack.md` (committed base rates: modern cert, relist, CVSG, salience band sections).
- `grep` over `data/cases/scotus/**/event.yaml` for the companion cases, then read `event.yaml` only for `scotus/73500252` (Flagstar v. Kivett, No. 25-1350: `evt-order-cvsg-disposition` opened 2026-10-05), `scotus/73281044` (Citizens Bank v. Conti: petition event resolved), and `scotus/72475676` (Flagstar v. Kivett, No. 22-349: petition event resolved). No snapshot or outcome file of any other case was read; nothing under `data/qp-topics/` was read.

No web searches.
