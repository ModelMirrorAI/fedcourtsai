# Retrieval log (claude-baseline, run 20261003T200236Z)

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
  → `ranged corpus reads: 8 GET(s), 2097152 byte(s)`; returned recent granted SCOTUS
  rows (none topically related).
- `uv run fedcourts query --court scotus --era 2020s --limit 6`
  → `ranged corpus reads: 0 GET(s), 0 byte(s)`; recent SCOTUS rows, none related.
- An earlier invocation with an unsupported `--text` flag errored and returned no rows.

## CourtListener MCP

- `search` (type opinions, courts ca5/ca6/ca8, q `"Horseracing Integrity and Safety"
  nondelegation`, filed after 2025-07-01) → 0 results.

## Web searches

- Fifth Circuit remand decision in *National Horsemen's Benevolent & Protective Ass'n
  v. Black* after *Consumers' Research* (surfaced the June 11, 2026 opinion and TDN
  coverage).
- Oklahoma v. United States No. 25-1325 Solicitor General brief (surfaced the No.
  26-201 petition PDF and an unrelated 1999 OSG page of the same case name).
- FTC v. National Horsemen's 2026 petition / Solicitor General.
- Horseracing Integrity and Safety Authority 2026 petition docket.
- site:justice.gov OSG brief Oklahoma v. United States 25-1325 (no 2026 hit).
- HISA Supreme Court October 2026 petitions / rescheduled conference (nothing new).

## Web fetches

- supremecourt.gov docket pages: 25-1325 (ends at the Sept 21, 2026 "Rescheduled"
  entry; nothing later), 26-199, 26-201, 26-332, 26-335.
- justice.gov/osg/brief/oklahoma-v-united-states-response-hold → a 1999 brief in a
  different case of the same name; disregarded.
- thoroughbreddailynews.com article on the Fifth Circuit staying its mandate (July
  16, 2026); pickpony.com article on the Authority and FTC petitions (Aug. 20, 2026).
- PDFs downloaded from supremecourt.gov and read locally with pypdf: Brief for the
  Federal Respondents (Aug. 28, 2026), Response of the Authority respondents (Aug. 28,
  2026), Reply Brief for Petitioners (Sept. 15, 2026), all in No. 25-1325; Petition
  for a Writ of Certiorari in No. 26-201 (FTC v. National Horsemen's).

No search surfaced a disposition of this petition; the live docket shows it pending.
