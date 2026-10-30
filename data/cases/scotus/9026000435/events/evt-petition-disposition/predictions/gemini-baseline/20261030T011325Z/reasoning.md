# Certiorari Prediction: *Nexstar Media Inc., Authorized to Operate Television Station WROC-TV v. National Labor Relations Board* (No. 26-435)

## 1. Procedural Posture and Baseline Anchor

Petitioner Nexstar Media Inc. (operating television station WROC-TV in Rochester, New York) seeks a writ of certiorari to review a June 30, 2026 unpublished Summary Order of the United States Court of Appeals for the Second Circuit (No. 24-2472 (L), 24-2683 (XAP)), which denied Nexstar's petition for review and granted the National Labor Relations Board's cross-application for enforcement of an unfair labor practice order (*Nexstar Media, Inc.*, 373 NLRB No. 92 (Aug. 29, 2024)).

From `record/context.json` and the provisioned snapshot (`2026-10-30.json`):
- **Stage / Moment:** `cert` / `distribution` (`evt-petition-disposition`).
- **Salience Band & Signals:** `band = "baseline"` (`sal-v4`), `distribution_count = 1`, `cvsg_date = null`, `response_requested = null`.
- **Docket Trajectory:** The petition was filed on September 28, 2026, and docketed on October 1, 2026. On October 8, 2026, the Solicitor General (on behalf of Respondent NLRB) filed a waiver of the right to respond. No amicus briefs have been filed. On October 28, 2026, the petition was distributed for its first conference (November 13, 2026), with no call for a response (CFR) having issued prior to distribution.

### Base-Rate Calculation (`metrics/statpack.md`)
Under `sal-v4`, the strictly-prior-Term `baseline` band **risk-set** (`prefix_est_grant_rate`, `prefix_weighted_resolved`) pooled across OT2017–OT2025 (weighted grants / weighted resolved) is:
- OT2017: $0.025 	imes 1338 = 33.45$
- OT2018: $0.030 	imes 1338 = 40.14$
- OT2019: $0.027 	imes 1291 = 34.86$
- OT2020: $0.032 	imes 1221 = 39.07$
- OT2021: $0.033 	imes 1236 = 40.79$
- OT2022: $0.027 	imes 1130 = 30.51$
- OT2023: $0.031 	imes 1143 = 35.43$
- OT2024: $0.030 	imes 1179 = 35.37$
- OT2025: $0.038 	imes 928 = 35.26$
- **Pooled Risk-Set Rate:** $324.88 / 10,804 \approx \mathbf{3.01\%}$ (`0.0301`).
- **Pooled Terminal Rate (`baseline`):** $78.18 / 8,850 \approx \mathbf{0.88\%}$ (`0.0088`).

Because the Government waived its response and the petition went straight to distribution without a CFR or amicus briefs, the case sits at the bottom of the `baseline` risk set. Absent a late CFR before or at conference, the Court essentially never grants plenary review without calling for a response, and even a GVR without a response is exceedingly rare unless the case is being held for or disposed of under a directly controlling Supreme Court decision. Adjusting downward from the 3.01% `baseline` risk-set prior for the government waiver, absence of amici, unpublished summary order below, and fact-bound record yields a grant-family probability of **0.8% (`0.008`)** and a predicted disposition of **`denied`**.

---

## 2. Case Background and Legal Analysis

### A. Underlying Agency and Second Circuit Proceedings
In October 2023, NABET-CWA petitioned the NLRB to represent a bargaining unit of 24 employees at WROC-TV, including 12 producers (news producers, digital content producers, and creative services producers). Nexstar argued that the producers were statutory "supervisors" excluded from coverage under Section 2(11) of the NLRA, 29 U.S.C. § 152(11), contending they had authority to "assign" and "responsibly to direct" reporters, photographers, and meteorologists using "independent judgment."

