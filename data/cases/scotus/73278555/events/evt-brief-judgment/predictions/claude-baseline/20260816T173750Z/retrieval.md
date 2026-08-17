# Retrieval log

Beyond the provisioned inputs (snapshot, event.yaml, context.json, QP text,
petition, and the bundled BIO + respondents' merits brief), this forward-mode
cell consulted:

## Corpus

- `uv run fedcourts query --court scotus --citation "595 U.S. 170" --citation "573 U.S. 409" --limit 4`
  → no rows; stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)` and
  the coverage note that only 161 of 590,339 scotus rows carry citation data (a
  known-sparse filter — not retried).
- Committed `metrics/statpack.md`, "The merits docket (granted cases)" section —
  the pooled 2017–2024 disturbed rate (359/515 = 69.7%) used as the anchor.

An earlier `fedcourts query` attempt used a nonexistent `--text` flag and made
no corpus read.

## Web searches (WebSearch)

1. `Anderson v. Intel Supreme Court 25-498 Solicitor General amicus brief merits respondents`
2. `"Anderson v. Intel" solicitor general brief "supporting respondents" OR "supporting affirmance" ERISA meaningful benchmark`
3. `Parker-Hannifin Corp v. Johnson 24-1030 Supreme Court cert petition status 2026`
4. `"Anderson v. Intel" United States amicus brief July 2026 ERISA "meaningful benchmark" DOL position affirm`

Key results used: DOL press release (dol.gov, 2026-07-10) and trade coverage
(PLANSPONSOR "DOL Backs Intel", 401kspecialistmag "DOL, ICI, ERIC Urge Supreme
Court to Side with Intel") confirming the United States' merits amicus supports
respondents and urges affirmance; SCOTUSblog case page and relist coverage
confirming *Parker-Hannifin* (No. 24-1030) is held, not granted.

## Page fetches (WebFetch)

- justice.gov OSG brief page for Anderson v. Intel → HTTP 403, unusable.
- supremecourt.gov PDF of the 2026-07-09 amicus filing → HTTP 403, unusable.
- pionline.com "Solicitor general backs participant in Intel Supreme Court
  case" → dated October 29, 2019; it concerns the earlier *Intel v. Sulyma*
  petition, not this case — discarded as a signal.
- scotusblog.com essay "How a seemingly unexciting case on retirement plans
  could have massive consequences" (July 2026) — merits-argument summary; its
  author's affirmance advocacy noted as defense-side commentary, weighted
  accordingly.

No CourtListener MCP calls were made (the provisioned documents and the
searches above covered what the forecast needed). Nothing retrieved concerned
this case's outcome — none exists; argument is set for October 6, 2026.
