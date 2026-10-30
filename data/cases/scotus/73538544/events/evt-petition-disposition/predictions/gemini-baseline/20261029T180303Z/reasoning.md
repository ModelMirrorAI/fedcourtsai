# Prediction Rationale (`reasoning.md`): *Christina Casarez v. Irigoyen Farms, Inc., et al.* (No. 25-1421)

## 1. Case Overview and Provisioned Record

- **Case ID / Docket:** `scotus/73538544` (No. 25-1421), *Christina Casarez v. Irigoyen Farms, Inc., et al.*
- **Event / Stage / Moment:** `evt-petition-disposition` (`stage: cert`, `moment: distribution`, `mode: forward`, `cutoff: null`).
- **Provisioned Inputs Read:**
  - Snapshot: `data/cases/scotus/73538544/record/snapshots/2026-10-29.json` (`input_snapshot: "2026-10-29.json"`).
  - Context: `data/cases/scotus/73538544/record/context.json` (`band: "elevated"`, `salience_version: "sal-v4"`, `distribution_count: 2`, `cvsg_date: null`, `term: 2025`, `paper_only_filings: false`).
  - Provisioned Documents (`data/cases/scotus/73538544/record/documents/`):
    - `questions-presented.txt` (1,478 bytes): The three questions presented from the petition.
    - `petition.txt` (72,911 bytes, 36 pages): Petition for a writ of certiorari filed June 26, 2026, including the appendix reproducing the unpublished October 7, 2025 opinion of the Court of Appeal of California, Fifth Appellate District (No. F086901, Pet. App. 1a–14a) and the January 14, 2026 order of the Supreme Court of California denying review (No. S293879, Pet. App. 15a).
    - `brief-in-opposition.txt` (66,322 bytes, 52 pages combined): Concatenates **both** respondents' briefs—(1) Respondent Irigoyen Farms, Inc.'s August 26, 2026 Brief in Support in Part (supporting certiorari on Question 2) and in Opposition in Part (opposing GVR and summary reversal on Questions 1 and 3), and (2) Respondent Walmart Inc.'s October 13, 2026 Brief for Respondent filed in response to the Court's September 10, 2026 Call for Response, in which Walmart (represented by Roman Martinez of Latham & Watkins LLP) **explicitly agrees that the Court should grant, vacate, and remand (GVR) in light of *Montgomery v. Caribe Transport II, LLC*, 608 U.S. 219 (2026)**.
    - `cert-reply.txt` (18,567 bytes, 12 pages): Petitioner's August 31, 2026 reply brief to Irigoyen Farms' response. Note: The docket snapshot also records a second reply brief filed by Petitioner on October 20, 2026 (`Reply_to_Wmt_Br_in_Opp.pdf`), which was not included in `cert-reply.txt` (noted in `flags.json` under `provisioning`), as well as Irigoyen Farms' October 23, 2026 motion for leave to file a sur-reply brief, which the Clerk noted as "not accepted for filing" on October 28, 2026.

## 2. Base-Rate Anchoring from `metrics/statpack.md`

- **Salience Band Anchor (`sal-v4`, `band: "elevated"`, `term: 2025`):**
  - Following the prompt contract, we anchor on the `elevated` band's **bracketed `reached`** rate in the "Segment base rate by salience band (sal-v4)" table pooled strictly over Terms preceding `term: 2025` (i.e., OT2017 through OT2024):
    - OT2024: 18.3% (`n=338`, ~62 grants)
    - OT2023: 17.5% (`n=354`, ~62 grants)
    - OT2022: 19.2% (`n=302`, ~58 grants)
    - OT2021: 20.8% (`n=342`, ~71 grants)
    - OT2020: 16.4% (`n=397`, ~65 grants)
    - OT2019: 13.8% (`n=334`, ~46 grants)
    - OT2018: 16.1% (`n=348`, ~56 grants)
    - OT2017: 18.1% (`n=404`, ~73 grants)
  - Pooling across OT2017–OT2024 gives **493 grants out of 2,819 reached petitions = 17.5%** (`n=2819`). (For comparison, the leading ended-in-band `elevated` figure across OT2017–OT2024 is 216 / 2,032 = 10.6%.)
