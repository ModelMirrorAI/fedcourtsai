# Retrieval log — scotus/73274837 evt-petition-disposition (claude-baseline, 20260712T114712Z)

Cell mode: `forward` (pending case; retrieval unrestricted). No lookup sought or
returned this case's own disposition — none exists yet.

## Corpus lookups (`fedcourts` CLI, ranged backend)

1. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "554 U.S. 570" --corpus-backend ranged`
   — sought SCOTUS priors citing Bruen/Heller; returned no rows (citation index
   does not cover these cert dockets).
   stderr: `ranged corpus reads: 402 GET(s), 105381888 byte(s)`
2. `uv run fedcourts query --court scotus --corpus-backend ranged`
   — ranked SCOTUS priors; surfaced the June 30, 2026 order-list behavior:
   *Viramontes v. Cook County* (25-238) and *Grant v. Higgins* (25-566) granted
   (22 and 17 distributions respectively), *McCoy v. ATF* (25-24) and *WV
   Citizens Defense League v. ATF* (25-132) denied the same day.
   stderr: `ranged corpus reads: 402 GET(s), 105381888 byte(s)`

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (grant rate ≈ 4.9%, denied ≈ 92.6%); relist-count and CVSG cuts are
  unpopulated (`(unknown)` bucket only), so they contributed nothing.

## Web searches (engine-surfaced)

1. WebFetch `https://www.supremecourt.gov/qp/25-00238qp.pdf` and
   `.../25-00566qp.pdf` — sought the granted QPs; both returned HTTP 403
   (supremecourt.gov blocks the fetcher). Not retried.
2. WebSearch: `Supreme Court grants certiorari Viramontes Cook County Grant
   Higgins assault weapons magazines June 30 2026 question presented` —
   confirmed the two cases were consolidated on a QP limited to
   AR-15-platform/similar semi-automatic rifles (magazines not included), with
   argument expected early OT2026. Sources included saf.org, jurist.org,
   thereload.com, everytownlaw.org.
3. WebSearch: `Duncan v. Bonta certiorari petition Supreme Court magazine ban
   held relisted June 2026` — confirmed *Duncan v. Bonta* (25-198, California
   LCM ban) is likewise still pending after ~19 relists, and that the D.C.
   Circuit's *Benson* decision (which briefly created a square LCM split in
   March 2026) was vacated — matching the supplemental-brief exchange on this
   docket. Sources included calgunlawyers.com, scotusblog.com, ammoland.com,
   en.wikipedia.org.

## CourtListener MCP

- Not used: the provisioned record plus corpus/web retrieval answered the
  decisive questions, and the remaining budget was conserved.
