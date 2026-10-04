# Retrieval log — claude-baseline, scotus/73274853, evt-brief-judgment, run 20261004T201824Z

Forward cell; retrieval unrestricted. Nothing retrieved contained a disposition.

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "594 U.S. 482"` (PennEast known-case lookup)
   - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - stderr note: citations filter sparsely populated (200 scotus rows carry any cite); returned no rows.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   - stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Returned recent granted dockets (first 8 inspected); none doctrinally similar; not used.

Base rates: `metrics/statpack.md`, section "The merits docket (granted cases)" — pooled
grant Terms 2017–2024 (the rendered rows strictly before OT2025): 360/516 = 69.8%.

## CourtListener MCP

3. `search` (type `o`, court `ca8`, q: "WBI Energy" Hoffmann "just compensation" "Natural Gas Act") → 1 hit:
   WBI Energy Transmission, Inc. v. 189.9 rods…, 132 F.4th 1058 (8th Cir. Mar. 24, 2025), No. 24-1693, opinion id 10829157.
4. `read_document` (opinion_id 10829157) → full text of the Eighth Circuit opinion (Stras, J.; Shepherd and Kelly, JJ.), ~22.9k chars.

## Web

5. `WebFetch` https://www.supremecourt.gov/docket/docketfiles/html/public/25-159.html — docket entries June 2026 onward, amicus list, document links. Surfaced post-cutoff entries of 21 Sept 2026 (US merits amicus brief supporting respondent; SG motion for divided argument; Chamber of Commerce and INGAA/API amicus briefs).
6. `WebSearch` "Hoffmann v. WBI Energy Transmission Solicitor General brief Natural Gas Act just compensation state law 25-159" — located the QP page and SCOTUSblog case page; not otherwise used.
7. `WebFetch` https://www.supremecourt.gov/DocketPDF/25/25-159/409699/20260522181308374_Hoffmann-5.22-final.pdf — the United States' CVSG brief (May 2026). The fetch tool could not read the PDF; text extracted locally with pypdf (50k chars). Read: Discussion intro, Part B (split, importance, vehicle), Conclusion ("should be granted").
8. `WebFetch` https://www.supremecourt.gov/DocketPDF/25/25-159/425110/20260921193036019_Hoffmann_bsacUnitedStates.pdf — the United States' merits amicus brief supporting respondent (Sept 2026). Same local extraction (73k chars). Read: cover, table of contents, Summary of Argument, Conclusion ("should be affirmed").

## Subagents (reading provisioned files only)

- One subagent summarized `record/documents/merits-brief-petitioner.txt` in full.
- One subagent summarized `record/documents/merits-brief-respondent.txt` in full.

Total external calls: 2 corpus queries, 2 MCP calls, 4 web calls — within the advisory budget.
