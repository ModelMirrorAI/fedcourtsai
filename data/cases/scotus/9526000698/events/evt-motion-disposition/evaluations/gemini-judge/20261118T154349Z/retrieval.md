# Evaluator Retrieval Log (`scotus/9526000698` — `evt-motion-disposition` — `20261118T154349Z`)

All lookups below were used solely to verify lower-court procedural facts, docket numbers, and holdings cited in `gemini-baseline`'s `reasoning.md` (and to verify `statpack_digest` parity); `predicted_reasoning_quality` was graded strictly against the staged record (`outcome.json` and `record/snapshots/2026-11-18.json`).

## 1. `fedcourts` Corpus & Statpack CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9526000698" --event "evt-motion-disposition" --role evaluator`
   - Transfer line: none.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --decided-before 2026-11-15 --limit 50`
   - Stderr transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Purpose: Checked whether `gemini-baseline`'s prior-denial query returned any earlier `Simpkins` row that might have supplied secondary docket numbers (`0` matches for `Simpkins`).
3. `uv run fedcourts statpack-at data/cases/scotus/9526000698/record/blinded/claude-baseline/ --ref HEAD --out-dir /tmp/statpack-at/claude-baseline`
   - Confirmed `statpack_digest` `sha256:51adef9eb718f3df6423188358b9c32ada5eda492c113a279dca2a17bbba64c4` (`7ea07eba62d3`) matches the committed statpack; scratch directory removed immediately after check.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 72231859, "fields": ["entry_number", "date_filed", "description"]}, num_results=35)`
   - Verified D.D.C. `1:26-cv-00304` (`Simpkins v. State of Tennessee`) entry dates (`2026-03-04` ECF 21/22, `2026-03-19` ECF 25, `2026-03-24`, `2026-04-30` ECF 27, `2026-10-14` ECF 30) and ECF 15 (`MOTION for Referral to U.S. Attorney`).
2. `mcp_courtlistener_read_document(opinion_id=11241240, chunk_index=0, chunk_size=6000)` and `mcp_courtlistener_read_document(opinion_id=11241240, chunk_index=[1, 2], chunk_size=6000)`
   - Read full text (15,590 chars) of Judge Amir H. Ali's January 14, 2026 Memorandum Opinion in `Simpkins v. State of Tennessee`, No. `25-04566` (D.D.C.), verifying its four actual dismissal grounds (FRCP 8(a), *Rooker-Feldman*, lack of jurisdiction over M.D. Tenn., and *Younger* abstention) and confirming it did not cite `Case No. 48621`, `2024-CR-5582`, the Eleventh Amendment, or 28 U.S.C. § 2283.
3. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry__docket": 72231859, "fields": ["id", "document_number", "description", "is_available"]}, num_results=30)`
   - Verified document descriptions for D.D.C. `1:26-cv-00304` entries 7–31.
4. `mcp_courtlistener_search(type="r", court=["cadc", "dcd"], party_name="Simpkins", fields=["caseName", "docketNumber", "court_id", "dateFiled", "dateTerminated", "docket_id"], num_results=15)`
   - Confirmed no D.C. Circuit (`cadc`) RECAP docket exists on CourtListener for `Simpkins`.
5. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 72232400, "fields": ["entry_number", "date_filed", "description"]}, num_results=20)`
   - Verified the 5 docket entries in D.D.C. `1:26-cv-00310` (`Simpkins v. Caesar`).

## 3. Web Searches

None.
