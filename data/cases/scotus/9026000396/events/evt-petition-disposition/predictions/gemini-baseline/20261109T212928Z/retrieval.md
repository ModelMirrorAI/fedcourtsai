# Retrieval Log

## 1. Corpus Lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --q "3632" --limit 10`
   - Result: Failed (exit code 2; `--q` is not a valid flag on `fedcourts query`).
2. `uv run fedcourts query --court scotus --docket-number 25-818 --include-open --full`
   - Stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/73279955`, *Terrell Anthony Hargrove v. Ian Healy, Warden*, No. 25-818, originating from CA6 No. 24-3809; filed 2026-01-12, distributed once for 2026-04-17 conference, response not requested, cert denied 2026-04-20).
3. `uv run fedcourts query --court scotus --docket-number 25-5930 --include-open --full`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/73281102`, *William Maxwell v. Sandra Dinis, Acting Warden*, No. 25-5930, originating from CA5 No. 23-40699; filed 2025-10-22, cert granted 2026-06-01, court-appointed amicus curiae in support of judgment below).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", q='"3632(d)(4)(C)" "supervised release"')`
   - Result: Returned 15 opinion clusters, including *Hargrove v. Healy* (6th Cir. Sept. 10, 2025), *Gonzalez v. Herrera* (9th Cir. Aug. 19, 2025), *Rivera-Perez v. Stover* (2d Cir. Mar. 26, 2026), *Osorio-Calderon v. Warden FCI Sandstone* (8th Cir. June 30, 2026), *Fortner v. Eischen* (8th Cir. Mar. 13, 2026), *Bonnie v. Warden Dunbar* (4th Cir. Nov. 5, 2025), and *Hogan v. FCI, La Tuna Case Mgr* (5th Cir. Oct. 9, 2026).
2. `mcp_courtlistener_read_document(opinion_id=11349983)`
   - Result: Full text of *Jose Osorio-Calderon v. Warden, FCI Sandstone*, No. 25-3090 (8th Cir. June 30, 2026) (addressing judicial review of BOP prerelease custody placement under 18 U.S.C. §§ 3621(b) and 3632(d)(4)(C)).
3. `mcp_courtlistener_read_document(opinion_id=11493186)`
   - Result: Full text of *Hogan v. FCI, La Tuna Case Mgr*, No. 25-50315 (5th Cir. Oct. 9, 2026) (addressing accrual of FSA time credits prior to arrival at designated BOP facility).
4. `mcp_courtlistener_search(type="o", q='"Gonzalez v. Herrera" "3632(d)(4)(C)"')`
   - Result: Returned 3 opinion clusters citing *Gonzalez v. Herrera*: *Gonzalez v. Herrera* (9th Cir.), *Rivera-Perez v. Stover* (2d Cir.), and *Bonnie v. Warden Dunbar* (4th Cir.), confirming no subsequent circuit split has emerged in favor of petitioner's interpretation.
