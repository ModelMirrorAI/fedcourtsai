# Evaluation of `codex-baseline` — `scotus/73278467` (`evt-order-cvsg-disposition`)

## Outcome and Quantitative Summary

On November 9, 2026, the Supreme Court granted the petition for a writ of certiorari, vacated the Tenth Circuit's judgment, and remanded for further consideration in light of *West Virginia v. B. P. J.*, 609 U.S. 958 (2026), and *United States v. Skrmetti*, 605 U.S. 495 (2025) (`actual_disposition: "gvr"`, `actual_granted: 1`, `disposition_route: "gvr"`). Following the June 30, 2026 CVSG order, the Solicitor General filed an invited brief on September 25, 2026 recommending a GVR in light of *B.P.J.* and *Skrmetti* and advising against plenary review; the petition was distributed a third time on October 14, 2026 (`distribution_count: 3`) for the November 6, 2026 conference and resolved on November 9, 2026.

- **Label accuracy (`correct`)**: `codex-baseline` predicted `predicted_disposition: "denied"` against `actual_disposition: "gvr"`, so exact label match is **0** (`correct: 0`).
- **Brier score (`brier_score`)**: `codex-baseline` predicted `probability: 0.43` (`granted: 0`) against `actual_granted = 1`, yielding a Brier score of **0.3249** (compared against the stamped segment base rate).
- **Declared claims (scored in code by the harness)**: `codex-baseline` was the **only** candidate in this cell to place more than 50% conditional probability on `summary-disposition-route` (`0.55`), accurately forecasting that a cert-order GVR was more probable than a plenary grant, and also calibrated `relist-increment` (`0.95`) and `cvsg-increment` (`0.0`) cleanly.

## Reasoning Quality (`reasoning_quality`: 0.92)

### Record Grounding
`codex-baseline` carefully examined the provisioned snapshot, context, questions presented, and key sections of both `petition.txt` and `brief-in-opposition.txt`. It accurately identified:
- The party-presentation obstacle on Question 1 (that petitioners failed to press the *Turner v. Safley* argument below and accepted intermediate scrutiny after *Fowler*, as detailed at BIO pp. 6–7, 10–12).
- The interlocutory motion-to-dismiss posture, the contested nature of the circuit split, and the separate abusive-search claim on Question 2 that would survive regardless.
- Crucially, petitioners' alternative request for a GVR based on the Tenth Circuit's reliance on *Fowler v. Stitt* and this Court's vacatur of *Fowler* in light of *United States v. Skrmetti* (Pet. pp. 5, 15, 30–31; BIO pp. 23–26), supplemented by a targeted CourtListener check of *Skrmetti* (605 U.S. 495).
The only significant piece of context `codex-baseline` missed was that *West Virginia v. B.P.J.* (which reversed the Ninth Circuit's decision in *Hecox v. Little*, also cited by the Tenth Circuit) had been decided on June 30, 2026 — the day of the CVSG order — which reinforced the *Skrmetti* GVR pathway.

### Base-Rate Anchoring and Calibration
Evaluated against the statpack build in force when the candidate ran (`73762050f49c`, rebuilt via `fedcourts statpack-at`, rather than the later committed pack), `codex-baseline`'s statistical anchoring was exemplary. Using `statpack.json`, it computed the exact unrounded `sal-v4` `high`-band `[reached]` rate pooled across all eight strictly prior Terms 2017–2024 (excluding Terms 2025 and 2026), matching the stamped segment base rate, cross-checked the paid scored-segment CVSG cut without double-counting it as an independent multiplier, explained why terminal relist buckets do not estimate forward distribution hazards while a CVSG brief is pending, and cited the exact git commit timestamp of the statpack (`September 14, 2026, 11:02 UTC`) while distinguishing artifact commit vintage from live corpus poll freshness.

`codex-baseline` articulated an explicit, coherent four-way probability decomposition (`23.65%` cert-order GVR/summary disposition, `19.35%` plenary grant, `55%` denial, and `2%` dismissal/withdrawal, summing to `0.43` any grant and yielding `0.55` conditional probability on `summary-disposition-route`), and properly set the vacuous `cvsg-increment` claim to `0.0`. Its structural insight — that the party-presentation vehicle flaw depressed plenary review while the vacatur of *Fowler* in light of *Skrmetti* sustained the GVR route as the modal grant pathway — was borne out by the resolved record. Its overall grant probability (`0.43`) fell slightly short of the `0.50` threshold because it treated the Solicitor General's forthcoming recommendation as unmodeled uncertainty rather than accounting for the current SG's posture on biological-sex classifications and the intervening decision in *B.P.J.*.

## Predicted reasoning (`predicted_reasoning_quality`: 0.75)

`codex-baseline`'s forecast document (`predicted_reasoning.md`) committed to specific, discriminating claims about the GVR pathway, vehicle obstacles, and procedural trajectory that were largely borne out:
1. **GVR as the modal grant route (`borne-out`)**: The document forecast that conditional on any grant, disposition in the cert order was the likelier route (`0.55`), specifically stating that "[a] GVR for reconsideration of the equal-protection analysis is the principal summary route, given the petition's reliance on the vacatur of Fowler in light of Skrmetti." Both the Solicitor General's September 25, 2026 brief and the Court's November 9, 2026 order resolved the petition by GVR in light of *B.P.J.* and *Skrmetti*, highlighting the Tenth Circuit's reliance on *Fowler*.
2. **Party-presentation and pleading-stage barriers to plenary review (`borne-out`)**: The document explained that plenary review was depressed by the Tenth Circuit's party-presentation refusal to decide Question 1 and the motion-to-dismiss posture and surviving abusive-search claim on Question 2. The Solicitor General's brief relied on those same vehicle defects in advising against plenary review.
3. **Post-SG conference trajectory (`borne-out`)**: The document predicted that the SG would file an invited brief, that the petition would return to conference for "one or two additional distributions before disposition" with no second CVSG, and that the Court would resolve the petition during October Term 2026. The docket recorded exactly one additional distribution on October 14, 2026 and an OT2026 resolution on November 9, 2026.
4. **Close overall tilt toward denial over grant (`not-borne-out`)**: The document placed overall non-grant slightly ahead of grant (`57%` vs. `43%`), whereas the GVR pathway it identified carried the day (`actual_disposition: "gvr"`, `actual_granted: 1`).

Because its central structural and procedural claims — especially identifying a *Skrmetti*/*Fowler* GVR as the modal grant route over plenary review — were specific and borne out, with only the close top-line binary tilt falling on the denial side of `0.50`, `predicted_reasoning_quality` is graded at **0.75**.

## Leakage Audit

- **Mode**: `forward` (`influenced_prediction: "not_applicable"`, `retrieved_outcome_material: false`, `leakage_suspected: false`).
- **Evidence**: All tool calls in `retrieval_log.json` occurred on `2026-09-18T18:20–18:24Z`, prior to the SG brief (`2026-09-25`) and the GVR order (`2026-11-09`), and no live queries were made against Docket No. 25-442.
