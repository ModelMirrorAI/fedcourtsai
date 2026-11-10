# Evaluation of `codex-baseline` for `scotus/9026000107` (`evt-order-call-for-response-disposition`)

## 1. Outcome and Quantitative Summary

- **Case:** *Garnell Walls v. Prince George's County, Maryland, et al.*, No. 26-107 (`scotus/9026000107`)
- **Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`, `cutoff: 2026-09-03`)
- **Actual Outcome (`outcome.json`):** `actual_disposition: "denied"`, `actual_granted: 0`, `resolved_at: "2026-11-09"`, `noted_dissent_from_denial: false`, `signals.distribution_count: 2`, `signals.cvsg_date: null`.
- **Candidate Forecast (`prediction.json`):** `predicted_disposition: "denied"`, `granted: 0`, `probability: 0.24` (`disposition: 0.24`, `relist-increment: 0.99`, `cvsg-increment: 0.01`, `summary-disposition-route: 0.28`, `dissent-from-denial: 0.14`, `big_case_score: 0.52`).
- **Scored Metrics:**
  - `correct`: `1` (`"denied" == "denied"`)
  - `brier_score`: $(0.24 - 0)^2 = 0.0576$
  - `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for harness stamping against the stamped segment base rate.

While `codex-baseline` predicted the correct binary outcome (`denied`), its grant probability (`0.24`) was substantially over-optimistic compared to `gemini-baseline` (`0.06`) and `claude-baseline` (`0.13`), incurring the highest Brier (`0.0576`) penalty in the cell.

---

## 2. Reasoning Quality (`reasoning_quality = 0.72`)

### Strengths (`reasoning.md`)
1. **Accurate Statpack Grounding:** When checked against the historical statpack build in force when `codex-baseline` ran (`uv run fedcourts statpack-at` -> commit `7bcde3b105cb`), every figure `codex-baseline` quoted from `metrics/statpack.md` matched the `7bcde3b105cb` build exactly (including the `sal-v4` `baseline` and `elevated` `[reached]` rates across OT 2021–2025, the marginal `cert_amicus = 2+` rate of `18.4% granted + 4.5% gvr = 22.9%` over `n = 1,449`, and the `ca4` originating-court rate of `2.8% granted + 2.6% gvr = 5.4%` over `n = 1,662`).
2. **Doctrinal Framing:** `codex-baseline` clearly articulated both Questions Presented (*Pakdel*/*Williamson County* finality on QP 1 and *Lexmark*/*Susan B. Anthony List* prudential ripeness on QP 2), identified the preservation obstacle on QP 2 documented in Footnote 1 of the Fourth Circuit opinion (`App. 2a n.1`), and noted the contrast between Judge Boardman's reluctance to require legislative exhaustion (`App. 27a`) and the Fourth Circuit's reliance on the legislative Water & Sewer Plan amendment process (`App. 7a–10a`).

### Weaknesses (`reasoning.md`)
1. **Incomplete Reading of `appendix.txt` Missed the Fatal Vehicle Defect:** `retrieval_log.json` shows that `codex-baseline` read only the first 200 lines of `appendix.txt` plus a narrow grep (`Burford|futile|legislative`), skipping lines 550–850 (`App. 20a–27a`) of Judge Boardman's motions-hearing bench ruling. In that omitted portion of the transcript, petitioner's counsel *conceded* that the February 28, 2022 letter from DPIE Director Bolling was merely an informational response and *not* a final decision on a waiver application, and petitioner failed to retain a copy of any waiver application or plead that he had it notarized or paid the fee required by the 2018 Water & Sewer Plan. Because `codex-baseline` missed that concession, it mistakenly asserted that *"Question 1 [is] cleanly outcome-determinative of the Fourth Circuit's judgment."* In reality, as the County's Brief in Opposition (`brief-in-opposition.txt`, pp. 2–4, 9–11) later emphasized, the absence of any formal administrative waiver application or denial meant petitioner had not even satisfied ordinary administrative finality before DPIE.
2. **Over-Weighting the Marginal `2+` Amicus Cut:** By treating the marginal `cert_amicus = 2+` rate (`22.9%`) as an anchor that pulled this petition up to `0.24`—above even the `elevated` band's `[reached]` rate—`codex-baseline` under-discounted for the confounding in that marginal cut (which includes CVSGs, government petitioners, and clean circuit splits) and the severe vehicle defects of an unpublished, single-parcel local land-use affirmance.

---

## 3. Predicted Reasoning (`predicted_reasoning_quality = 0.76`)

`codex-baseline`'s `predicted_reasoning.md` is clear, coherent, and right on the outcome and procedural path, though slightly over-hedged toward a grant/summary reversal on QP 1:
1. **Denial of Certiorari (`borne-out`):** Correctly identified denial of certiorari as the primary expected disposition (~76%), while noting the unpublished posture, Judge Boardman's *Burford* abstention warning (`App. 14a–15a`), and the preservation issue on QP 2 (`App. 2a n.1`).
2. **Post-CFR Redistribution (`borne-out`):** Correctly forecast (`0.99`) that the petition would be redistributed after the County filed its Brief in Opposition (`signals.distribution_count: 2`).
3. **No CVSG (`borne-out`):** Correctly forecast (`0.01`) that the Court would not invite the Solicitor General (`signals.cvsg_date: null`).
4. **No Noted Dissent (`borne-out`):** Correctly forecast that denial without noted dissent was the modal outcome (`0.14` dissent probability; `noted_dissent_from_denial: false`).

Because the central procedural and disposition claims were borne out, while the document overestimated the cleanness of QP 1 as a vehicle for *Pakdel* review because it missed the administrative-waiver concession at `App. 20a–27a`, it earns `0.76` on the [0, 1] anchor scale.

---

## 4. Leakage Audit (`mode: "forward"`, `leakage_suspected: false`)

- `retrieval_log.json` records `mode: "forward"`, run on October 29, 2026 while the petition was unresolved.
- All 10 tool calls were local file reads (`2026-09-03.json`, `questions-presented.txt`, `petition.txt`, `appendix.txt`, `metrics/statpack.md`) and local CLI checks (`fedcourts paths`, `fedcourts validate`). Zero corpus queries, CourtListener searches, or web searches were executed (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`).
