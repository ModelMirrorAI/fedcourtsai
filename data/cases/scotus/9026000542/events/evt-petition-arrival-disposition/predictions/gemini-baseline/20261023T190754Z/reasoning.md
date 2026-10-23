# Predictor Rationale (`reasoning.md`) — *Timothy Hall v. Eastern Panhandle Anesthesia Associates, et al.* (No. 26-542)

## 1. Headline Probability and Disposition
- **Predicted Disposition:** `denied` (`granted: 0`)
- **`probability` (`P(granted)`):** `0.003` (0.3%)
- **`confidence`:** `0.95`

## 2. Base-Rate Anchoring (`metrics/statpack.md` & `record/context.json`)
Per `record/context.json`, this cell is at `moment: arrival` (`evt-petition-arrival-disposition`) in `mode: "forward"` for October Term 2026 (`term: 2026`), with frozen salience conditioning:
- `band`: `"baseline"` under `salience_version: "sal-v4"` (private petitioner on the paid docket, `distribution_count: 0`, `cvsg_date: null`).
- `input_snapshot`: `"2026-10-24.json"`.

Following the `moment: arrival` anchoring rule, I anchor on the `baseline` caption-class floor's **bracketed `reached` (risk-set) grant rate** in the `sal-v4` segment table of `metrics/statpack.md`, pooled strictly across the nine completed Terms preceding OT2026 (OT2017–OT2025):
- **2025:** reached 3.9% (`n = 1,303`, weighted grants = 51)
- **2024:** reached 5.7% (`n = 1,271`, weighted grants = 72)
- **2023:** reached 5.9% (`n = 1,312`, weighted grants = 77)
- **2022:** reached 5.8% (`n = 1,192`, weighted grants = 69)
- **2021:** reached 5.6% (`n = 1,500`, weighted grants = 84)
- **2020:** reached 4.5% (`n = 1,739`, weighted grants = 78)
- **2019:** reached 4.6% (`n = 1,399`, weighted grants = 64)
- **2018:** reached 4.6% (`n = 1,524`, weighted grants = 70)
- **2017:** reached 4.7% (`n = 1,643`, weighted grants = 77)
- **Pooled prior-Term `baseline` (`sal-v4` reached) anchor:** `642 / 12,883 = 4.983%` (~5.0%).

Cross-checking the other relevant cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall (denial-reweighted, `n = 39,147` resolved):** `granted` 1.5% (589), `gvr` 1.0% (386), `denied` 95.3% (37,298), `dismissed` 2.2% (874) — combined grant-family rate ~2.5%.
- **Originating circuit (`ca4`, Fourth Circuit, denial-reweighted, `n = 3,447` resolved):** `granted` 1.3% (46), `gvr` 1.2% (42), `denied` 95.2% (3,283), `dismissed` 2.2% (76) — combined grant-family rate ~2.55%, roughly half the D.C. Circuit rate and below the overall paid arrival average.

## 3. Case-Specific Adjustments from the Anchor
Starting from the ~4.98% `baseline` arrival risk-set anchor for private paid petitions, several strong, cumulative negative signals in the provisioned snapshot and lower-court record drive the probability of certiorari down by more than an order of magnitude to `0.003` (0.3%):

1. **Self-Represented (Pro Se) Petitioner on the Paid Docket (`2026-10-24.json`):**
   Although docketed on the paid appellate docket (`26-542`, `sJsonCaseType: "Paid"`), the snapshot's party/counsel block identifies petitioner Timothy Hall as representing himself (`"Attorney": "Timothy Hall"`, `"PartyName": "Timothy Hall"`, `"IsCounselofRecord": false`, with `[contact detail withheld]`). Within the `baseline` paid risk set, the ~5.0% grant rate is overwhelmingly concentrated in petitions filed by experienced appellate and Supreme Court counsel; paid pro se petitions almost never ascend the escalation ladder (response requests, relists, CVSG) or receive plenary or summary review.
2. **Unpublished Per Curiam Fourth Circuit Disposition on an Informal Briefing Calendar (`ca4` No. 25-2149):**
   The snapshot identifies the decision below as a June 23, 2026 ruling of the Fourth Circuit in No. 25-2149 (rehearing denied July 21, 2026). CourtListener RECAP docket `71455680` (`Timothy Hall v. Eastern Panhandle Anesthesia Associates`, No. 25-2149) shows that the appeal proceeded under the Fourth Circuit's pro se informal briefing order (Docket Entry 2, Sept. 25, 2025) and was resolved by an **unpublished per curiam opinion** and judgment on June 23, 2026 (Docket Entries 36–37), with rehearing denied July 21, 2026 (Docket Entry 40). Unpublished summary dispositions from the informal briefing calendar create no binding circuit precedent and rarely implicate a genuine circuit split.
