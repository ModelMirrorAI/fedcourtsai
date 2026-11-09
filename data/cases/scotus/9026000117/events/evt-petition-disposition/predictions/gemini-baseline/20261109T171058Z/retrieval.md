# Retrieval Log — `scotus/9026000117` (`evt-petition-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

1. **`uv run fedcourts query --court scotus --docket-number 26-116`**
   - **Transfer:** `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - **Result:** Retrieved companion docket `scotus/9026000116` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*, No. 26-116), originating from the Eleventh Circuit (`26-11828`), filed `2026-07-24`, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`, `disposition: null`.
   - **Use:** Confirmed that the companion *Caster* petition for certiorari before judgment is traveling in lockstep with `26-117` at `distribution_count: 3`.

2. **`uv run fedcourts query --court scotus --docket-number 26-118`**
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result:** Retrieved companion docket `scotus/9026000118` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 26-118), originating from the Northern District of Alabama (`2:21-cv-1291-AMM`), filed `2026-07-24`, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`, `disposition: null`.
   - **Use:** Confirmed that the companion *Singleton* direct appeal under 28 U.S.C. § 1253 is also traveling in lockstep with `26-117` at `distribution_count: 3`.

3. **`uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`**
   - **Transfer:** `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - **Result:** Returned 10 OT 2026 `gvr` dispositions, including two direct appeals from a three-judge district court decided on October 5, 2026: *Benancio Garcia, III v. Steven Hobbs, Secretary of State of Washington, et al.* (`scotus/73279753`, No. 25-901) and *Jose A. Trevino, et al. v. Steven Hobbs, Secretary of State of Washington, et al.* (`scotus/73279880`, No. 25-918).
   - **Use:** Established that summary vacatur-and-remand orders on three-judge district court appeals in redistricting cases are coded in the corpus as `disposition: "gvr"`.

4. **`uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`**
   - **Transfer:** `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - **Result:** Returned 10 recent OT 2026 `granted` dispositions (merits grants and emergency application grants).
   - **Use:** Compared distribution counts and procedural postures of full merits grants against summary `gvr` orders.

5. **`uv run fedcourts query --court scotus --docket-number 25-274`**
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result:** Retrieved `scotus/73275213` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 25-274), the prior direct appeal from the May 2025 permanent injunction in this very case (`2:21-cv-01530`), showing `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`.
   - **Use:** Verified that the Supreme Court's May 11, 2026 order vacating the permanent injunction and remanding in light of *Callais* on a 28 U.S.C. § 1253 Jurisdictional Statement was recorded as `disposition: "gvr"`.

6. **`uv run fedcourts query --court scotus --docket-number 25-272` and `--docket-number 25-273`**
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)` (for both)
   - **Result:** `25-273` (`scotus/73275215`, *Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*) likewise showed `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`. (`25-272` was an unrelated First Circuit case.)
   - **Use:** Confirmed identical `gvr` coding for the companion *Singleton* direct appeal in the prior round.

7. **`uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 15` and `--disposition dismissed --limit 15`**
   - **Transfer:** `ranged corpus reads: 1030 GET(s), 270008320 byte(s)` (`summary-reversal`, 0 rows matched in era `2020s`) and `ranged corpus reads: 5 GET(s), 1310720 byte(s)` (`dismissed`, 15 rows returned).
   - **Result:** Showed that recent `dismissed` cases are primarily Rule 46 voluntary dismissals or IFP dismissals, while `summary-reversal` had no matching rows under that filter in the 2020s slice.
   - **Use:** Confirmed that summary vacatur-and-remand orders on jurisdictional statements are categorized under `gvr` rather than `summary-reversal` or `dismissed`.

8. **`uv run fedcourts query --court scotus --docket-number 25-275` and `--era 2020s --disposition other --limit 15`**
   - **Transfer:** `ranged corpus reads: 14 GET(s), 3670016 byte(s)` and `ranged corpus reads: 1030 GET(s), 270008320 byte(s)`
   - **Result:** `25-275` was an unrelated Sixth Circuit case; `--disposition other` returned no rows.
   - **Use:** Confirmed that three-judge court summary dispositions do not land in `other`.

