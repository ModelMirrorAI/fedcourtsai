# Evaluation — `codex-baseline` (`scotus/9026000239`, `evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / moment:** `cert` (`moment: arrival`, opened `2026-08-24`).
- **Outcome (`2026-11-13`):** Certiorari **granted** (`actual_disposition: "granted"`, `actual_granted: 1`, `disposition_route: "plenary"`, `disposition_basis: "standard"`), after two distributions (`11/06/2026` and `11/13/2026`, `distribution_count: 2`) and no CVSG (`cvsg_date: null`), with the docket order reading: *"Petition GRANTED limited to Questions 1 and 2 presented by the petition."*
- **Prediction:** `predicted_disposition: "granted"`, `probability: 0.92` (`correct = 1`, `brier_score = 0.0064`), outperforming the stamped segment base rate.

## Rationale Quality (`reasoning_quality`: 0.89)

`codex-baseline`'s `reasoning.md` combines rigorous base-rate conditioning with substantive statutory and precedential analysis:

1. **Sound historical base-rate pooling.** Checked against the reconstructed statpack build in force when it ran (`02dd6a20fccc`, `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, `sal-v3`, rather than the current committed `sal-v8` pack), `codex-baseline` accurately pools the `sal-v3` `federal` band across Terms 2017–2025 (`201` resolved weighted cases, `~71%` grant-family rate) and explicitly notes why that arrival risk-set rate — rather than the terminal zero-relist rate — governs a newly docketed paid petition at `distribution_count = 0`.
2. **Doctrinal depth and comparator analysis.** `codex-baseline` goes beyond generic institutional heuristics to read and distinguish the petition's key June 2026 Supreme Court comparator, *Mullin v. Al Otro Lado* (No. 25-5, decided June 25, 2026, 6–3), recognizing that *Al Otro Lado* reinforced the current six-Justice majority's text-focused immigration posture while leaving open this case's distinct statutory question because *Al Otro Lado* involved aliens outside the United States rather than aliens physically present after crossing the border. It also squarely identifies the government's textual vulnerability under 8 U.S.C. § 1158(a)(1) ("physically present in the United States ... irrespective of such alien's status"), the D.C. Circuit's stay of its mandate pending Supreme Court review, and the arrival-moment truncation of the 408-page PDF inside the lower-court opinion appendix.
3. **Minor analytical weaknesses.** Two points hold `reasoning.md` slightly back: (a) it treats the possibility that the Court might "prefer further percolation" as a primary downward adjustment without noting that the universal class relief entered in the D.C. Circuit practically forecloses parallel circuit percolation elsewhere; and (b) it assigns a notably high `0.22` conditional probability to a GVR or summary disposition based on *Al Otro Lado*, *Aleman Gonzalez*, or *Trump v. CASA*, even though all three decisions predated the D.C. Circuit's July 23, 2026 denial of rehearing (and were already briefed in a petition expressly seeking plenary review of a flagship presidential proclamation).

## Predicted reasoning (`predicted_reasoning_quality`: 0.84)

`codex-baseline`'s `predicted_reasoning.md` was directionally accurate across every testable cert-stage dimension, sitting solidly above `0.75` while tempered slightly by hedging on QP 2 and summary-route odds:

- **Conference count, relist path, and no CVSG (central, borne out):** Forecast that the petition would be distributed at least once and "probably be granted after its initial conference or one relist," with no CVSG. That matched the actual trajectory closely: distributed for the November 6, 2026 conference, relisted once, and granted at the November 13, 2026 conference (`distribution_count: 2`, `cvsg_date: null`).
- **Ordering of the three questions presented (central, borne out, mildly hedged):** Forecast that the Court would "most likely grant the first question ... and may add the Section 1252(f)(1) question," while treating the Article III / Rule 23 Question 3 as less likely to be granted. The Court granted *"limited to Questions 1 and 2 presented by the petition"*, bearing out both the inclusion of QPs 1–2 and the pruning of QP 3, though hedging QP 2 as "may add" committed somewhat less cleanly than a firm QP 1+2 call.
- **Plenary route over summary action (central, borne out, hedged):** Correctly called plenary briefing and argument as more likely than summary disposition (`disposition_route: "plenary"`), though describing a GVR or narrow summary ruling as "a material alternative" hedged a path that was institutionally remote given the pre-rehearing timing of the cited precedents.
- **Post-grant merits and conditional denial (conditional, unresolved):** Its conditional predictions of merits reversal on at least one ground and a silent denial if cert were denied were not tested by the cert-grant outcome.

## Leakage Assessment

- **Mode:** `forward` (`run_id: 20260824T231410Z`, `result_capture_coverage: 0.9118`).
- **Assessment:** Clean (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`). The prediction ran on `2026-08-24` (docketing day, nearly three months before the `2026-11-13` grant order). All shell wrapper calls were captured (only synthetic MCP mirror entries were marked `unobserved`), retrieval was limited to pre-decision inputs, `metrics/statpack.md`, and the June 25, 2026 *Mullin v. Al Otro Lado* opinion on CourtListener, and no call touched `data/qp-topics/`.
