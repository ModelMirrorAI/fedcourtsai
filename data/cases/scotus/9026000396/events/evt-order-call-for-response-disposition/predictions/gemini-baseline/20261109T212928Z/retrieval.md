# Retrieval Log

## 1. Corpus Tooling (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000396" --event "evt-order-call-for-response-disposition" --role predictor`
   - Resolved `case_id` (`scotus/9026000396`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --court scotus --docket-number "25-818"`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned `scotus/73279955`, *Terrell Anthony Hargrove v. Ian Healy, Warden* (No. 25-818), originating from `ca6` (No. 24-3809), distributed once (`2026-04-17`), cert denied `2026-04-20`.
3. `uv run fedcourts query --court scotus --docket-number "25-5930"`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73281102`, *William Maxwell v. Sandra Dinis, Acting Warden* (No. 25-5930), originating from `ca5` (No. 23-40699), cert granted `2026-06-01` after 3 distributions.
4. `uv run fedcourts query --court scotus --limit 10`
   - Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned 10 recent resolved SCOTUS petitions to inspect recent Term disposition patterns.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", q='"3632(d)(4)(C)" "supervised release"', filed_after="2025-01-01")`
   - Returned 9 opinions citing `3632(d)(4)(C)` and `"supervised release"` since January 1, 2025, including *Hargrove v. Healy* (6th Cir., opinion_id `11136016`), *Gonzalez v. Herrera* (9th Cir., opinion_id `11123272`), *Rivera-Perez v. Stover* (2d Cir., opinion_id `11282260`), *Osorio-Calderon v. Warden FCI Sandstone* (8th Cir., opinion_id `11349983`), *Fortner v. Eischen* (8th Cir., opinion_id `11275195`), *Bonnie v. Warden Dunbar* (4th Cir., opinion_id `11198702`), and *Hogan v. FCI, La Tuna Case Mgr* (5th Cir., opinion_id `11493186`).
2. `mcp_courtlistener_read_document(opinion_id=11349983, chunk_index=0)`
   - Read chunk 0 of *Osorio-Calderon v. Warden FCI Sandstone* (8th Cir. June 30, 2026) — confirmed it concerns judicial review of prerelease custody placement under 18 U.S.C. § 3621(b), not reducing supervised release terms.
3. `mcp_courtlistener_read_document(opinion_id=11198702, chunk_index=0)`
   - Read chunk 0 of *Bonnie v. Warden Dunbar* (4th Cir. Nov. 5, 2025) — confirmed it concerns sentence aggregation under 18 U.S.C. § 3584(c) for disqualifying offenses under § 3632(d)(4)(D).
4. `mcp_courtlistener_read_document(opinion_id=11493186, chunk_index=0)`
   - Read chunk 0 of *Hogan v. FCI, La Tuna Case Mgr* (5th Cir. Oct. 9, 2026) — confirmed it concerns earning FSA time credits prior to arrival at a designated BOP facility.
5. `mcp_courtlistener_read_document(opinion_id=11136016, chunk_index=0)`
   - Read chunk 0 of *Hargrove v. Healy*, 155 F.4th 530 (6th Cir. Sept. 10, 2025) — confirmed the 2-1 panel split (Nalbandian & Griffin, JJ., vs. Moore, J., dissenting) holding that FSA credits cannot reduce a supervised-release term and noting the district court's alternative holding on sentence aggregation for a disqualifying offense.
6. `mcp_courtlistener_read_document(opinion_id=11123272, chunk_index=0)`
   - Read chunk 0 of *Gonzalez v. Herrera*, 151 F.4th 1076 (9th Cir. Aug. 19, 2025) — confirmed the Ninth Circuit's published holding that § 3632(d)(4)(C) requires applying unused FSA time credits to reduce the length of a supervised release term.