Following an evidentiary hearing, the NLRB Regional Director issued a Dec. 1, 2023 Decision and Direction of Election applying the Board's longstanding synthesis in *Oakwood Healthcare, Inc.*, 348 NLRB 686 (2006) (adopted after *NLRB v. Kentucky River Community Care, Inc.*, 532 U.S. 706 (2001)). The Regional Director found that Nexstar failed to meet its burden of proving supervisory status because:
1. Producers follow a standard daily format ("the wheel") and editorial parameters set by the News Director and Executive Producer; they cannot mandate scripts, require overtime, discipline employees, or override managers.
2. Putting together rundown rundowns and requesting edits is routine collaborative work among skilled newsroom professionals rather than statutory "assignment" or "responsible direction" (where the putative supervisor is held accountable for others' performance).
3. The Regional Director noted a long, unbroken line of post-*Oakwood* decisions rejecting identical supervisory claims by Nexstar and other broadcasters for television news producers.

After the Union won the election (17–1), Nexstar engaged in a technical refusal to bargain to test the certification. On August 29, 2024, the Board (*Nexstar Media, Inc.*, 373 NLRB No. 92) granted summary judgment against Nexstar under Section 8(a)(5) and (1).

On June 30, 2026, a unanimous Second Circuit panel (Pooler, Chin, and Robinson, JJ.) issued a non-precedential Summary Order denying Nexstar's petition for review and enforcing the Board's order. In its standard-of-review boilerplate, the panel quoted *NLRB v. Special Touch Home Care Services, Inc.*, 708 F.3d 447, 453 (2d Cir. 2013), stating that review of Board decisions is "quite limited" and that review of legal conclusions is "deferential" so long as they have a "reasonable basis in law," while adding in a footnote that it "need not consider whether the Board's legal conclusions are entitled to *Chevron* deference" (*Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024)) because Second Circuit deference to the NLRB relied on *Universal Camera Corp. v. NLRB*, 340 U.S. 474 (1951), and *Ford Motor Co. v. NLRB*, 441 U.S. 488 (1979). On the merits, the panel walked through the evidentiary record under 29 U.S.C. § 160(e) and concluded that substantial evidence supported the Regional Director's findings that WROC-TV's producers lacked authority to assign or responsibly direct other employees using independent judgment.

### B. Assessment of Questions Presented and Certiorari Criteria

**1. Question 2 — Deference to the NLRB after *Loper Bright*:**
Nexstar's primary hook is the Second Circuit's footnote declining to apply *Loper Bright* to the NLRB's legal conclusions. While whether *Ford Motor Co.* deference to the NLRB survives *Loper Bright* is a question of general interest to the administrative-law bar (and several circuits, such as the Fifth, Sixth, and Third Circuits, have explicitly applied *Loper Bright* to review NLRB statutory interpretations *de novo*), this case is an exceptionally poor vehicle to address it—and does not even warrant a GVR—for three reasons:
- **No Intra- or Inter-Circuit Split on Pure Questions of Law:** Just two months after the unpublished summary order in *Nexstar*, the Second Circuit issued a published opinion in *Siren Retail Corp. v. NLRB*, No. 24-3168 (2d Cir. Sept. 2, 2026), expressly quoting the APA, 5 U.S.C. § 706 ("the reviewing court shall decide all relevant questions of law"), and reviewing the validity of the Board's legal standard without deference before reviewing its application for substantial evidence. Thus, the Second Circuit's binding law already aligns with *Loper Bright* on pure questions of law; the stray footnote in *Nexstar* appears in a non-precedential summary order.
- **No Legal Interpretation Is Disputed:** Nexstar does not actually challenge the validity of the Board's legal definitions of "assign," "responsibly to direct," or "independent judgment" articulated in *Oakwood Healthcare, Inc.*, 348 NLRB 686 (2006). On the contrary, Nexstar relies on *Oakwood Healthcare* and argues that the Regional Director misapplied those definitions to the facts of WROC-TV's newsroom.
- **Mixed Fact-Bound Application:** Under 29 U.S.C. § 160(e), the Board's findings of fact—including whether particular employees possess supervisory authority in a given workplace—are conclusive "if supported by substantial evidence on the record considered as a whole." As the D.C. Circuit observed in *Hospital Menonita de Guayama, Inc. v. NLRB*, 94 F.4th 1, 5 (D.C. Cir. 2024), because supervisory status under Section 2(11) is a question of "degrees and shades of meaning" turning on workplace specifics, appellate review of the Board's application of Section 2(11) to a specific job classification is classic substantial-evidence review. Even under *Loper Bright*, statutory delegations of fact-intensive application and § 160(e) substantial-evidence review remain intact.

