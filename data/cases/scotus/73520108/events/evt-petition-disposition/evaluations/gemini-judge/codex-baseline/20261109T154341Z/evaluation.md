# Evaluation of `codex-baseline`

## Outcome and Quantitative Summary

- **Event:** `evt-petition-disposition` (`scotus/73520108`, *Goldman Sachs Bank USA v. Brown*, No. 25-1408)
- **Actual outcome:** `actual_granted = 1`, `actual_disposition = "granted"`, `disposition_route = "plenary"`, `resolved_at = "2026-11-06"`, `distribution_count = 4`, `cvsg_date = null`.
- **Candidate prediction:** `granted = 0`, `predicted_disposition = "denied"`, `probability = 0.38`.
- **Scoring:**
  - `correct`: `0` (predicted `denied` vs. actual `granted`)
  - `brier_score`: `(0.38 - 1)^2 = 0.3844` (best Brier score among the three candidates)
  - `segment_base_rate` and `brier_skill_score`: left null for the harness stamp (which computes the skill over the stamped segment base rate).

## Reasoning Quality (`reasoning_quality = 0.95`)

`codex-baseline` delivered the strongest overall analysis and best-calibrated probability (`0.38`) among the three candidates:

- **Factual and procedural precision:** Grounded every claim in specific citations to the petition, the Fourth Circuit majority and dissenting opinions in the appendix (pages 1a–28a, noting the exact truncation boundary of `petition.txt`), the BIO, and the September 14 and September 15 supplemental briefs. Accurately highlighted why co-respondent Maze's discharged Chapter 7 posture blunted respondents' attempt to distinguish *MBNA America Bank v. Hill* solely on the basis of Brown's ongoing Chapter 13 plan.
- **Precedent and statutory analysis:** Provided a rigorous account of the *McMahon* / *Epic Systems* displacement standard and the conflict between the Fourth Circuit's categorical rule on 11 U.S.C. § 362(k) claims and the Second Circuit's approach in *Hill*, while clearly separating private § 362(k) statutory damages claims from § 105(a) contempt sanctions (*Anderson*, *Belton*).
- **Calibration and base-rate discipline:** Checked against the prediction-time statpack build via `fedcourts statpack-at` (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sal-v4`), `codex-baseline` properly anchored on the prior-Term `elevated` bracketed `reached` pool without self-selection or double-counting the first relist. It then gave substantial weight to the petitioner's September 15 supplemental response—recognizing that because the Fourth Circuit announced a categorical forum rule on an interlocutory appeal from a motion to compel arbitration, a routine damages amendment in the bankruptcy court would not moot the arbitration question—landing at `0.38`, the highest grant probability in the panel.
- **Epistemic discipline:** Carefully distinguished verified record facts from contested party characterizations, documented the exact scope of its supplemental brief fetches, and explained why the petition was a live grant contender despite ultimately leaning toward denial.

## Predicted reasoning (`predicted_reasoning_quality = 0.6`)

In `predicted_reasoning.md`, `codex-baseline` laid out a detailed, well-structured conditional forecast:

1. **Primary disposition (`not-borne-out`):** Forecast an unexplained denial of certiorari as the single most likely outcome (`62%` denial / `38%` grant), reasoning that the contested split and unsettled bankruptcy pleadings would narrowly tip the Court against review. Because the Court granted certiorari on November 6, 2026, the primary disposition call was not borne out, though the document stressed that `0.38` represented a high grant hazard.
2. **Relist trajectory and resolution window (`borne-out`):** Assigned a `45%` probability of at least one further distribution beyond the October 9 conference and specifically predicted that the petition would resolve in October or November 2026 rather than being held for months. The Court distributed the case twice more (October 16 and November 6, `distribution_count = 4`) and granted certiorari on November 6, 2026.
3. **CVSG (`borne-out`):** Forecast a low (`6%`) probability of a CVSG because the dispute turns on private arbitration clauses and textual construction of the Bankruptcy Code rather than a federal regulatory program (`cvsg_date = null`).
4. **Disposition route and vehicle framing conditional on grant (`borne-out`):** Predicted that if granted, the Court was overwhelmingly likely (`92%` conditional probability; `8%` summary route) to set the case for plenary merits review on the single § 362(k) question presented as framed, leaving standalone § 105(a) contempt proceedings outside the question. This matched the November 6 plenary grant order (`disposition_route = plenary`).
5. **Merits direction conditional on grant (`unresolved`):** Forecast that on plenary review the Court would likely reject a categorical Bankruptcy Code exception for § 362(k) damages claims under the FAA and reverse or vacate the Fourth Circuit. Because this event resolves only the cert stage, this merits claim is `unresolved`.

While the modal denial prediction failed, `codex-baseline` gave the highest grant probability (`0.38`), accurately called the October/November 2026 resolution window after additional relists without a CVSG, and nailed the conditional plenary grant structure, earning `0.6`.

## Leakage Assessment (`not_applicable`, `leakage_suspected = false`)

- **Mode:** `forward` (`snapshot_date: 2026-10-05`, `created_at: 2026-10-06T00:25:04Z`, `resolved_at: 2026-11-06`).
- **Audit of `retrieval_log.json` and `retrieval.md`:** `result_capture_coverage` is `0.96875` (one failed `web.open` attempt on the Sept. 14 PDF URL was logged as `unobserved` before the agent fetched the same URL via Python `urllib.request` + `pypdf`). Every external fetch was strictly limited to two supremecourt.gov PDF URLs already listed in the provisioned October 5, 2026 snapshot: respondents' September 14, 2026 supplemental brief and petitioner's September 15, 2026 supplemental response. Both predated the November 6, 2026 grant by over seven weeks.