- **Signal Cuts (Paid Scored Segment in `metrics/statpack.md`):**
  - **Relist count (`1` relist, corresponding to `distribution_count: 2`):** Over `n=2538` resolved petitions (`2568` total), base rate is `denied 85.3%, granted 8.5%, gvr 5.2%, dismissed 1.0%` (grant family `granted + gvr = 13.7%`). For `2` relists (`n=495` resolved), `denied 57.4%, granted 28.3%, gvr 12.9%, dismissed 1.4%` (grant family `41.2%`); for `3+` relists (`n=484` resolved), `denied 61.6%, granted 23.1%, gvr 14.3%, dismissed 1.0%` (grant family `37.4%`).
  - **CVSG status (`none`):** Over `n=13556` resolved petitions (`13976` total), base rate is `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (grant family `6.4%`).
  - **Amicus-brief count (`0`):** Over `n=11109` resolved petitions (`11406` total), base rate is `denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.2%` (grant family `3.8%`).
  - **Originating court:** State intermediate appellate court (`Court of Appeal of California, Fifth Appellate District`; in the statpack's `(none)` circuit bucket `n=11615` resolved, `denied 96.4%, dismissed 2.2%, gvr 0.7%, granted 0.6%`, and comparable to `Court of Appeal of California, Second Appellate District`, `n=189` resolved, `denied 89.4%, dismissed 6.3%, gvr 3.7%, granted 0.5%`).

## 3. Case-Specific Adjustments Driving `probability = 0.92` (`predicted_disposition = "gvr"`)

Starting from the `elevated` band reached base rate of **17.5%** (`n=2819`), four case-specific features in the provisioned record move the grant probability upward to **0.92** (`granted: 1`, `predicted_disposition: "gvr"`):

1. **The Decision Below Explicitly Relied on the Exact Seventh Circuit Precedents (*Ye* and *Montgomery*) That This Court Unanimously Reversed/Abrogated in *Montgomery v. Caribe Transport II, LLC*, 608 U.S. 219 (May 14, 2026):**
   - In its October 7, 2025 opinion, the California Court of Appeal held that the FAAAA's safety exception, 49 U.S.C. § 14501(c)(2)(A), did not save Petitioner's common-law negligence claims against either Walmart or Irigoyen Farms because neither respondent directly owned or operated a motor vehicle (Pet. App. 10a–14a). In reaching that holding, the Court of Appeal explicitly adopted *Ye v. GlobalTranz Enterprises, Inc.*, 74 F.4th 453 (7th Cir. 2023) ("Casarez's assertions to the contrary cannot survive the reasoning of *Ye*, which we find persuasive," Pet. App. 12a), and cited the Seventh Circuit's decision in *Montgomery v. Caribe Transport II, LLC*, 124 F.4th 1053 (7th Cir. 2025) (Pet. App. 13a).
   - After the California Supreme Court denied review on January 14, 2026, this Court on May 14, 2026 unanimously (9–0) reversed the Seventh Circuit in *Montgomery*, 608 U.S. 219, and expressly abrogated *Ye*, holding that § 14501(c)(2)(A) does not require a "direct link" or direct ownership or operation of a motor vehicle.
2. **The September 10, 2026 Call for Response (CFR) Following Walmart's Waiver:**
   - Respondent Irigoyen Farms filed a substantive response on August 26, 2026, while Respondent Walmart filed a waiver on August 27, 2026. The petition was distributed on September 9, 2026, and the very next day (September 10, 2026) the Court requested a response. Under standard Supreme Court practice, the Court calls for a response from a waiving respondent before entering a GVR order vacating a judgment in that respondent's favor.
3. **Respondent Walmart's Express Concession in Its October 13, 2026 Brief That the Court Should GVR:**
   - Retaining Roman Martinez of Latham & Watkins LLP after the CFR, Walmart filed a brief on October 13, 2026, that unequivocally supports a GVR:
     > "Walmart agrees that this case meets this Court's established criteria for a GVR order."
     > "CONCLUSION: This Court should grant, vacate, and remand in light of its decision in *Montgomery*."
   - Walmart further explains why a GVR is proper as to the entire judgment below: Petitioner's summary-judgment opposition and appellate briefing against Walmart asserted a negligent-selection theory ("virtually identical to the claim in *Montgomery*"), and the California Court of Appeal entered a single judgment affirming summary judgment for both Walmart and Irigoyen based on a unified safety-exception analysis grounded in *Ye* and *Montgomery* (7th Cir.).
4. **Why `gvr` (~0.90) Dominates `granted` (~0.01), `summary-reversal` (~0.01), and `denied` (~0.08):**
   - **Plenary review (`granted`, ~0.01)** is unwarranted because the decision below is unpublished, there is no genuine circuit conflict on Question 2 (whether § 14501(c)(1) applies to shippers) that requires resolution before the state court reconsiders the § 14501(c)(2)(A) safety exception under *Montgomery*, and Walmart opposes plenary review.
   - **Summary reversal (`summary-reversal`, ~0.01)** is inappropriate because the California courts ruled before *Montgomery* was decided and left unresolved alternative state-law preservation and pleading defenses (such as Walmart's argument that Petitioner failed to plead negligent selection in her operative complaint).
   - **Denial (`denied`, ~0.08)** represents the small residual risk that the Court concludes on closer inspection that state-law pleading forfeiture as to Walmart and factual distinctions between negligent cargo loading by a shipper (Irigoyen) and negligent carrier selection by a broker (*Montgomery*) make remand futile. Given the Court of Appeal's explicit reliance on *Ye*'s categorical "ownership or operation" rule for both defendants and Walmart's express acquiescence in a GVR, that residual denial risk is roughly 8%.

## 4. Secondary Claims, Distributions, and Big-Case Score

- **`relist-increment` (0.18):** Because `distribution_count` is currently `2` only because the first distribution (Sep. 9) was interrupted by the Sep. 10 CFR, the upcoming November 13, 2026 conference is the first conference with full briefing. Most post-CFR GVRs where the respondent concedes the GVR issue directly from that conference without an additional relist, leaving an ~18% probability of at least one further distribution (e.g., a one-conference check/clean-up relist).
- **`cvsg-increment` (0.01):** Near zero; *Montgomery* was just decided and a routine GVR requires no SG input.
- **`summary-disposition-route` (0.99):** Conditional on a grant (`0.92`), the probability that the grant is a summary disposition in the cert order itself (`gvr` or `summary-reversal`, ~0.91 total) rather than plenary review (~0.01) is `0.91 / 0.92 ≈ 0.99`.
- **`dissent-from-denial` (0.02) and `order-writers` (0.001–0.005 per Justice):** Separate writings on routine GVR orders (or denials of fact-bound state FAAAA cases) are exceedingly rare.
- **`big_case_score` (0.15):** Assessed on significance *if decided* (independent of grant likelihood), this is a follow-on FAAAA preemption dispute from an unpublished California intermediate appellate decision; even if the Court reached Question 2 on shipper preemption, its legal and public salience is modest (`0.15`).

## 5. Note on Upstream Retrieval and Provisioning

- Two calls to `mcp_courtlistener_search` returned HTTP 429 (`Rate limit exceeded: 1400/day`). Following the prompt instructions, we degraded gracefully to `uv run fedcourts query` and the provisioned filings in `record/documents/`, which already contained the full text of the California Court of Appeal opinion and the parties' thorough discussion of *Montgomery v. Caribe Transport II, LLC*, 608 U.S. 219 (2026).
- As noted in `flags.json`, `cert-reply.txt` contains Petitioner's August 31, 2026 reply brief (to Irigoyen Farms) and omits Petitioner's October 20, 2026 reply brief (to Walmart); however, because Petitioner asked for a GVR in Question 1 and Walmart agreed to a GVR in its October 13 brief, Petitioner's October 20 reply could only reinforce that shared agreement on GVR.