**2. Question 1 — Alleged Split with the Eighth Circuit (*Multimedia KSDK*):**
Nexstar claims a circuit split with *Multimedia KSDK, Inc. v. NLRB*, 303 F.3d 896 (8th Cir. 2002) (en banc), where the Eighth Circuit held that television producers at a St. Louis station exercised independent judgment in assigning work. This argument fails every Rule 10 criterion:
- *Multimedia KSDK* was decided in 2002, four years *before* the Board overhauled its Section 2(11) definitions in *Oakwood Healthcare* (2006) in response to *Kentucky River* (2001).
- As both the Regional Director and the Second Circuit explained, supervisory determinations are inherently fact-specific; a 24-year-old decision resting on a different evidentiary record under a superseded Board framework does not create a doctrinal circuit conflict.

---

## 3. Outcome Decomposition & Auxiliary Forecasts

### A. Big-Case Score (`big_case_score = 0.14`)
The dispute concerns a single 24-person bargaining unit at a local Rochester television station and a non-precedential summary order. While the petition invokes *Loper Bright* in the NLRA context, the underlying dispute is a routine substantial-evidence challenge to a bargaining-unit certification. If decided on the merits, a ruling clarifying that *Loper Bright* abrogates *Ford Motor* deference to NLRB statutory interpretations would have moderate administrative-law salience, but because the case is a non-precedential, fact-bound vehicle with no amicus participation, its overall stakes score is low (**0.14**).

### B. Mechanical Claims (`cert-v3`)
1. **`disposition` (`0.008`):** Matches the headline grant-family probability. If the Court acts favorably at all, a GVR (`0.0045` unconditional) or summary reversal (`0.0005`) to clean up the Second Circuit's footnote in light of *Loper Bright* is slightly less unlikely than a plenary grant (`0.003`), so `summary-disposition-route` conditional on a grant is elevated alongside a tiny overall grant probability.
2. **`relist-increment` (`0.03`):** Because Respondent waived its response and no CFR has been issued prior to distribution (`distribution_count = 1`), the overwhelming majority of waived-response petitions are denied on their first conference list. There is a ~3% chance that a Justice's chambers flags the *Loper Bright* footnote, triggering a late CFR or a relist.
3. **`cvsg-increment` (`0.001`):** Respondent is the National Labor Relations Board, represented by the Solicitor General. Because a federal agency is already a named party, the Court does not issue a CVSG (and the claim is structurally vacuous / masked at evaluation under `federal_party`). We state `0.001` to reflect the near-zero structural probability.
4. **`summary-disposition-route` (`0.36`):** Conditional on the petition landing in the grant family (`granted` or `gvr`), the historical paid-petition cert-order disposition share in `statpack.json` across OT2017–OT2025 is approximately 31.8% (`summary_route_base_rate`). Here, because the only plausible reason for the Court to touch this non-precedential summary order would be to vacate the panel's footnote stating that *Ford Motor* insulates the NLRB from *Loper Bright*, the conditional probability of a cert-order disposition (GVR or summary disposition) given a grant is slightly above the historical base rate (**0.36**).
5. **`dissent-from-denial` (`0.015`):** Conditional on denial, there is a small (~1.5%) chance that one or more Justices (most plausibly Justice Gorsuch or Justice Thomas, who have scrutinized lower-court resistance to *Loper Bright* and agency deference) note a dissent from or statement respecting the denial of certiorari.

### C. Distribution Claims (`order-writers`)
Conditional on the order disposing of the petition, per-Justice writing probabilities are very low (~0.1% to 0.8%), with slightly higher weight on Justices Gorsuch (`0.008`), Thomas (`0.005`), and Alito (`0.004`), who are the most frequent authors of dissents from denial in administrative-deference and *Loper Bright* follow-on petitions.

### D. Semantic Claim (`primary-ground`)
If the Court were to grant plenary review or GVR, the dispositive ground would be that under *Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024), and Section 706 of the Administrative Procedure Act, 5 U.S.C. § 706, courts reviewing NLRB orders under 29 U.S.C. § 160(e)–(f) must exercise independent judgment on questions of statutory interpretation under the NLRA (including the meaning of "supervisor" in 29 U.S.C. § 152(11)) rather than affording *Chevron*-like deference to the Board's legal conclusions.
