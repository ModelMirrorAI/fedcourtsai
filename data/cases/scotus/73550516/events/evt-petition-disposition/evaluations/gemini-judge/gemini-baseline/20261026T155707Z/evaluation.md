# Evaluation of `gemini-baseline` — `scotus/73550516` (`evt-petition-disposition`)

## Stage and Outcome Summary

- **Stage:** `cert` (`moment: distribution`)
- **Realized outcome:** `actual_disposition = "dismissed"`, `actual_granted = 0` (joint stipulation to dismiss under Rule 46 filed October 19, 2026; dismissed October 20, 2026). The docket recorded no further distributions beyond the initial August 12, 2026 distribution (`signals.distribution_count = 1`), no CVSG (`signals.cvsg_date = null`), and no separate writings (`noted_dissent_from_denial = null`).
- **Prediction summary:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.18`.
- **Headline scores:**
  - `correct = 0`: On a cert cell, `correct` is an exact label match of `predicted_disposition` (`"denied"`) against `actual_disposition` (`"dismissed"`). Because the petition was voluntarily dismissed under Rule 46 rather than denied at conference, the exact disposition label match is `0` even though `gemini-baseline` rightly predicted `granted = 0`.
  - `brier_score = 0.0324`: `(0.18 - 0)^2 = 0.0324`.
  - **Baseline and skill:** Because the scored prediction carries a frozen `context.band` (`baseline` under `sal-v4`), `segment_base_rate`, `brier_skill_score`, `base_rate_basis`, and `claim_scores` are left for `stamp-cell` to compute against the stamped segment base rate.

## What `gemini-baseline` Got Right and Wrong

- **What went right:**
  - **Basic hold-and-GVR framing and reasonable headline probability:** `gemini-baseline` recognized that the petitioner requested a hold pending the lead case (*Indian Harbor Insurance Co. v. Town of Vinton*), framed the grant probability here as roughly the probability of a grant in the lead case multiplied by the probability of reversal triggering a GVR, and landed on a reasonable headline probability (`0.18`) that achieved the lowest primary Brier score (`0.0324`) when the petition resolved without a grant.
- **What it missed:**
  - **Superficial reading of the provisioned record:** As `retrieval_log.json` shows, `gemini-baseline` read only the first 50 lines of `petition.txt` and ran two `grep` commands (`Outokumpu` and `circuit split`), never reading the body of the petition or any of Appendices A–D. As a result, its single-paragraph `reasoning.md` (~160 words) completely missed the threshold contract-construction issue on which the Fifth Circuit relied in *Town of Vinton* (the policy's Allocation Endorsement creating separate contracts with the domestic and foreign insurers), the interaction between the McCarran-Ferguson Act and La. R.S. § 22:868, and the Louisiana Supreme Court's ruling in *Police Jury of Calcasieu Parish*.
  - **Inaccurate docket citation in `reasoning.md`:** `gemini-baseline` cited the lead case in `reasoning.md` as `*Indian Harbor* (No. 25-1524)`. That docket number does not appear in the petition (which cites extension application `No. 25-A1099`) and is not the lead case's Supreme Court docket number (which is `No. 25-1383`, filed *before* this petition's `No. 25-1427`).
  - **Overconfidence on `relist-increment`:** `gemini-baseline` asserted in `reasoning.md` that the August 17 response request *"guarantees a re-distribution once the brief is filed"* and assigned `0.98` to `relist-increment`, overlooking the possibility of a pre-redistribution Rule 46 dismissal or withdrawal.

## Reasoning Quality (`0.42`)

Despite achieving a slightly lower headline Brier score (`0.0324`) than its peers due to its `0.18` grant probability, `gemini-baseline` receives `0.42` on `reasoning_quality`. The analysis is a terse, one-paragraph summary derived from `head` and `grep` snippets of the petition without engaging the appendices or the substantive counterarguments in the lower-court opinions, and it includes an unverified, inaccurate docket number (`No. 25-1524`) for the lead petition.

## Leakage Audit

- **Mode:** `forward` (run on 2026-10-06, two weeks prior to the 2026-10-20 resolution).
- **Findings:** Clean on outcome leakage (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). Audit of all 29 calls in `retrieval_log.json` shows no post-resolution material and no access to `data/qp-topics/`. However, `retrieval.md` is incomplete: call 16 in `retrieval_log.json` executed `uv run fedcourts query --court scotus --title "Indian Harbor" --decided-before "2026-10-06"`, which `gemini-baseline` omitted from `retrieval.md`.
