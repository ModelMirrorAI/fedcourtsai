# Retrieval log

Provisioned inputs read: `record/snapshots/2026-10-05.json`, `record/context.json`,
`record/documents/documents.json`, `questions-presented.txt`, `petition.txt`
(truncated at the appendix), `brief-in-opposition.txt`; the event definition;
`metrics/statpack.md` (modern cert disposition, originating circuit, relist
count, CVSG status, salience band, per-Term and sal-v4 segment band tables);
`docs/salience.md` (band definitions).

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "141 S. Ct. 1513"`
   (looking for the *GE Capital Retail Bank v. Belton* cert docket, No. 20-481)
   `ranged corpus reads: 10 GET(s), 2621440 byte(s)` — no rows; the tool's
   note says only about 200 SCOTUS rows carry any reporter citation.
2. `uv run fedcourts query --court scotus --citation "586 U.S. 823"`
   (looking for *Credit One Bank v. Anderson*, No. 17-1652)
   `ranged corpus reads: 0 GET(s), 0 byte(s)` — no rows, same note.

## Web fetches (forward cell; this case's own later filings, all predating the snapshot)

3. supremecourt.gov docket PDF — petitioner's reply brief (Sept 9, 2026); read
   in full from the fetched PDF.
4. supremecourt.gov docket PDF — respondents' Rule 15.8 supplemental brief
   (Sept 14, 2026); read in full. Discloses the bankruptcy court's Sept 10
   dismissal of the adversary complaint without prejudice.
5. supremecourt.gov docket PDF — petitioner's response to the supplemental
   brief (Sept 15, 2026); read in full.
6. cpradr.org "U.S. Supreme Court Review; Fall Term Cert Possibilities" —
   checked for competing arbitration petitions this Term; it names only
   *Burford German Funding v. financialright claims* (No. 25-1269) and does not
   mention this case.

## Web searches

7. Query on the case name, docket number and Section 362(k) arbitration: hits
   were the petition PDF, ABA's case page, NCBRC posts on the petition and the
   BIO, Law360 and a bankruptcy blog on the Fourth Circuit decision. None
   reported any disposition of the petition (none exists; the case is pending
   for the Oct 9 conference). I did not open the commentary pages; the filings
   themselves were the better source.
8. Query on October 2026 cert grants in arbitration/bankruptcy: returned
   coverage of the Spring 2026 FAA decisions (*Jules v. Andre Balazs
   Properties*, *Flowers Foods*) and the CPR preview above; nothing on this
   petition.

No CourtListener MCP calls were made; the Supreme Court's own docket PDFs
covered what the snapshot lacked.
