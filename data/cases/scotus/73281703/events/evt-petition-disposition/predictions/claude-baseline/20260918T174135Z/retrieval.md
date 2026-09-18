# Retrieval log

## Corpus tooling
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  - stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  - Returned 8 rows: four substantive applications granted in August/September 2026 (26A326, 26A274, 26A203, 26A124) and four OT2025 cert grants from the June 29, 2026 conference (25-246 Jouppi v. Alaska, distribution_count 3; 25-238 Viramontes, 22; 25-566 Grant, 17; 25-965 Grand, 5). Used only as shape: recent grants of paid petitions came after multiple distributions, consistent with the relist-before-grant habit assumed in the relist claim. No prior shared this case's subject matter; there is no topic filter for SCOTUS rows.

## Committed base rates
- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "by CVSG status (paid scored segment)", "Cert petitions by salience band", "Petitions by originating court (incl. state courts)", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)". Pooled the `elevated` bracketed `reached` figure over OT2017-OT2024 (17.2%, weighted n 2810).

## CourtListener MCP
- `search` (type `d`, court `scotus`, docket_number `25-1028`): 0 results.
- `search` (type `d`, court `scotus`, q `Smith Michigan Department of Corrections`, filed after 2026-01-01): 0 results.
- `call_endpoint` `docket-entries` for docket 73281703: 0 results (SCOTUS dockets on CourtListener carry no entries; the supremecourt.gov snapshot is the record).

Purpose of the first two: to confirm the BIO's footnote that certiorari was denied on June 29, 2026 in the Sixth Circuit's Smith v. Michigan Dep't of Corrections (whether section 504 supplies a private retaliation action). Not confirmed; treated as the BIO's assertion.

## Web fetch
- The petitioner's reply brief, docketed August 18, 2026, from supremecourt.gov (`.../25-1197/419365/20260818131348116_cert reply 25-1197 Greer v Benton School District.pdf`). The fetch tool's summary was unreliable, so the saved PDF's text was extracted locally and read in full. It is the case's own filing, predates the snapshot, and is within the forward-mode baseline; it reveals nothing about the disposition.

No search surfaced this case's disposition; the petition is set for the September 28, 2026 conference and is undecided as of this run.
