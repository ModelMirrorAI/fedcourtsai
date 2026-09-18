# Retrieval log

Beyond the provisioned inputs (snapshot 2025-10-15, context.json, questions-presented.txt, petition.txt, brief-in-opposition.txt, and the committed `metrics/statpack.md`):

## Corpus tooling
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` — stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Top rows were OT2025 substantive applications and granted petitions unrelated to this case; not used in the number.

## CourtListener MCP
- `get_endpoint_item dockets 73274796` (fields id, case_name, docket_number, date_filed, date_terminated) — docket 25-113, `date_terminated: null`.
- `call_endpoint docket-entries docket=73274796` — 0 results (CourtListener carries no entries for this SCOTUS docket).
- `search type=o court=ca10 q="Renteria" "Superintendent of Insurance" "health care sharing"` — 0 results.
- `search type=o court=ca10 docket_number=23-2123` — 0 results.

## Web (forward mode, unrestricted)
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-113.html` (twice: proceedings list; PDF links). Entries after the snapshot: 2026-05-26 Brief amicus curiae of United States filed; 2026-06-09 DISTRIBUTED for Conference of 6/25/2026; 2026-06-09 Supplemental brief of petitioners filed. No later entry.
- WebFetch `https://www.supremecourt.gov/DocketPDF/25/25-113/409896/20260526191106693_Renteria%205.26.26%20post%20proofs.pdf` (SG amicus brief; text extracted locally with pypdf). Recommendation: hold pending *St. Mary Catholic Parish v. Roy*, No. 25-581 (cert. granted 2026-04-20); preemption question does not warrant review.
- WebFetch `https://www.supremecourt.gov/DocketPDF/25/25-113/412911/20260609105540964_25-113%20Supplemental%20Brief%20and%20Appendix.pdf` (petitioners' supplemental brief; text extracted locally). Asks for a grant now or, alternatively, a hold; appendix carries the New Mexico First Judicial District's 2025-09-24 decision affirming OSI's order and 2026-01-05 orders denying reconsideration.
- WebFetch `https://www.scotusblog.com/cases/renteria-v-new-mexico-office-of-the-superintendent-of-insurance/` — status "Pending Petition"; same timeline; no entry after 2026-06-09.
- WebFetch `https://certpool.com/dockets/25-113` — pending; three distributions listed (9/29/2025, 10/10/2025, 6/25/2026).
- WebSearch `Renteria v. New Mexico Office of the Superintendent of Insurance 25-113 Solicitor General brief health care sharing ministry` — surfaced the SG brief page at justice.gov, SCOTUSblog, certpool, AHCSM press release.
- WebSearch `"Renteria" "New Mexico" Solicitor General recommends Supreme Court health care sharing ministry Gospel Light May 2026` — Law360 headline "US Tells Justices To Hold 'Lightning Rod' Health Ministry Case" (consistent with the brief).
- WebSearch `"St. Mary Catholic Parish v. Roy" 25-581 Supreme Court certiorari granted oral argument Colorado universal preschool` — cert granted 2026-04-20; argument expected fall 2026.

No search surfaced a disposition of this petition; the case is undecided as of 2026-09-18. Roughly 16 retrieval calls in total.
