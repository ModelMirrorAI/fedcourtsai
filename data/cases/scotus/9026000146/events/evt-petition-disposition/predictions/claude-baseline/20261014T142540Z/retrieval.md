# Retrieval

- CourtListener MCP `search` (type=o, court=ca10, case_name="Daley", filed_after=2025-10-01) → *Daley v. Choate*, No. 24-1191, filed 2025-11-03 (opinion id 10729625).
- CourtListener MCP `get_endpoint_item` opinions/10729625 `plain_text` → returned an unrelated S.D.W. Va. discovery order (a CourtListener data mismatch). Not used.
- Web search "Daley v. Baltazar Tenth Circuit 24-1191 Bivens" → SCOTUSblog case page stub (docket facts only, no disposition).
- Web search "\"Daley v. Choate\" Tenth Circuit 2025" → Tenth Circuit opinion listings showing it as published, from D. Colo.
- `metrics/statpack.md` (committed), "Segment base rate by salience band (sal-v4)" table.
- No `fedcourts query` corpus lookups.
