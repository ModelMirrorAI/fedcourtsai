# Retrieval log

Mode `forward`; retrieval unrestricted. All retrieval was through the
configured tools (CourtListener MCP, web search, web fetch, and the `fedcourts`
corpus CLI); PDFs that the fetch tool could not parse were text-extracted
locally with pypdf from the fetched copy. Roughly 22 calls.

## Corpus CLI

- `uv run fedcourts query --court scotus --citation "583 U.S. 281" --citation "596 U.S. 573" --citation "586 U.S. 392" --citation "538 U.S. 510" --citation "533 U.S. 678"`
  - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  - stderr note: citations filter sparsely populated (200 SCOTUS rows carry a cite); zero rows returned. No priors were used from the corpus.
- Base rates: committed `metrics/statpack.md`, "The merits docket (granted cases)" section (pooled grant Terms 2017 through 2025, 377/540 disturbed).

## CourtListener MCP

- `search` (opinions, q="Barbosa da Cunha", courts ca2/nywd/nynd/nysd/nyed/vtd/ctd): 0 results.
- `search` (opinions, ca2, q="1225(b)(2)(A)" AND "1226(a)" AND "bond hearing", filed after 2026-01-01): 1 result, Barbosa Da Cunha v. Freden, 25-3141, en banc order of 2026-09-25 (cluster 10983473, opinion 11451136).
- `search` (opinions, citation "175 F.4th 61"): 0 results.
- `search` (opinions, ca2, case_name "Barbosa da Cunha"): the same en banc order only.
- `read_document` (opinion 11451136): no text available on CourtListener; fetched the PDF from the Second Circuit instead (below).

## Web

- Fetched `supremecourt.gov/qp/26-00104qp.pdf` (questions presented; extracted locally).
- Fetched `supremecourt.gov/docket/docketfiles/html/public/26-104.html` (docket, counsel of record).
- Fetched `supremecourt.gov/docket/docketfiles/html/public/25-1415.html` (Putra v. Lopez-Campos docket; distributed 9/28, letters 9/14 and 9/25, no disposition as of 9/25).
- Fetched `supremecourt.gov/docket/docketfiles/html/public/26-43.html` (Buenrostro-Mendez v. Blanche docket; distributed 9/28, no disposition as of 9/25).
- Fetched `supremecourt.gov/orders/courtorders/100126zr_6j37.pdf` (October 1, 2026 order: 26-104 granted; 25-1131 granted limited to Q1; 25-1349 granted; extracted locally).
- Fetched `justice.gov/d9/2026-07/barbosa_da_cunha_hold_pet_-_final.pdf` (government's petition with the Second Circuit opinion and district court decision appended; extracted locally and read: QP, statement, reasons for granting, the panel opinion's text sections on "seeking admission", Jennings, § 1226(c) and the Laken Riley Act).
- Fetched `ww3.ca2.uscourts.gov/decisions/OPN/25-3141_complete en banc_opn.pdf` (en banc denial with Bianco/Nathan concurrence, Schwartz concurrence, Menashi dissent, Cabranes statement; extracted locally).
- Fetched `scotusblog.com/cases/rhoney-v-barbosa-da-cunha/` (case page; no argument date yet).
- Fetched `latintimes.com` article on Genalo v. Black (No. 25-886) being mooted by a pardon and dismissed September 11, 2026.
- Fetched `jurist.org` news report on the grant.
- Fetched `cdn.ca9.uscourts.gov/.../25-6842.pdf` (Ninth Circuit opinion; not parsed, not read; circuit tally taken from the Menashi dissent instead).
- Web searches (3): grant coverage; circuit-split coverage; October 1 order list. Surfaced pbs.org, courthousenews.com, cis.org, cliniclegal.org, bloomberglaw.com, congress.gov CRS LSB11438, and myattorneyusa.com; fetches of courthousenews, cis.org, cliniclegal, congress.gov and myattorneyusa returned 403 and were not read.

Nothing retrieved postdates the grant except the October 1 order itself and
news coverage of the grant; no material about the merits disposition exists.
