# Retrieval log — scotus/73299074 / evt-petition-disposition / claude-baseline / 20260717T180352Z

## Corpus tooling

- `uv run fedcourts query --court scotus --era modern --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:` line
  was printed (the query never reached the corpus). No further corpus queries
  attempted; degraded to the committed statpack per the contract.
- Read committed `metrics/statpack.md` (modern discretionary-cert base rates,
  relist/CVSG cuts, per-Term table) for base-rate context.

## CourtListener MCP (forward mode — unrestricted)

1. `search` (type=d, q="Devillier") — located candidate dockets; too broad.
2. `search` (type=d, q="Devillier" AND "Texas", court=txsd/ca5/scotus) — 0 hits
   (query syntax too restrictive).
3. `search` (type=d, case_name="Devillier v. Texas") — found the underlying
   cases: S.D. Tex. 3:20-cv-00223 (docket 17305392), CA5 21-40750, CA5 21-90043.
4. `call_endpoint` (docket-entries, docket=17305392, newest first, 30 entries) —
   remand history: CA5 remand Dec 2024; Texas's motion to remand to state court
   Dec 13, 2024; M&R Jan 5, 2026; order adopting M&R Apr 9, 2026; documents
   transmitted Apr 10–14, 2026. This is the order the mandamus petition targets
   (filed Apr 24, 2026).
5. `search` (type=d, case_name="In re Devillier", filed after 2025-06-01) — 0
   hits; no CA5 mandamus docket appears in RECAP.

None of these calls surfaced any disposition of this petition itself (none
exists — it is distributed for the 9/28/2026 conference).

## Web searches

None.
