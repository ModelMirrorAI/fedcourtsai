# Retrieval log — scotus/73500230 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Cell mode: `forward` (pending petition; retrieval unrestricted).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:`
  stderr line was printed (the call never reached the corpus). No retry;
  degraded to the committed statpack per the prompt contract.
- Read committed `metrics/statpack.md` (and the per-Term fee-class detail in
  `metrics/statpack.json`) for base rates: modern discretionary-cert grant rate
  ~2.5–3.3% per Term; paid-petition est. grant rate 5.4% (OT2025) / 6.9%
  (OT2024); relist and CVSG cuts noted (this case has neither signal yet).

## CourtListener MCP

- `search` (type=d, court=scotus, case_name="Gopher Media") — 0 results.
- `search` (type=d, court=scotus, q="Gopher Media") — 0 results.
- `call_endpoint` dockets (court=scotus, docket_number=25-1067) — found
  Gopher Media LLC v. Melone, No. 25-1067, filed 2026-03-10,
  `date_terminated: null` (companion petition on the same split still pending;
  forward signal about a related case, not this case's outcome).
- `call_endpoint` docket-entries (docket=73281353) — 0 results (CourtListener
  carries no entry-level data for that SCOTUS docket).

## Web searches

None.

No lookup touched this case's own disposition (none exists yet — the petition
is distributed for the 2026-09-28 conference).
