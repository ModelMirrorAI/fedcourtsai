# Retrieval log

Provisioned inputs read: `event.yaml`, `record/context.json`,
`record/snapshots/2026-08-18.json`, `record/documents/documents.json`,
`questions-presented.txt`, `petition.txt` (grep and the panel caption),
`brief-in-opposition.txt` (listed, not read in depth), `merits-brief-petitioner.txt`
and `merits-brief-respondent.txt` (tables of contents, summaries of argument,
introductions, and the passages characterizing the United States' position).
Committed base rates: `metrics/statpack.md`, "The merits docket (granted
cases)" section.

## Corpus lookups (`fedcourts`)

None. `fedcourts query` was not run (no subject filter fits an
implied-right-of-action question, and a citation lookup's egress was not
worth a prior I could not use), so there is no `ranged corpus reads` line to
record.

## CourtListener MCP

None. The MCP tool schemas were loaded but no call was made.

## Web retrieval (forward cell — unrestricted)

1. WebSearch: `Crowther v. Board of Regents University System of Georgia
   25-183 Solicitor General brief Title IX employees private right of action`
   — surfaced the supremecourt.gov QP and petitioner-brief PDFs, the
   CourtListener opinion page, CAC, Saul Ewing, NWLC and Oyez pages. Used only
   to locate sources.
2. WebSearch: `Crowther v. Board of Regents Supreme Court oral argument Title
   IX employment October Term 2026` — surfaced SCOTUSblog, Ropes & Gray, Saul
   Ewing, Ogletree, Littler, K-12 Dive and Washington Examiner pages; the
   result summary reported argument set for 2026-11-30.
3. WebFetch `https://www.scotusblog.com/cases/crowther-v-board-of-regents-of-the-university-system-of-georgia/`
   — docket timeline through 2026-08-24 (respondent-side amici including the
   United States), argument 2026-11-30, no decision.
4. WebSearch: `"Crowther" Title IX "brief for the United States as amicus
   curiae" invitation 25-183 Solicitor General recommends` — surfaced the
   justice.gov CVSG PDF, the OSG brief page, the supremecourt.gov docket page,
   Relist Watch and the NEA amicus PDF; the result summary reported the SG
   recommended grant and that the United States filed in support of
   respondents on 2026-08-24.
5. WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-183.html`
   — live docket entries after 2026-08-17: 2026-08-24 amicus briefs for
   respondents (United States, National School Attorneys Association et al.,
   Chamber of Commerce, West Virginia and 20 states) and the SG's motion for
   divided argument; 2026-09-04 set for argument 2026-11-30; 2026-09-15 record
   requested; 2026-09-16 petitioners' reply brief filed; 2026-09-18 circulated.
   No disposition.
6. WebFetch `https://www.justice.gov/osg/supreme-court-briefs?search_api_fulltext=Crowther`
   — **HTTP 403 Forbidden**, no content.
7. WebFetch `https://www.justice.gov/d9/2026-04/25-183_crowther_cvsg.pdf`
   — the SG's CVSG brief. WebFetch could not read the binary; the PDF was
   saved locally and its text extracted with `pdftotext`/pypdf. Read: table of
   contents, Statement (panel and en banc posture), Discussion Part A (the
   Eleventh Circuit is correct; Sandoval/Gonzaga/Gebser scope-of-remedy
   framework; Title VII structure; Novotny and Brown; Jackson, North Haven and
   Cannon distinguished; footnote 2 disclaiming the government's Lakoski and
   Doe v. Mercy positions), and the Conclusion ("The petition for a writ of
   certiorari should be granted").
8. WebFetch `https://www.courtlistener.com/opinion/10266389/thomas-crowther-v-board-of-regents-of-the-university-system-of-georgia/`
   — page rendered empty through WebFetch; no content used. The panel
   (W. Pryor, C.J., Luck and Ed Carnes, JJ.) was read from the provisioned
   petition appendix instead.

Nothing retrieved disclosed or hinted at a disposition of the question
presented; the case is pending argument.
