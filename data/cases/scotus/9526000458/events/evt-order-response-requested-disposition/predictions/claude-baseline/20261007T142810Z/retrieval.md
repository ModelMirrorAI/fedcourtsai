# Retrieval log — 26A458, K.M.K. v. Washington Interscholastic Activities Association

Forward cell (`context.mode: forward`); retrieval unrestricted. Nothing about this
application's own disposition was sought or surfaced.

## Provisioned inputs read

- `record/snapshots/2026-10-06.json` (two proceedings entries: application
  submitted 2026-10-02 to Justice Kagan; response requested 2026-10-06, due
  2026-10-13 4 p.m. EDT)
- `record/context.json` (forward; band null; response_requested true;
  referred_to_court false; amicus_briefs 0; term 2026; cutoff 2026-10-07, date cut)
- `record/documents/application.txt` + `documents.json` (134 pp., `truncated: true`,
  `empty_text: false`) — read the introduction, statement of the case, the
  argument on the mandatory-injunction standard, the parental-rights and
  irreparable-harm sections, the cert-before-judgment section, and the conclusion.
- `metrics/statpack.md`, section *The interim docket (applications)*.

## Corpus lookups (`fedcourts query`, local corpus service)

1. `uv run fedcourts query --court scotus --include-applications --disposition granted`
   — stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`. Top-ranked rows were
   almost all time-extension applications (26A4xx) plus a few cert grants; no
   substantive stay/injunction priors surfaced.
2. `uv run fedcourts query --court scotus --include-applications --disposition denied`
   — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Rows were
   2026-10-05 cert denials; no application priors surfaced.

Neither query informed the number; the committed statpack is the only corpus
base rate used.

## CourtListener MCP lookups

1. `search` type=d, courts ca9+wawd, "Brown v. Washington Interscholastic Activities
   Association" → district docket 73462677 (W.D. Wash. 3:26-cv-05616, Judge Estudillo).
2. `search` type=o, ca9, quoted WIAA + "injunction pending appeal", filed after
   2026-09-01 → 0 results.
3. `call_endpoint` docket-entries, docket 73462677, newest first → PI denied
   2026-08-23; injunction pending appeal denied 2026-08-31; case stayed with status
   report due 2027-01-15; CA9 orders of 2026-09-25 and 2026-10-01 noted.
4. `search` type=o, ca9, "Brown Washington Interscholastic Activities Association",
   filed after 2026-08-01 → cluster 10984095 (26-5488, 2026-09-25, Published).
5. `search` type=o, scotus, "Mirabelli v. Bonta", filed after 2026-01-01 → cluster
   10802600 (25A810, 2026-03-02, per curiam).
6. `search` type=d, scotus, "Washington Interscholastic Activities Association" → 0
   results (CourtListener carries no SCOTUS application docket for this matter).
7. `call_endpoint` clusters id=10984095 → no panel/judges fields populated.
8. `call_endpoint` opinions cluster=10984095 → `plain_text` empty (no text available).
9. `call_endpoint` opinions cluster=10802600 → full Mirabelli per curiam, Barrett
   concurrence (Roberts, Kavanaugh joining), Kagan dissent (Jackson joining);
   Thomas and Alito would grant in full; Sotomayor would deny in full.
10. `search` type=r, ca9, docket_number 26-5488 → appellate docket 74707109.
11. `call_endpoint` docket-entries, docket 74707109, newest first → panel Hawkins,
    W. Fletcher, Mendoza; order for publication 2026-09-25 denying the injunction
    pending appeal; amicus briefs filed 2026-09-29/10-01 by State of Iowa et al.,
    Women's Liberation Front, Do No Harm; opening brief filed 2026-09-22; appellee
    motion to extend briefing time 2026-10-05.

No web searches.