3. **Fact-Bound Threshold Dismissals and Interlocutory Arbitration Stay Below (`wvnd` No. 3:24-cv-00061-GMG-RWT):**
   CourtListener RECAP docket `68547595` (N.D. W. Va. No. 3:24-cv-00061) contains the complaint (`recap_document_id=399647335`, ECF No. 1) and Chief District Judge Gina M. Groh's 17-page Memorandum Opinion and Order entered August 27, 2025 (`recap_document_id=450473624`, ECF No. 72), which was the subject of the Fourth Circuit appeal:
   - Petitioner, an anesthesiologist provider employed by Eastern Panhandle Anesthesia Associates (EPAA) from July 2017 until his termination on February 10, 2020, waited until May 20, 2024—more than four years after his termination and over three-and-a-half years after his September 11, 2020 EEOC right-to-sue notice—to file suit against nine defendants (EPAA, WVU-BMC, Air Methods, HealthNet Aeromedical Services, Berkeley County Board of Education, West Virginia Department of Education, Nationwide Mutual Insurance Company, Berkeley County Commission, and Berkeley County Assessor) alleging ADA, Rehabilitation Act, West Virginia Human Rights Act, and West Virginia Patient Safety Act claims.
   - Judge Groh dismissed seven sets of defendants with prejudice (or without prejudice under Rule 12(b)(5) as to the unserved county defendants) on clear threshold grounds: the 90-day federal statutory filing window and two-year statutes of limitations barred the claims against the hospital and aeromedical defendants; Eleventh Amendment immunity and lack of standing barred the state education claims; and none of the non-EPAA defendants had an employment relationship with petitioner.
   - Crucially, as to petitioner's actual former employer (EPAA), Judge Groh granted EPAA's motion to compel arbitration under the 2017 employment agreement and **stayed the civil action as to EPAA only** pending arbitration pursuant to `9 U.S.C. § 3` (ECF No. 72 at 15–17).
   - Because the action remained stayed as to EPAA without a final judgment disposing of all claims and parties under 28 U.S.C. § 1291 (and without a Rule 54(b) certification at the time of the appeal, alongside `9 U.S.C. § 16(b)`'s bar on interlocutory appeals from orders staying proceedings and compelling arbitration), the appeal to the Fourth Circuit suffered from a textbook finality/jurisdictional defect. Indeed, subsequent N.D. W. Va. docket entries following the Fourth Circuit's July 29, 2026 mandate (ECF No. 88) show post-mandate motions in the district court in October 2026 for "Judgment under Rule 54(b)" (ECF No. 89, Oct. 13, 2026) and "Dismiss/Lack of Prosecution" (ECF No. 90, Oct. 14, 2026; Roseboro Notice ECF No. 91, Oct. 16, 2026).

Taken together, this petition is an archetypal low-probability pro se filing with fatal threshold and vehicle obstacles. A grant probability of `0.003` (0.3%) reflects the residual tail possibility of an unexpected GVR.

## 4. Rationale for Declared Claims (`cert-v2`) and `big_case_score`
- **`disposition` (`0.003`):** Matches top-level `probability` exactly (`P(any grant) = 0.003`).
- **`relist-increment` (`0.98`):** Under `fedcourtsai.pipeline.claims._resolve_relist_increment`, the claim resolves to `int(outcome.signals.distribution_count > context.distribution_count)`. Because this is an `arrival` cell where `context.distribution_count` is `0`, `outcome.signals.distribution_count > 0` asks whether the petition will be distributed at least once for a conference (as opposed to being dismissed under Rule 46 before ever being distributed). In the OT2025 paid cert cohort (`metrics/statpack.json`), ~99% of resolved paid petitions reach at least one conference distribution (`dismissed` accounts for ~1.0% of paid resolutions, and some dismissals occur after distribution). Allowing a ~2% chance of pre-distribution dismissal or withdrawal given ongoing October 2026 district court motions, `P(distribution_count > 0) = 0.98`. (By contrast, the probability of a *second* distribution—an actual relist to `distribution_count >= 2`—is ~0.02.)
- **`cvsg-increment` (`0.001`):** Across the paid scored segment in `metrics/statpack.md`, only 90 of 12,135 weighted petitions (~0.74%) draw a CVSG, and almost none are pro se unpublished employment/arbitration appeals.
- **`summary-disposition-route` (`0.65`):** Conditional on the remote event of a grant, a summary order (GVR) is substantially likelier (`0.65`) than plenary briefing and oral argument (`0.35`), both because GVRs represent ~40% of all modern cert grants in `metrics/statpack.md` (`386 / (589 + 386) = 39.6%`) and because the Court virtually never sets a pro se civil petition from an unpublished interlocutory disposition for plenary argument without counsel appointment or a clean vehicle.
- **`dissent-from-denial` (`0.002`):** Conditional on denial, a noted dissent or statement respecting denial is exceedingly rare in fact-bound pro se civil petitions with severe procedural barriers.
- **`big_case_score` (`0.03`):** Decoupled from grant likelihood, the underlying dispute—an individual employment-termination and arbitration enforcement dispute with four-year-old claims dismissed on routine timeliness and non-employer grounds—has negligible national legal, policy, or public significance even if decided.

## 5. Provisioned Inputs & Uncertainty Notes
- **Provisioned inputs read:** `record/snapshots/2026-10-24.json` and `record/context.json`. No `record/documents/` directory was provisioned for this arrival cell, so the petition text and questions presented were not on disk; I relied on the snapshot metadata and retrieved the underlying Fourth Circuit and Northern District of West Virginia records via CourtListener MCP.
- **Main uncertainty:** For the `relist-increment` claim (`0.98`), the sole material uncertainty is whether petitioner voluntarily withdraws or fails to perfect the docket before initial conference distribution in light of the October 2026 post-mandate motions in the district court (`3:24-cv-00061` ECF Nos. 89–91).
