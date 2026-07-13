# Retrieval log — scotus/73275187, evt-petition-disposition, claude-baseline, 20260713T075800Z

Mode: `forward` (pending case; retrieval unrestricted). No lookup sought or
surfaced this petition's own disposition — it is undecided.

## Committed base rates

- Read `metrics/statpack.md`, sections "Modern discretionary-cert petitions
  by disposition" (grant ~4.9% resolved, denial-reweighted), "by originating
  circuit", "by relist count" / "by CVSG status" (both entirely `(unknown)`
  buckets — unusable), and the per-Term table (Term 2025: est. grant rate
  4.9%, paid 125 filings).

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "524 U.S. 321" --corpus-backend ranged`
   — priors citing *Bajakajian*. Zero rows.
   `ranged corpus reads: 408 GET(s), 106954752 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged`
   — same-era resolved priors. Returned recent cert dockets including
   several distributed for the 6/29/2026 conference and granted/denied
   2026-06-30 (*Monsanto*, *Petersen*, *McCoy*, *Viramontes*, *Wells*),
   which established that the cleanup-conference orders issued June 30 and
   that this petition, distributed for that same conference, was not among
   them — the carried-over-the-summer signal used in `reasoning.md`.
   `ranged corpus reads: 408 GET(s), 106954752 byte(s)`

## Web fetch (this case's own docketed filing)

3. `curl` of the petitioner's supplemental brief PDF from the snapshot's
   docket link (`supremecourt.gov/DocketPDF/25/25-246/414988/…Supplemental%20Brief.pdf`),
   text extracted locally with pypdf. Purpose: identify what the
   Dec-2025-to-Jun-2026 hold was for. It names *Pung v. Isabella County*
   and argues the QP survives *Pung* untouched.

## CourtListener MCP

4. `search(type=o, court=scotus, q="Pung Isabella County excessive fines")`
   — verified *Pung v. Isabella County*, No. 25-95, decided 2026-06-23,
   independently of the petitioner's characterization. One result; no
   opinion text pulled.

Total retrieval calls: 4 (2 corpus, 1 web fetch, 1 MCP) — well inside the
~25-call budget.
