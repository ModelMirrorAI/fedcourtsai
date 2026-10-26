# Evaluation of `claude-baseline` — `scotus/73550516` (`evt-petition-disposition`)

## Stage and Outcome Summary

- **Stage:** `cert` (`moment: distribution`)
- **Realized outcome:** `actual_disposition = "dismissed"`, `actual_granted = 0` (joint stipulation to dismiss under Rule 46 filed October 19, 2026; dismissed October 20, 2026). The docket recorded no further distributions beyond the initial August 12, 2026 distribution (`signals.distribution_count = 1`), no CVSG (`signals.cvsg_date = null`), and no separate writings (`noted_dissent_from_denial = null`).
- **Prediction summary:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.20`.
- **Headline scores:**
  - `correct = 0`: On a cert cell, `correct` is an exact label match of `predicted_disposition` (`"denied"`) against `actual_disposition` (`"dismissed"`). While `claude-baseline` accurately predicted no grant (`granted = 0` vs. `actual_granted = 0`), the Rule 46 voluntary dismissal rather than a conference denial yields `correct = 0` on the disposition label.
  - `brier_score = 0.04`: `(0.20 - 0)^2 = 0.04`.
  - **Baseline and skill:** Because the scored prediction carries a frozen `context.band` (`baseline` under `sal-v4`), `segment_base_rate`, `brier_skill_score`, `base_rate_basis`, and `claim_scores` are left for `stamp-cell` to compute against the stamped segment base rate.

## What `claude-baseline` Got Right and Wrong

- **What went right:**
  - **Best-in-cell procedural and companion-docket investigation:** Beyond reading the entire provisioned petition and appendices, `claude-baseline` traced the extension application cited in the petition (`No. 25-A1099`) to the actual lead Supreme Court docket, *Indian Harbor Insurance Co. v. Town of Vinton*, No. 25-1383 (`scotus/73500284`), and verified its live procedural posture (Skadden counsel, amicus briefs from APCIA and arbitration scholars, response requested July 27, BIO filed August 26, reply filed September 9). It also checked subsequent Fifth Circuit treatment (*Transportation Consultants*, Sept. 3, 2026) via CourtListener.
  - **Explicitly anticipated the Rule 46 settlement/dismissal mechanism:** Remarkably, `claude-baseline` explicitly identified voluntary dismissal/settlement in both `reasoning.md` and `predicted_reasoning.md`. In `reasoning.md`, it shaded its derivative GVR probability downward to `0.20` specifically to account for *"the chance the lead case settles or is dismissed during the hold,"* and when discussing `relist-increment` it wrote that *"the residual is a dismissal or withdrawal before redistribution"* (and in `predicted_reasoning.md`: *"the only way it does not happen is a settlement-driven dismissal before redistribution"*). That exact residual event is what transpired when the parties filed a Rule 46 joint stipulation to dismiss on October 19, 2026 before any response brief or second distribution occurred.
  - **Rigorous doctrinal and quantitative decomposition:** `claude-baseline` cleanly decomposed the follower petition's grant-family probability as a function of the lead petition's grant probability and conditional reversal/GVR rate (`P(lead granted) × [P(consolidated) + P(held) × P(reversal/vacatur) × P(GVR)]`), while carefully weighing both the strength of the *GE Energy* open question and respondent's contract-construction argument that the separate-contract endorsement and *Bufkin* make the split non-dispositive.
- **What it missed:**
  - Although `claude-baseline` rightly identified pre-redistribution settlement/dismissal as the exact complement to `relist-increment`, it priced that residual at only 6% (`relist-increment = 0.94`), taking a high Brier penalty on that secondary claim when the case settled and was dismissed under Rule 46 prior to redistribution.

## Reasoning Quality (`0.92`)

`claude-baseline` earns `0.92` — the highest reasoning score in the cell. Its analysis combined deep mastery of the provisioned record, targeted verification of the lead *Indian Harbor* docket (`No. 25-1383`), nuanced treatment of the Fifth Circuit's contract-allocation holding versus the New York Convention equitable-estoppel question reserved in *GE Energy*, and an explicit, prescient identification of pre-redistribution settlement/dismissal as the key non-redistribution pathway.

## Leakage Audit

- **Mode:** `forward` (run on 2026-10-05/06, two weeks prior to the 2026-10-20 resolution).
- **Findings:** Clean (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). All 48 tool calls in `retrieval_log.json` were audited; all corpus, CourtListener, and `supremecourt.gov` lookups occurred while the petition was still open and unresolved, no `data/qp-topics/` paths were accessed, and `retrieval.md` faithfully reports every external call and `ranged corpus reads` line.
