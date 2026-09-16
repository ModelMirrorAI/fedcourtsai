# Retrieval log

Mode `forward`; retrieval unrestricted. Seventeen calls, under the advisory
budget of 25.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)` (20 rows; read
  distribution counts of recent grants for shape).
- `uv run fedcourts query --court scotus --era 2020s --disposition gvr`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (20 rows; recent GVRs
  cluster at two to four distributions).
- Base rates from the committed `metrics/statpack.md` (segment table by
  salience band, relist and CVSG cuts, per-Term table).

## CourtListener MCP

- `search` (opinions, ca9, Aug to Sep 2025, "Soto Palmer" Hobbs Trevino):
  one hit, Susan Palmer v. Jose Trevino, No. 23-35595, filed 2025-08-27,
  published; panel not populated.

## Web searches (engine-surfaced)

- "Louisiana v. Callais 2026 Supreme Court decision holding Section 2 Voting
  Rights Act"
- "Garcia v. Hobbs Supreme Court petition certiorari 2026 Washington
  legislative district 15 racial gerrymander"
- "Callais order list vacated remanded further consideration in light of
  Louisiana v. Callais 2026 petitions"
- "Supreme Court June 2026 order list Voting Rights Act petitions Callais
  granted vacated remanded ..."

## Web fetches

- supremecourt.gov docket 25-918 (entries and document links; no entry after
  2026-06-17)
- supremecourt.gov docket 25-901, Garcia v. Hobbs (twice: entries, then the
  State brief URL)
- Brief of respondent State of Washington, 25-918 (June 2, 2026): asks for
  GVR in light of Callais
- Reply brief of petitioners, 25-918 (June 10, 2026)
- Petitioners' May 17, 2026 letter re denial of Rule 60(b) motion
- Brief of respondent State of Washington, 25-901 (June 2, 2026): asks for
  a matching GVR, or alternatively denial
- Order list of May 18, 2026 (Callais GVRs with Justice Jackson dissenting)
- Wikipedia, Louisiana v. Callais (secondary summary of the April 29, 2026
  decision)
- SCOTUSblog case page for 25-918 (pending; no commentary)
- congress.gov CRS report LSB11431 on Callais: HTTP 403, not read

The fetch tool's PDF summaries were unreliable; the PDFs it saved were
text-extracted locally with pypdf and read directly. Nothing under
`data/qp-topics/` was read. No outcome for this petition was encountered.
