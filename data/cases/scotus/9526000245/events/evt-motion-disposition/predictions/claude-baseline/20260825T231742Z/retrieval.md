# Retrieval log

Beyond the provisioned inputs (event.yaml, context.json, the 2026-08-26
snapshot) and the committed `metrics/statpack.md`:

## CourtListener MCP

1. `search` (type `d`, court `ca7`, docket_number `26-2577`) — 0 results; the
   Seventh Circuit appeal is not in RECAP.
2. `search` (type `r`, q `"Hobbins" AND "Gerol"`) — found the underlying case:
   *Hobbins Forester v. Gerol*, E.D. Wis. 2:26-cv-01287, filed 2026-07-22,
   nature of suit 530 Habeas Corpus (General), docket_id 73658638.
3. `call_endpoint` (`docket-entries`, docket 73658638) — 21 entries: pro se
   emergency habeas challenging state bond restraints; order of 2026-07-28
   denying the petition, dismissing the action, dismissing the TRO motion as
   moot, and declining a certificate of appealability.

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --include-applications --limit 8`
  - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned recent SCOTUS application rows, including the pro se analogue
    26A237 (Golden v. Transunion: substantive, denied 4 days after filing, no
    response requested, no referral) and the granted/high-profile substantive
    applications (26A124) whose shape dominates the grant side of the base
    rate.
- One prior invocation failed on a nonexistent `--caption` option (usage
  error; no corpus read).

## Web

None.
