# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/petition.txt`, `record/documents/questions-presented.txt`, the event's `event.yaml`, `metrics/statpack.md` (modern cert by disposition, by circuit, relist and CVSG cuts, per-Term table, salience band table sal-v4).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6`
   `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   Returned 26A326, 26A274, 26A203, 26A124 (2026 emergency applications), 25-246 Jouppi v. Alaska, 25-238 Viramontes v. Cook County. Not posture-similar; used only as a sanity check on modern grant shapes.
2. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 4`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Returned four 2026 applications (26A305, 26A306, 26A296, 26A298). Not used.

(A first attempt passed a free-text argument and was rejected by the CLI; no corpus read occurred.)

## CourtListener MCP

- `search` type `d`, court `scotus`, q `Garcia v. Hobbs` — 0 results.

## Web searches (forward mode)

- "Louisiana v. Callais Supreme Court decision 2026 Voting Rights Act Section 2" — confirmed Callais decided April 29, 2026, 6–3 (Alito, J.), narrowing Section 2. Public information predating the snapshot; used as forward signal.
- "Trevino v. Hobbs Soto Palmer certiorari Supreme Court Washington Legislative District 15 2026" — located companion docket No. 25-918 and its filings.

## Web fetches (supremecourt.gov)

- Docket page for No. 25-901 (this case) — matched the provisioned snapshot; no entries after June 17, 2026. No disposition surfaced.
- Docket page for No. 25-918 (Trevino v. Hobbs) — response requested Mar 25, 2026; motion to expedite denied May 26, 2026; distributed for the 9/28/2026 conference.
- 25-901 Brief of respondent State of Washington (June 2, 2026) — read in full (PDF text extracted locally).
- 25-901 Reply of petitioner (June 10, 2026) — read in full.
- 25-918 Revised petition — read the questions presented and statement of related proceedings.
- 25-918 Brief in opposition of Soto Palmer respondents (June 2, 2026) — read the introduction, summary of argument, and the passages discussing Garcia and Callais.
- 25-918 Petitioners' May 17, 2026 letter re denial of Rule 60(b) motion, with the district court's May 15, 2026 order attached — read the letter and the order's first five pages.
- 25-918 Motion to expedite (May 15, 2026) — read the first three pages.

Nothing retrieved revealed this petition's disposition; the case is pending as of the snapshot.
