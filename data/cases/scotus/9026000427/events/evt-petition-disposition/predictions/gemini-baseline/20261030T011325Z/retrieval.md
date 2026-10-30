# Retrieval Log

## 1. Provisioned Record and Metrics Inspected

- `data/cases/scotus/9026000427/events/evt-petition-disposition/event.yaml` — Cert-stage petition disposition event (`moment: distribution`, `opened_at: '2026-09-29'`).
- `data/cases/scotus/9026000427/record/context.json` — Frozen context (`mode: forward`, `band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, `term: 2026`, `snapshot_date: 2026-10-30`).
- `data/cases/scotus/9026000427/record/snapshots/2026-10-30.json` — SCOTUS docket snapshot for No. 26-427 (*Richard W. Coleman, Jr. v. Merit Systems Protection Board*), showing petition filed September 29, 2026 (*pro se*), waiver of right of respondent MSPB to respond filed October 19, 2026, and distribution on October 21, 2026 for the Conference of November 6, 2026.
- `data/cases/scotus/9026000427/record/documents/documents.json`, `questions-presented.txt`, and `petition.txt` — Full text of the Petition for Writ of Certiorari and Appendices A–D, including the Federal Circuit's June 10, 2026 nonprecedential *per curiam* decision (No. 2025-2031; Lourie, Schall, Taranto, JJ.), the MSPB's December 30, 2022 Initial Decision and August 14, 2024 nonprecedential Final Order (Docket No. DC-1221-22-0109-W-1), and the Federal Circuit's August 6, 2026 order denying panel rehearing and rehearing *en banc*.
- `metrics/statpack.md` and `metrics/statpack.json` — Checked `sal-v4` cert grant-family base rates by band (`baseline` band ~1.01% in OT2025, ~1.07% in OT2024, ~1.18% in OT2023), cert-order summary/GVR share among grants (~48.9% across OT2017–OT2025), and per-Justice authorship rates.

## 2. Corpus Queries (`uv run fedcourts query`)

1. **Query 1 — Recent 2020s SCOTUS resolved priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Purpose: Checked recent resolved SCOTUS dispositions in the 2020s era and verified salience-score and disposition patterns across baseline vs. elevated/high-salience filings.

2. **Query 2 — SCOTUS priors filtered by Federal Circuit panel judges (Lourie, Schall, Taranto):**
   - Command: `uv run fedcourts query --court scotus --judge Lourie --judge Schall --judge Taranto --limit 10`
   - Transfer line: `ranged corpus reads: 641 GET(s), 167968768 byte(s)`
   - Purpose: Checked whether any resolved SCOTUS corpus records carry panel judge tags matching the Federal Circuit panel (`Lourie`, `Schall`, `Taranto`); returned 0 matching SCOTUS rows because lower-court panel judges are not populated on SCOTUS docket rows.

## 3. External Tool Queries (CourtListener MCP)

1. `mcp_courtlistener_search` (`type="o"`, `court="cafc"`, `case_name="Coleman v. Merit Systems Protection Board"`) — Checked for indexed opinions or subsequent citations to the June 10, 2026 nonprecedential decision in No. 2025-2031 (0 results indexed).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Merit Systems Protection Board" "Individual Right of Action""`) — Checked whether the Supreme Court has previously addressed IRA jurisdiction and continuing-reprisal theories under 5 U.S.C. §§ 1221 and 2302(b)(8) (0 results).
3. `mcp_courtlistener_search` (`type="o"`, `court="cafc"`, `q=""Bosley" "162 F.3d 665""`) — Retrieved 16 Federal Circuit decisions applying *Bosley v. Merit Systems Protection Board*, 162 F.3d 665 (Fed. Cir. 1998), confirming that the Federal Circuit has consistently treated ongoing paycheck or duty consequences of a pre-disclosure discrete personnel action as non-actionable in IRA appeals without intracircuit or intercircuit conflict.
