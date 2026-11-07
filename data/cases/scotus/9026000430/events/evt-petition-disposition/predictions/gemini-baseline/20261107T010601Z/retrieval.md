# Retrieval Log (`scotus/9026000430` / `evt-petition-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

All corpus queries were executed in forward mode (no `--decided-before` cutoff, matching `record/context.json` `"mode": "forward"`).

### A. Companion and Related HISA Dockets (Current Term)

1. `uv run fedcourts query --court scotus --docket-number "26-199"`
   - Transfer stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: `scotus/9026000199` (*Horseracing Integrity and Safety Authority, Incorporated, et al. v. National Horsemen's Benevolent and Protective Association, et al.*), filed `2026-08-17`, open (`disposition: null`), originating from 5th Cir. No. `23-10520`. Entered reasoning to confirm the status and parties of the Authority's lead enforcement petition.

2. `uv run fedcourts query --court scotus --docket-number "26-201"`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/9026000201` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*), filed `2026-08-17`, open (`disposition: null`), Solicitor General D. John Sauer as counsel of record for petitioner FTC. Entered reasoning to confirm the Solicitor General's principal petition on the enforcement question.

3. `uv run fedcourts query --court scotus --docket-number "26-332"`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/9026000332` (*Gulf Coast Racing LLC., et al. v. Horseracing Integrity and Safety Authority, Incorporated, et al.*), filed `2026-09-11`, open (`disposition: null`). Entered reasoning as the companion Appointments Clause cross-petition from the same Fifth Circuit judgment.

4. `uv run fedcourts query --court scotus --docket-number "26-335"`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/9026000335` (*Texas, et al. v. Jerry Black, et al.*), filed `2026-09-14`, open (`disposition: null`). Entered reasoning as Texas's parallel cross-petition challenging HISA's rulemaking provisions.

5. `uv run fedcourts query --court scotus --docket-number "25-1325"`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/73500226` (*Oklahoma v. United States*), filed `2026-05-29`, `distributed_for_conference: "2026-10-09"`, `distribution_count: 1`, open (`disposition: null`), originating from the Sixth Circuit (`ca6`). Entered reasoning to confirm the parallel Sixth Circuit enforcement petition and its earlier distribution.

### B. Prior Round of HISA Petitions (OT2024 GVR Cluster)

6. `uv run fedcourts query --court scotus --docket-number "24-472"`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/72484185` (*National Horsemen's Benevolent and Protective Association, et al. v. Horseracing Integrity and Safety Authority, Inc., et al.*), filed `2024-10-29`, `distributed_for_conference: "2025-06-26"`, `distribution_count: 3`, `date_cert_granted: "2025-06-30"`, `disposition: "gvr"`. Entered reasoning to verify the disposition of the Horsemen's prior cross-petition at the time of the *Consumers' Research* GVR.

7. `uv run fedcourts query --court scotus --docket-number "24-429"`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/72484140` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*), `date_cert_granted: "2025-06-30"`, `disposition: "gvr"`. Entered reasoning to confirm the OT2024 GVR package.

8. `uv run fedcourts query --court scotus --docket-number "24-433"`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/72484144` (*Horseracing Integrity and Safety Authority, Incorporated, et al. v. National Horsemen's Benevolent and Protective Association, et al.*), `date_cert_granted: "2025-06-30"`, `disposition: "gvr"`. Entered reasoning to confirm the OT2024 GVR package.

9. `uv run fedcourts query --court scotus --docket-number "24-465"`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: `scotus/72484176` (*Texas, et al. v. Jerry Black, et al.*), `date_cert_granted: "2025-06-30"`, `disposition: "gvr"`. Entered reasoning to confirm the OT2024 GVR package.

10. `uv run fedcourts query --court scotus --docket-number "24-489"`
    - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: `scotus/72484202` (*Gulf Coast Racing, L.L.C., et al. v. Horseracing Integrity and Safety Authority, Inc., et al.*), `date_cert_granted: "2025-06-30"`, `disposition: "gvr"`. Entered reasoning to confirm the OT2024 GVR package.

### C. Structured Filter Priors Query

11. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
    - Transfer stderr: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
    - Result: Returned recent OT2026 grants including `scotus/9026000012` (No. 26-12, granted after 3 distributions), `scotus/9026000204` (No. 26-204, DOJ petition from 5th Cir. granted after 2 distributions), and `scotus/73281386` (No. 25-1103, government petition from D.C. Cir. granted after 2 distributions). Entered reasoning as context on recent OT2026 grant patterns.

---

## 2. CourtListener MCP Queries

1. `mcp_courtlistener_search(type="o", court="ca5", case_name="National Horsemen's Benevolent and Protective Association v. Black")`
   - Result: 0 hits under that exact full string in search index (full Fifth Circuit opinion text was read directly from provisioned `record/documents/appendix.txt`, App. 1a–50a).

2. `mcp_courtlistener_search(type="o", court="ca6", case_name="Oklahoma v. United States")`
   - Result: Cluster ID `10760271`, *State of Oklahoma v. United States*, Docket No. `22-5487`, decided `2025-12-17` (163 F.4th 294). Entered reasoning to verify the Sixth Circuit's post-*Consumers' Research* remand decision.

3. `mcp_courtlistener_search(type="o", court="ca8", case_name="Walmsley v. Federal Trade Commission")`
   - Result: 0 new post-remand opinions found on CourtListener, confirming the Fifth Circuit's note (Pet. App. 30a n.17) and the BIO's statement that the Eighth Circuit had not yet issued a post-remand opinion in *Walmsley*.

4. `mcp_courtlistener_search(type="o", citation="606 U.S. 656")`
   - Result: Cluster ID `10776820`, *FCC v. Consumers' Research*, 606 U.S. 656, Docket No. `24-354`, decided `2025-06-27`. Entered reasoning to verify the Supreme Court's 2025 nondelegation precedent.
