# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-24.json`, `context.json`, `event.yaml`, and the five documents under `record/documents/`), I consulted:

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73278422 --event evt-brief-judgment --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --citation '596 U.S. 482' --citation '589 U.S. 93' --citation '582 U.S. 120' --citation '446 U.S. 14'` — a known-case lookup of the Bivens line (Egbert, Hernández, Abbasi, Carlson). stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`, plus a `note:` that only 200 SCOTUS rows carry any reporter citation; it returned one unrelated row (scotus/16473441), so it informed nothing.
- `metrics/statpack.md`, "The merits docket (granted cases)" section — the pooled strictly-prior disturbed rate (grant Terms 2017–2024 rendered: 360/516 = 69.8%).

## CourtListener MCP

1. `search` (type `o`, court `scotus`, q `Bivens "new context" Carlson`, filed after 2025-01-01) — returned Goldey v. Fields, 606 U.S. 942 (2025), which both briefs already cite.
2. `search` (type `d`, court `scotus`, docket_number `25-417`) — no results.
3. `call_endpoint` `docket-entries` (docket 73278422, newest first) — zero entries returned, so no post-snapshot docket check was possible.
4. `search` (type `o`, court `scotus`, q `Bivens`, filed after 2025-07-01) — returned Cisco Systems, Inc. v. Doe (No. 24-856, decided 2026-06-23) and Hencely v. Fluor Corp. (No. 24-924, decided 2026-04-22); I did not read either opinion, and used only the dates (Cisco came down the day after this petition was granted, which both merits briefs discuss).

No web searches. Nothing retrieved concerned this case's disposition, which does not yet exist.
