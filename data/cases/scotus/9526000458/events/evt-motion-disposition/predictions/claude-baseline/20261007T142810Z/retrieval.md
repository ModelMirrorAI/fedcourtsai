# Retrieval log

Provisioned inputs read: `event.yaml`, `record/context.json`,
`record/snapshots/2026-10-03.json`, `record/documents/documents.json`,
`record/documents/application.txt`. Also read the sibling event definition
`events/evt-order-response-requested-disposition/event.yaml` in the case
directory (forward mode; see `flags.json`).

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9526000458 --event evt-motion-disposition --role predictor`
- `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 12`
  — stderr: `ranged corpus reads: 27 GET(s), 7012352 byte(s)`. Returned
  twelve 26A-series grants that are time-extension or procedural grants; no
  substantive injunction prior surfaced.
- `uv run fedcourts query --court scotus --include-applications --limit 25`
  — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Returned one 26A
  grant and recent cert denials/GVRs; not used.
- `metrics/statpack.md`, *The interim docket (applications)* — the anchor.

## CourtListener MCP

1. `search` (dockets, ca9/wawd) "Brown v. Washington Interscholastic
   Activities Association" — located W.D. Wash. 3:26-cv-05616 (docket 73462677).
2. `search` (opinions, scotus, filed after 2026-01-01) "B.P.J." Title IX
   transgender athletes — West Virginia v. B.P.J., cluster 10882186, filed
   2026-06-30.
3. `search` (opinions, scotus) "Mirabelli v. Bonta parental rights" — timed out.
4. `call_endpoint` clusters id 10882186 — judges: Kavanaugh; syllabus empty.
5. `search` (opinions, scotus, filed after 2025-10-01) "Mirabelli Bonta" —
   cluster 10802600, docket 25A810, filed 2026-03-02.
6. `search` (opinions, scotus, filed after 2025-06-01) "injunction pending
   appeal" application — Trump v. Barbara, B.P.J., Mirabelli, Trump v. CASA,
   Skrmetti.
7. `search` (opinions, ca9, filed after 2026-08-01) "Washington
   Interscholastic Activities Association" injunction pending appeal — no
   results.
8. `call_endpoint` opinions cluster 10802600 — read the Mirabelli per curiam,
   Barrett concurrence, and Kagan dissent in full.
9. `read_document` opinion 11349709 (B.P.J.) — no text available.

## Web fetches

- `https://www.supremecourt.gov/docket/docketfiles/html/public/26a458.html`
  — this application's live docket: Oct 2 submission; Oct 6 response
  requested by Justice Kagan, due Oct 13, 2026.
- `https://www.supremecourt.gov/docket/docketfiles/html/public/24-43.html`
  — B.P.J. judgment entry (June 30, 2026: reversed and remanded; Kavanaugh
  for six; Sotomayor, Kagan, Jackson concurring in judgment in part and
  dissenting in part).
- `https://www.supremecourt.gov/docket/docketfiles/html/public/22a800.html`
  — the 2023 B.P.J. application: response requested, three amicus briefs,
  referred, denied with Alito and Thomas dissenting.
