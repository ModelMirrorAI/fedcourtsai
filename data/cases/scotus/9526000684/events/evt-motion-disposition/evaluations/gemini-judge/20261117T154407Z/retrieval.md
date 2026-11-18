# Evaluator Retrieval Log — `scotus/9526000684` (`evt-motion-disposition`)

Evaluator: `gemini-judge` (`run_id`: `20261117T154407Z`)

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court scotus --docket 9526000684 --event evt-motion-disposition --role evaluator`
   - Transfer line: none (path resolution only).
2. `uv run fedcourts query --court scotus --docket-number 26A657`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified pre-snapshot companion application `scotus/9526000657` (*Paul Schultz v. Kevin McCarthy*, CA4 `26-2406`, filed `2026-11-06`, denied `2026-11-10`, `interim_reading: "denied"`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`).
3. `uv run fedcourts query --court scotus --docket-number 26A658`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Verified pre-snapshot companion application `scotus/9526000658` (*Paul Schultz v. H. Jason Gold*, `26-2404`, filed `2026-11-06`, denied `2026-11-11`, `interim_reading: "denied"`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`).
4. `uv run fedcourts query --court scotus --docket-number 25A914`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified cited application `scotus/72353169` (*Nicole Malliotakis, et al. v. Michael Williams, et al.*, decided `2026-03-02`, `interim_reading: "granted"`).
5. `uv run fedcourts query --court scotus --docket-number 26A476`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified cited application `scotus/9526000476` (*Federal Communications Commission v. Sherrod Brown, et al.*, decided `2026-10-14`, `interim_reading: "granted"`).
6. `uv run fedcourts statpack-at data/cases/scotus/9526000684/record/blinded/gemini-baseline/ --ref origin/main --out-dir /home/runner/.gemini/tmp/fedcourtsai/statpack-at/gemini-baseline`
   - Transfer line: none (rebuilt the candidates' pinned statpack build `8a8367f41747`, `sha256:86f2abefec9e0321c5007631d1abc7bf17ab2188b12eda8f922d31c9905f9d14`, into temporary scratch).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73338626`, `fields=["id", "case_name", "docket_number", "date_filed", "date_terminated", "assigned_to_str", "referred_to_str"]`)
   - Verified E.D. Va. docket `1:26-cv-01125` (*Schultz v. BOKF, N.A.*, filed `2026-04-27`, assigned to Judge Leonie M. Brinkema, referred to Magistrate Judge Ivan D. Davis).
2. `mcp_courtlistener_analyze_citations`
   - Verified all six U.S. Reports citations referenced across the candidate rationales: *Hollingsworth v. Perry*, 558 U.S. 183 (2010); *Nken v. Holder*, 556 U.S. 418 (2009); *Ohio Citizens for Responsible Energy, Inc. v. NRC*, 479 U.S. 1312 (1986); *Cheney v. United States District Court*, 542 U.S. 367 (2004); *United States v. Sineneng-Smith*, 590 U.S. 371 (2020); and *Liteky v. United States*, 510 U.S. 540 (1994).
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Clark v. Sweeney" OR "Margolin""`, `fields=["caseName", "docketNumber", "dateFiled", "citation"]`)
   - Verified *Clark v. Sweeney*, No. `25-52` (decided `2025-11-24`), and *Margolin v. NAIJ*, No. `25-767` (decided `2026-05-26`).
4. `mcp_courtlistener_search` (`type="d"`, `court="ca4"`, `docket_number="26-2404"`, `fields=["caseName", "docketNumber", "dateFiled", "dateTerminated"]`)
   - Verified Fourth Circuit docket `26-2404` (*In re: Paul Schultz*).
5. `mcp_courtlistener_search` (`type="d"`, `court="ca4"`, `docket_number="26-2405"`, `fields=["caseName", "docketNumber", "dateFiled", "dateTerminated"]`)
   - Verified Fourth Circuit docket `26-2405` (*In re: Paul Schultz*).
6. `mcp_courtlistener_search` (`type="rd"`, `court="vaeb"`, `docket_number="24-11959"`, `order_by="entry_date_filed desc"`, `num_results=10`, `fields=["caseName", "docketNumber", "entry_date_filed", "entry_number", "short_description", "description"]`)
   - Verified Bankr. E.D. Va. `24-11959` docket entries, including `Dkt. 830` (`2026-10-22`, `"Stay"`) and `Dkt. 833` (`2026-10-29`, `"Order on Motion to Stay"`).

## 3. Web Searches

None.
