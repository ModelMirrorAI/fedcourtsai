# Evaluation of `codex-baseline`

**Cell:** `scotus/9026000239` / `evt-order-relist-disposition` (`stage: cert`, `moment: relist`)  
**Outcome:** `granted` (`actual_granted: 1`, `disposition_route: plenary`, `disposition_basis: standard`, `resolved_at: 2026-11-13`, limited to Questions 1 and 2)  
**Prediction:** `granted` (`probability: 0.90`) — `correct: 1`, `brier_score: 0.01`

Per the cert-stage evaluation contract, `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left for the harness stamp; comparisons to the baseline refer to the stamped segment base rate. Base-rate and statpack citations in `reasoning.md` were checked against prediction-time statpack build `ca0c9e1a49e2` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, reconstructed via `fedcourts statpack-at`), which was in force at `codex-baseline`'s run (`20261109T171058Z`) prior to later committed statpack updates.

## Rationale (`reasoning_quality`: 0.88)

`codex-baseline` delivered a rigorous, methodologically disciplined, and factually exact analysis in `reasoning.md`:

- **Exact record and statpack discipline:** Checked against the staged record and prediction-time statpack build `ca0c9e1a49e2`, every procedural fact and statistical count in `reasoning.md` verified cleanly. `codex-baseline` accurately read the October 7 and November 9 distributions for the November 6 and November 13 conferences, spotted the four September 23 amicus entries despite `context.amicus_briefs: null` without altering the frozen context, noted which filings were marked `truncated: true` (`petition`, `decision-below`) versus complete (`brief-in-opposition`, `cert-reply`), anchored on its frozen `federal` band (`sal-v8`) without double-counting Solicitor General status, and properly treated the paid-segment relist (`2,532`, `495`, `483`), CVSG (`164`, `13,550`), and amicus (`1,446`) cuts as mixed-caption terminal cross-checks rather than forward hazards or independent multipliers.
- **Substantive synthesis of the filings and companion vehicle:** `codex-baseline` accurately synthesized Judge Childs's D.C. Circuit majority, Judge Walker's partial dissent, the panel's unanimous rulings on mandatory withholding/CAT and APA vacatur, the BIO's strongest statutory and vehicle objections (§ 1158(a)(1)'s right to apply vs. discretionary grant, *Chenery*, unchallenged vacatur of the guidance, § 1252(f)(1)'s scope, and the narrowed class definition), and the SG's reply highlighting *Department of Homeland Security v. D.V.D.*, No. 26-426 (verified as granted via corpus query). Crucially, it explained why plenary review remained modal despite *D.V.D.*: *D.V.D.* did not reach Question 1's substantive challenge to Proclamation 10,888's categorical asylum bar, and the stayed D.C. Circuit mandate meant denial would halt a nationwide presidential policy.
- **Overstated hold/GVR and further-relist weights:** The main substantive blemish in `reasoning.md` was assigning an illustrative `25%` probability to a hold-and-GVR (`30%` conditional summary route) and `46%` to at least one further distribution. Where the Solicitor General seeks urgent review of a nationwide invalidation of a presidential border proclamation and the centerpiece substantive question (Question 1) cannot be resolved by *D.V.D.*, holding the entire petition into 2027 for a partial remedial overlap was substantially less plausible than granting plenary review now and addressing Question 2 alongside Question 1.

## Predicted reasoning (`predicted_reasoning_quality`: 0.65)

`codex-baseline`'s `predicted_reasoning.md` got the modal disposition, plenary route, Question 1, and unsigned order right, but hedged substantially on timing/route and missed the discriminating Question 2 vs. Question 3 split:

1. **Modal disposition and plenary route (`borne-out`):** Correctly forecast a grant of certiorari (`90%`), with plenary review for briefing and argument (`70%` conditional) prevailing over a *D.V.D.* hold-and-GVR (`30%` conditional).
2. **Relist trajectory (`borne-out`, heavily hedged):** Placed no further distribution narrowly ahead (`54%` vs. `46%` for at least one further distribution, spanning November/December 2026 or a 2027 hold). While the modal side held when the Court granted on November 13 at `distribution_count = 2`, the nearly coin-flip framing committed weakly on timing.
3. **Scope of plenary grant (`not-borne-out` on the Q2/Q3 split):** Correctly forecast that plenary review would center on Question 1's asylum restriction without reopening mandatory withholding/CAT, and rightly noted that the Court could narrow the grant. However, between Questions 2 and 3, `codex-baseline` suggested the Court *"may also take the class-definition issue in Question 3"* while singling out Question 2 as *"especially susceptible to coordination with D.V.D."* In fact, the Court's November 13 order took Questions 1 and 2 and dropped Question 3 (*"Petition GRANTED limited to Questions 1 and 2 presented by the petition"*).
4. **Order writings (`borne-out`):** Correctly forecast that an unsigned order with no separate writings was most likely.

With the central disposition, plenary route, and Question 1 borne out, the Q2/Q3 scope lean reversed, and substantial hedging on further relists and hold/GVR, the forecast sits squarely between the `0.50` and `0.75` anchors at `0.65`.

## Leakage

Clean `forward` cell (`leakage_suspected: false`, `influenced_prediction: not_applicable`, `retrieved_outcome_material: false`). The prediction ran on `2026-11-09`, four days before the `2026-11-13` grant. All 5 `unobserved` `web-search` calls in `retrieval_log.json` targeted prior precedents (`20-322`, `17-965`) or the separate `26-426` (*D.V.D.*) docket, `data/qp-topics/` was excluded via `find -not -path`, and no outcome existed at prediction time.
