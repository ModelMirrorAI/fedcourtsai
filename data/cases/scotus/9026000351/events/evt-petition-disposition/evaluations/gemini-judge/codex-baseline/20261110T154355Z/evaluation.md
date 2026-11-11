# Evaluation of `codex-baseline` for `scotus/9026000351` (`evt-petition-disposition`)

## Quantitative Summary

- **Outcome:** `actual_disposition = "denied"`, `actual_granted = 0` (resolved November 9, 2026, after a single conference distribution for November 6, 2026, with no CVSG and no noted dissent from denial).
- **Prediction:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.002`.
- **Accuracy & Calibration:** `correct = 1`, `brier_score = 0.000004`. This is a cert-stage cell, so `vote_accuracy` and `judgment_correct` are omitted/null, and `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left for the harness to stamp against the stamped segment base rate.

## Reasoning Quality (`0.93`)

`codex-baseline` delivered a rigorous, well-structured analysis in `reasoning.md`:

1. **Base-Rate Grounding:** Because the committed statpack has since moved to `sal-v8`, I verified `codex-baseline`'s base-rate use against historical statpack build `eb6830084a18` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, reconstructed via `uv run fedcourts statpack-at`), which was in force at `20261023T012839Z` when the candidate ran under `sal-v4`. Against that build, `codex-baseline` accurately pooled the `sal-v4` `baseline` risk-set figures strictly prior to OT2026 (OT2017–OT2025) from `statpack.json` and properly distinguished the risk-set anchor (which corresponds to the stamped segment base rate) from terminal-band and post-relist figures.
2. **Jurisdictional & Vehicle Analysis:** `codex-baseline` pinpointed the decisive threshold obstacle from the provisioned appendix: the Court of Federal Claims dismissed the complaint for lack of subject-matter jurisdiction because the petitioner sought only nonmonetary declaratory relief, and the Federal Circuit summarily affirmed on May 22, 2026 under *United States v. Navajo Nation*, 556 U.S. 287, 290 (2009), noting that the petitioner acknowledged the absence of a money-mandating claim. `codex-baseline` also rightly explained why the 28 U.S.C. § 455 recusal argument failed to supply jurisdiction or create a circuit split, and why the Solicitor General's October 16, 2026 waiver and single conference distribution pointed strongly toward routine denial.
3. **Incremental Claims:** The probabilities assigned to `relist-increment` (`0.02`), `cvsg-increment` (`0.001`), `summary-disposition-route` (`0.15`), and `dissent-from-denial` (`0.005`) were logically justified—specifically noting that a CVSG is structurally inapt where the United States is already the respondent.

## Predicted Reasoning (`0.85`)

In `predicted_reasoning.md`, `codex-baseline` led with four testable central claims and one conditional grant claim:
1. **Denial following the November 6, 2026 conference without requesting a response** (`borne-out`): The Court denied certiorari on the November 9, 2026 order list following the November 6 conference without calling for a response.
2. **Zero additional distributions (`relist-increment`)** (`borne-out`): The petition was resolved on its first distribution (`distribution_count: 1`).
3. **No Call for the Views of the Solicitor General (`cvsg-increment`)** (`borne-out`): No CVSG was issued (`cvsg_date: null`).
4. **No separate writing or noted dissent from denial** (`borne-out`): Certiorari was denied without any noted dissent or separate statement (`noted_dissent_from_denial: false`).
5. **Conditional grant scope and route** (`unresolved`): `codex-baseline` reasoned that if review were granted, the Court would take Question Presented 3 (Tucker Act scope) and potentially Question Presented 2 (recusal) rather than Question Presented 1 (§ 354(a)(2)(A)(i)), and would favor plenary review over summary disposition (15% conditional probability). Because certiorari was denied, this conditional forecast remained untested.

All testable central claims were specific and borne out, earning `0.85`.

## Leakage Assessment

- **Mode:** `forward` (`run_id = 20261023T012839Z`, created October 23, 2026—more than two weeks before the November 6, 2026 conference and November 9, 2026 denial).
- **Transcript Review:** `retrieval_log.json` (`result_capture_coverage = 0.92`) confirms that `codex-baseline` read prompt, schema, statpack, and provisioned case files (explicitly excluding `data/qp-topics/**`), attempted one CourtListener citation lookup for `556 U.S. 287` (throttled HTTP 429), and ran two web searches for *Navajo Nation* (`556 U.S. 287`) and `28 USC 1491`. No outcome material existed at prediction time or was retrieved (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
