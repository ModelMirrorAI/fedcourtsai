# Retrieval log

Beyond the provisioned inputs (event.yaml, record/context.json, the
2026-08-14 snapshot) and the committed `metrics/statpack.md`:

## CourtListener MCP

1. `search(type=d, court=ca9, docket_number=25-2374)` — 0 results (the Ninth
   Circuit case below is not in the RECAP docket index under that number).
2. `search(type=r, court=[ca9, azd], q="Allen Watkins")` — 0 results.
3. `search(type=d, court=[ca9, azd], case_name=Watkins, filed_after=2024-01-01)`
   — 13 dockets; identified the applicant's underlying District of Arizona
   litigation (self-filed civil suits: Watkins v. Becton Dickinson & Co.
   2:25-cv-01209 and 2:26-cv-00937, Watkins v. Santander Consumer USA
   2:25-cv-02152, Social Security appeals, and others). Used as forward
   context on the litigation the stay application arises from; no material
   about this application's own disposition was sought or surfaced.

## Corpus tooling

No `fedcourts query` / `open-events` calls — the query surface has no
ask/party-type filter that would isolate comparable interim applications, and
the statpack's interim section already gave the population shape. No ranged
corpus reads to record.

## Web

No web searches.
