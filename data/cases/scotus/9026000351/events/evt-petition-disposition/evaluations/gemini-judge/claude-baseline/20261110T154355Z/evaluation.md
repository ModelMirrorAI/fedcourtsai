# Evaluation of `claude-baseline` for `scotus/9026000351` (`evt-petition-disposition`)

## Quantitative Summary

- **Outcome:** `actual_disposition = "denied"`, `actual_granted = 0` (resolved November 9, 2026, after a single conference distribution for November 6, 2026, with no CVSG and no noted dissent from denial).
- **Prediction:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.003`.
- **Accuracy & Calibration:** `correct = 1`, `brier_score = 0.000009`. This is a cert-stage cell, so `vote_accuracy` and `judgment_correct` are omitted/null, and `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left for the harness to stamp against the stamped segment base rate.

## Reasoning Quality (`0.86`)

`claude-baseline` provided a concise and accurate rationale in `reasoning.md`:

1. **Base-Rate Grounding:** Because the committed statpack has since moved to `sal-v8`, I verified `claude-baseline`'s base-rate pooling against historical statpack build `eb6830084a18` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, reconstructed via `uv run fedcourts statpack-at`), which was in force at `20261023T012839Z` when the candidate ran under `sal-v4`. `claude-baseline` properly pooled the `sal-v4` `baseline` risk-set rows strictly prior to OT2026 (OT2017–OT2025) from that build (which corresponds to the stamped segment base rate) and treated the relist-0 terminal rate as an upper bound rather than a conditioned estimate.
2. **Case-Specific Adjustments:** `claude-baseline` concisely identified all of the primary downward factors: the petitioner's *pro se* status on the paid docket, the Solicitor General's October 16, 2026 waiver without a call for a response, the nonprecedential per curiam summary affirmance below under *United States v. Navajo Nation*, the petitioner's concession below that the claims are not money-mandating, the repeat-litigant history noted in the petition (including the June 22, 2026 mandamus denial and No. 26-9), and the jurisdictional barrier preventing the case from reaching Questions Presented 1 and 2. While slightly briefer on the statutory mechanics of 28 U.S.C. §§ 354 and 455 than `codex-baseline` and `gemini-baseline`, its legal judgment was sound and well-calibrated.

## Predicted Reasoning (`0.84`)

In `predicted_reasoning.md`, `claude-baseline` committed to five central claims (four resolved by the denial outcome and one conditional on a grant):
1. **Denial on the order list following the November 6, 2026 conference** (`borne-out`): The petition was denied on November 9, 2026 after the November 6 conference.
2. **No call for a response and no second conference / relist** (`borne-out`): `outcome.json` confirms `distribution_count: 1` with no response requested.
3. **No Call for the Views of the Solicitor General (CVSG)** (`borne-out`): `outcome.json` confirms `cvsg_date: null`.
4. **Conditional grant scope and route** (`unresolved`): `claude-baseline` stated that only Question Presented 3 (Tucker Act jurisdiction) had any traction if granted, with plenary review holding the larger share (~75%) over summary disposition (~25%). Because certiorari was denied, this conditional claim was not tested.
5. **No separate writing dissenting from denial** (`borne-out`): `outcome.json` confirms `noted_dissent_from_denial: false` and `writing_roles: null`.

All four testable central claims were borne out, earning `0.84`.

## Leakage Assessment

- **Mode:** `forward` (`run_id = 20261023T012839Z`, created October 23, 2026—more than two weeks before the November 9, 2026 denial).
- **Transcript Review:** `retrieval_log.json` (`result_capture_coverage = 1.0`) shows that `claude-baseline` read only prompt, schema, statpack, and provisioned case files, making no external web, MCP, or corpus queries. No outcome material existed at prediction time or was retrieved (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