9. **`uv run fedcourts query --court scotus --docket-number 25-830`**
   - **Transfer:** `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - **Result:** Checked docket `25-830` (cited in the Jurisdictional Statement p. 20 as *Abbott v. LULAC*, which was a typo in Appellants' brief as `25-830` is *Kanuszewski v. Shah*).
   - **Use:** Verified docket numbering.

10. **`uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026-06-01 --limit 25` and `--decided-before 2026-05-15 --limit 25`**
    - **Transfer:** `ranged corpus reads: 71 GET(s), 18612224 byte(s)` and `ranged corpus reads: 90 GET(s), 23592960 byte(s)`
    - **Result:** Retrieved `25-234` (*State Board of Election Commissioners v. Mississippi State Conference of the NAACP*, `date_cert_granted: "2026-05-18"`, `disposition: "gvr"`), `25-253` (*Turtle Mountain Band of Chippewa Indians v. Howe*, `disposition: "gvr"`), `25-274` (*Allen v. Milligan*, `disposition: "gvr"`), and `25-273` (*Allen v. Singleton*, `disposition: "gvr"`).
    - **Use:** Confirmed that all May 2026 post-*Callais* vacaturs (including three-judge district court appeals) were coded as `gvr`.

11. **`uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2025-07-01 --limit 25` and `--decided-before 2024-07-01 --limit 25`**
    - **Transfer:** `ranged corpus reads: 98 GET(s), 25690112 byte(s)` and `ranged corpus reads: 174 GET(s), 45613056 byte(s)`
    - **Result:** Retrieved `23-156` (*Speech First, Inc. v. Sands*), `23-60` (*Biden v. Feds for Medical Freedom*), `22-1225` (*Payne v. Biden*), `23-154` (*Kendall v. Doster*), and `23-467` (*Garcia v. Hobbs*), all coded as `disposition: "gvr"`.
    - **Use:** Confirmed that *Munsingwear* vacaturs of moot preliminary injunctions as well as three-judge district court vacaturs with instructions to dismiss are coded in the corpus as `disposition: "gvr"`.

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Allen v. Milligan"`, `filed_after="2026-01-01"`)**
   - **Result:** Found *Allen v. Milligan*, Nos. 25A1314, 25A1315, `cluster_id: 10869022`, `opinion_id: 11336479`, filed `2026-06-02`.
   - **Use:** Located the full text of the Supreme Court's June 2, 2026 opinion granting a stay of the May 26, 2026 preliminary injunction.

2. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Abbott v. LULAC"`, `filed_after="2025-01-01"`)**
   - **Result:** 0 results under that caption string.

3. **`mcp_courtlistener_read_document` (`opinion_id=11336479`)**
   - **Result:** Read the complete text (52,827 chars) of *Allen v. Milligan*, 608 U.S. ___ (June 2, 2026) (Nos. 25A1314, 25A1315), including the four-page *Per Curiam* opinion and Justice Jackson's dissent (joined by Justices Sotomayor and Kagan).
   - **Use:** Verified that a six-Justice majority held that the State is likely to succeed on the merits of both the Fourteenth Amendment intentional vote-dilution claim (under *Alexander*) and the VRA § 2 claim (under *Callais*), and stayed the May 26, 2026 order pending the filing and disposition of the appeal and the *Caster* cert petition.

4. **`mcp_courtlistener_search` (`type="d"`, `court="alnd"`, `docket_number="2:21-cv-01530"`)**
   - **Result:** Found the originating three-judge district court docket, *Milligan v. Allen*, `docket_id: 61494291`.

5. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Allen v. Caster"`, `filed_after="2026-01-01"`) and (`type="r"`, `court="alnd"`, `docket_number="2:21-cv-01530"`, `entry_date_filed_after="2026-05-01"`)**
   - **Result:** Confirmed docket match on `2:21-cv-01530` and switched to `type="rd"` to list individual RECAP documents.

6. **`mcp_courtlistener_search` (`type="rd"`, `court="alnd"`, `docket_number="2:21-cv-01530"`, `entry_date_filed_after="2026-05-01"`, `order_by="entry_date_filed desc"`)**
   - **Result:** Returned 44 docket entries filed since May 1, 2026, including Doc. 537 (`id: 480335147`, the May 26, 2026 Preliminary Injunction Order) and Doc. 544 (`id: 492999516`, the July 20, 2026 Order on Outstanding Motions).
   - **Use:** Identified the post-stay district court orders and located the full un-truncated text of Doc. 537.

7. **`mcp_courtlistener_read_document` (`recap_document_id=492999516`)**
   - **Result:** Read Doc. 544 (filed July 20, 2026), in which the three-judge district court granted the Defendants' unopposed motion to stay further district-court proceedings pending resolution of the Supreme Court appeal.
   - **Use:** Confirmed that the permanent-injunction remand proceedings in the district court are currently paused awaiting the Supreme Court's disposition of this appeal.

8. **`mcp_courtlistener_read_document` (`recap_document_id=480335147`, `chunk_index=10`, then `chunk_index=[14, 15, 16]`)**
   - **Result:** Read pages 74–80 of Doc. 537 (the May 26, 2026 Preliminary Injunction Order, the last two pages of which were omitted from `record/documents/petition.txt` due to the 150,000-character cap).
   - **Use:** Confirmed the exact operative text of the preliminary injunction on page 77 of Doc. 537: it preliminarily enjoined the Secretary of State only *"from conducting the 2026 congressional elections according to the 2023 Plan"* and ordered administration of *"all remaining events comprising Alabama's 2026 congressional elections according to the Special Master Plan,"* while setting a January 11, 2027 trial-readiness date for the permanent-injunction remand.

9. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="25-274"` and `"25-275"`) and (`q='"judgment is vacated" AND "moot"'` and `q='"jurisdictional statement" AND ("vacated" OR "dismissed" OR "reversed")'`)**
   - **Result:** Checked CourtListener opinion index for additional three-judge district court and *Munsingwear* opinions.
