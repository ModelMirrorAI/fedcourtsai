# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/petition.txt`, `record/documents/questions-presented.txt`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned eight recent granted rows (four 26A stay applications and four OT2025 cert grants at 3–22 distributions). Used only as a reminder of what a granted docket's distribution trajectory looks like; none was a comparable land-use or state-court-writ prior.

## Web (forward cell, unrestricted)

- Fetched the petitioner's supplemental brief from the docket link in the snapshot:
  `https://www.supremecourt.gov/DocketPDF/25/25-1299/423995/20260911183550672_CAGI%20Supp%20MAIN%20E%20FILE%20Sept%2011%202026.pdf`
  (38 pages including a supplemental appendix). Text extracted locally with pypdf. It reports the York County Court of Common Pleas order of July 21, 2026 affirming the Board of Zoning Appeals and the August 27, 2026 denial of reconsideration; it asks for a grant or, alternatively, vacatur and remand under Philadelphia Newspapers v. Jerome.
- One web search: `Supreme Court certiorari granted 2026 substantive due process land use zoning "shocks the conscience" circuit split`, to check for a pending merits case this petition could be held for. None found. The results included a May 2026 local news item (WRHI) about the petition's filing, which predates the snapshot and was not used; no disposition of this petition surfaced.

## CourtListener MCP

- Not used. The snapshot is same-day and the docket has no filed opposition; nothing on CourtListener would have added to the supremecourt.gov record.
