# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s`
  stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  Returned 20 recent SCOTUS rows, almost all 26A-series applications and one
  dismissed paid petition; no cert-stage prior close to this case's subject,
  so it informed nothing beyond confirming the corpus was reachable.
- `metrics/statpack.md` (committed): read "Modern discretionary-cert petitions
  by disposition", "Modern cert petitions by originating circuit", "Cert
  petitions by relist count (paid scored segment)", "Cert petitions by CVSG
  status (paid scored segment)", "Cert petitions by salience band", "SCOTUS
  cert petitions by Term", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

- `mcp__courtlistener__search` (type `o`, court `ca9`, query "Roberts v.
  Inslee Shriners", filed after 2025-06-01): **failed, HTTP 429 rate limit**
  ("300/hour", retry in ~400 s). Not retried; the Ninth Circuit memorandum was
  obtained from the docket appendix instead (below).

## Web fetches (forward cell, unrestricted)

All from links carried in the provisioned snapshot or from supremecourt.gov
docket pages:

- Governor Ferguson's brief in opposition (Aug 24, 2026), from the snapshot's
  docket link; text extracted locally with pypdf.
- Shriners respondents' brief in opposition (Aug 24, 2026), same method.
- Petitioners' reply (Sep 14, 2026), same method.
- Appendix to the extension application 25A911 (Feb 6, 2026), which
  reproduces the Ninth Circuit memorandum in No. 24-1949 (Dec 10, 2025, NOT
  FOR PUBLICATION, McKeown, Paez, Sanchez) and the district court order.
- Order list of June 1, 2026 (608 U.S.), to confirm No. 25-1119 Curtis v.
  Inslee was denied in the plain "Certiorari Denied" list with no separate
  writing.
- Supreme Court docket pages: No. 25-1119 (Curtis v. Inslee: waivers, amicus,
  one distribution, denied June 1, 2026, no response requested); No. 25-1280
  (Boysen v. PeaceHealth: waivers, distributed June 2, Response Requested June
  17, NCLA amicus, BIOs Sep 4 and Sep 8); No. 26-220 (Boyd v. Shriners, Third
  Circuit: petition filed Aug 12, response due Sep 18); No. 26-268 (Brock v.
  City of Bellingham: petition Aug 24, waiver Sep 2, distributed Sep 9 for the
  Sep 28 conference).
- One blog post (slphrbenefitsupdate.com, June 2, 2026) on the Curtis denial.

## Web searches

- `"Curtis v. Inslee" certiorari petition Supreme Court denied OR granted 2026`
- `"Boysen v. PeaceHealth" Supreme Court petition certiorari`
- `Supreme Court cert petition "response requested" OR "call for response" grant rate statistics percent granted`

None of these surfaced this petition's own disposition; No. 25-1327 is
pending for the September 28, 2026 conference.
