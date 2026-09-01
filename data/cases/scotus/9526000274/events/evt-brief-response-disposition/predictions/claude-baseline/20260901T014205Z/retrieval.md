# Retrieval log — claude-baseline, 26A274, 20260901T014205Z

Beyond the provisioned snapshot, event, and context (no `record/documents/`
were provisioned for this cell):

## Corpus

- `uv run fedcourts query --court scotus --include-applications --limit 12`
  — recent SCOTUS application priors (surfaced 26A203, NPS v. National Trust
  for Historic Preservation: substantive, response requested, referred, 7
  amici, granted 2026-08-31, used as a ladder/amicus comparable).
  Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.

## Committed statpack

- `metrics/statpack.md`, "The interim docket (applications)" — pooled
  strictly-prior substantive grant rate for an OT2026 application:
  31/296 ≈ 10.5% (Terms 2025 + 2024), clearing the 50-resolved floor.
  Also read the merits section header in passing (not used).

## Web (forward mode — unrestricted)

- WebSearch: `NRCC "Brown v. FCC" Fourth Circuit stay application Supreme
  Court 26A274` — identified the underlying litigation (CA4 No. 26-1785,
  FCC lowest-unit-charge public notice set aside Aug 25, 2026; CA4 denied
  the committees' stay).
- WebSearch: `Supreme Court stay application lowest unit rate NRCC NRSC
  government response FCC solicitor general September 2026` — coverage
  reporting FCC/DOJ backing for the committees' stay effort.
- WebFetch: insideradio.com article "Court Rejects Stay, Makes Lowest Unit
  Rate Ruling Effective Immediately" — CA4 stay denied 2-1 on Aug 28,
  mandate issued immediately, general-election ad window opens Sept 4, 2026.
- WebFetch: wiley.law alert "Supreme Court Decision Renews Focus on
  Political Advertising and Lowest Unit Charge" — NRSC v. FEC (June 30,
  2026, 6-3): coordinated party expenditure limits held unconstitutional;
  its interplay with the March 2026 FCC guidance.
- WebFetch (failed, HTTP 403): the filed US/FCC response PDF at
  supremecourt.gov (26A274GovtResponse.pdf) — could not read the
  government's stated position directly.
- WebFetch (failed, HTTP 403): Justia page for the CA4 opinion
  (26-1785, Aug 25, 2026).

No retrieval touched 26A274's own disposition (none exists yet — the
requested response is due Sept 3), and nothing under `data/qp-topics/` was
read.
