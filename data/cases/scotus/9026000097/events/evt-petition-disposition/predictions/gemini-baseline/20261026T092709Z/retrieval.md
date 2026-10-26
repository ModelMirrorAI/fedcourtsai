# Retrieval Log: *Hellman v. Craven*, No. 26-97

## 1. Provisioned Record (`data/cases/scotus/9026000097/record/`)
- Read `context.json` (`band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `cvsg_date: null`, `mode: "forward"`, `term: 2026`, `snapshot_date: "2026-10-26"`).
- Read `snapshots/2026-10-26.json` (docket sheet for No. 26-97, showing docketing on July 21, 2026, seven amicus briefs filed August 19–21, 2026, Respondent's waiver of right to respond submitted September 24, 2026 and docketed October 1, 2026, and distribution on October 7, 2026 for the Conference of October 23, 2026).
- Read `documents/documents.json`, `documents/questions-presented.txt`, `documents/petition.txt` (full petition for a writ of certiorari), and `documents/appendix.txt` (First Circuit opinion in *Hellman v. Craven*, 168 F.4th 255 (1st Cir. Feb. 20, 2026), District Court opinion dismissing complaint under Rule 12(b)(6), and relevant constitutional/statutory/regulatory provisions).

## 2. Repository Base Rates (`metrics/statpack.md` & `docs/outcome-decomposition.md`)
- Consulted `metrics/statpack.md` for `sal-v4` baseline-band cert grant rates across OT2017–OT2025 (~0.9% pooled) and amicus-count / relist cuts.
- Consulted `docs/outcome-decomposition.md` for `cert-v3` mechanical claim definitions, conditional baselines (`summary-disposition-route` ~0.354 over paid grants), and relist hazard rates (~0.263 at one distribution).

## 3. Corpus & External Retrieval
- **Corpus Query (`uv run fedcourts query --court scotus --docket-number 26-97`)**:
  - Confirmed corpus metadata for `scotus/9026000097`: `originating_court: "ca1"`, `originating_docket_number: "25-1417"`, `salience_score: 0.0145`, `distribution_count: 1`, `response_requested: null`, `response_filed_at: null`.
- **CourtListener MCP (`mcp_courtlistener_search`)**:
  - Queried `type="o"`, `case_name="Hellman v. Craven"` and `court="ca1"`, `docket_number="25-1461"` (0 results returned in the CourtListener opinion index; the full text of the First Circuit's February 20, 2026 opinion, 168 F.4th 255, and the District Court's opinion were already provisioned in full in `record/documents/appendix.txt`).
