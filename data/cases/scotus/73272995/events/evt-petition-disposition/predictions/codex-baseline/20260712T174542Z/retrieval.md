# Retrieval

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” the originating-circuit cut, and the Term 2025 row, to calibrate the aggregate grant rate.
- Consulted the Term 2025 paid/IFP detail in `metrics/statpack.json`; its IFP bucket reports 60 denied, 2 dismissed, and 0 granted among 62 resolved petitions.
- Consulted the repository's general disposition-classification logic in `src/fedcourtsai/pipeline/cert_signals.py` and its generic dismissal fixture in `tests/test_historical.py` to understand how the normalized labels distinguish an express cert denial from an express cert dismissal. No case-specific outcome file was read.
- No `fedcourts query` or `fedcourts open-events` lookup was run.
- No CourtListener MCP, REST API, or web lookup was run.
