# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` and `REPLAY_CUTOFF` unset; `context.json` `"mode": "forward"`). No lookup of this case (`scotus/9026000552` / No. 26-552) or any third-party forecast was attempted.

## 1. Corpus CLI Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 10 recent resolved 2020s SCOTUS rows (cert petitions and substantive applications resolved in November 2026, showing typical `sal-v8` salience scores, distribution counts, and denial/dismissal patterns).

2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Result: Returned 10 recent granted 2020s SCOTUS rows (showing multi-distribution / SG-petition / multiple-amici profiles typical of OT2026 cert grants).

3. `uv run fedcourts query --court scotus --citation "142 F.4th 769" --limit 5`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows (printed note that only 195 SCOTUS rows carry parallel reporter citations and the column holds a case's own cites rather than cited authorities).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="142 F.4th 769", num_results=5, fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions", "snippet"])`
   - Result: 0 hits under the reporter citation string (F.4th pagination not yet indexed on that cluster).

2. `mcp_courtlistener_search(type="o", citation="22 F.4th 1014", num_results=5, fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions", "snippet"])`
   - Result: 1 hit — *Mandy Li v. Commissioner of Internal Revenue*, 22 F.4th 1014 (D.C. Cir. Jan. 11, 2022) (`cluster_id: 5793758`, `opinion_id: 5648641`).

3. `mcp_courtlistener_search(type="o", court="scotus", q='"7623(b)" OR "Li v. Commissioner" OR "Lissack"', num_results=10, fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber", "snippet"])`
   - Result: 2 hits, both *Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024) (No. 22-451), confirming no Supreme Court merits opinion on 26 U.S.C. § 7623(b) after *Loper Bright*.

4. `mcp_courtlistener_search(type="o", court="cadc", q='"7623(b)" AND ("Li v. Commissioner" OR "whistleblower")', filed_after="2024-07-01", num_results=10, fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber", "opinions"])`
   - Result: 7 hits in the D.C. Circuit, including *Michael Lissack v. Cmsnr. IRS*, No. 21-1268 (filed Jan. 10, 2025, `opinion_id: 10778209`), *Patrick Kennedy v. Cmsnr. IRS & Roy Meidinger, Sr. v. IRS*, Nos. 21-1133 & 22-1239 (filed July 8, 2025, `opinion_id: 11091074`), *Thomas Shands v. Cmsnr. IRS* (Aug. 7, 2024), and *Mary Trongone v. Cmsnr. IRS* (reissued July 13, 2026).

5. `mcp_courtlistener_search(type="d", court="scotus", q='("Kennedy" OR "Lissack") AND "Commissioner of Internal Revenue"', filed_after="2025-01-01", num_results=10, fields=["caseName", "docketNumber", "dateFiled", "docket_id"])`
   - Result: 0 RECAP SCOTUS dockets returned.

6. `mcp_courtlistener_read_document(opinion_id=5648641, chunk_index=0, chunk_size=8000)`
   - Result: Read opening 8,000 characters of *Mandy Li v. Commissioner of Internal Revenue*, 22 F.4th 1014 (D.C. Cir. 2022), confirming its holding that 26 U.S.C. § 7623(b)(4) confers no Tax Court subject-matter jurisdiction over a threshold Whistleblower Office Form 211 rejection where the IRS did not proceed with an administrative or judicial action.

7. `mcp_courtlistener_read_document(opinion_id=11091074, chunk_index=0, chunk_size=8000)`
   - Result: Read opening 8,000 characters of *Patrick Kennedy v. Commissioner of Internal Revenue*, No. 21-1133 (D.C. Cir. July 8, 2025; 142 F.4th 769), confirming that even when the Whistleblower Office forwards a Form 211 to an IRS operating division, *Li* controls and the Tax Court lacks jurisdiction if the operating division takes no action against any taxpayer.

8. `mcp_courtlistener_read_document(opinion_id=10778209, chunk_index=0, chunk_size=8000)`
   - Result: Read opening 8,000 characters of *Michael Lissack v. Commissioner of Internal Revenue*, No. 21-1268 (D.C. Cir. Jan. 10, 2025; 125 F.4th 245), on remand from the Supreme Court after *Loper Bright*, confirming that Tax Court jurisdiction attaches when the IRS audits the taxpayer and that the D.C. Circuit upheld the Treasury whistleblower definitions rule *de novo* without *Chevron* deference.

9. `mcp_courtlistener_search(type="o", court="scotus", q='"Lissack" OR "Meidinger" OR ("Kennedy" AND "Internal Revenue")', filed_after="2025-01-15", num_results=10, fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id"])`
   - Result: 0 SCOTUS opinions/order-list hits after January 15, 2025, confirming no intervening Supreme Court merits grant or order-list developments on *Lissack*, *Kennedy*, or *Meidinger*.
