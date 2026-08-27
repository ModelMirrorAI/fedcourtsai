# Retrieval log

Forward-mode cell; all retrieval concerned the pre-petition lower-court
record and corpus priors/base rates, never this petition's own disposition
(which does not exist yet).

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert base rates; relist, CVSG,
  circuit, and salience-band cuts; the sal-v3 per-Term "Segment base rate by
  salience band" table (baseline bracketed `reached` rates pooled over Terms
  2017–2025 as the anchor).

## Corpus lookups (`fedcourts`)

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned five recency-ranked rows (recent substantive applications and
    pro se petitions), not close comparables; not relied on for any number.

## CourtListener MCP lookups (4 calls)

1. `search` (opinions, ca9, "Quaid v. Granet") — 0 results.
2. `search` (dockets, ca9, q=Quaid, docket_number=25-270) — found
   Quaid, et al. v. Granet, et al., CA9 No. 25-270 (docket 69570664); a
   parallel query without court filter surfaced the underlying district
   dockets: Randy Quaid v. Craig Granet, C.D. Cal. Nos. 2:23-cv-06850 and
   2:24-cv-03455, CA9 No. 25-1026, and the earlier Randy Quaid v. Bruce
   Berman, C.D. Cal. No. 2:21-cv-04793.
3. `call_endpoint` (dockets, id=67722996) — C.D. Cal. 2:23-cv-06850: federal
   question, "Other Statutory Actions", filed 2023-08-18, terminated
   2024-04-23.
4. `call_endpoint` (docket-entries, docket=69570664, latest 5) — pro se
   appellants Randy and Evgenia Quaid; appellees Craig Granet (appearing for
   himself) and R. Scott and Lannette Turicchi.

(One additional `call_endpoint` attempt errored on an invalid parameter and
returned no data.)

## Web searches

None.
