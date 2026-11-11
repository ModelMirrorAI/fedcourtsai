# Evaluation of `claude-baseline`

## Overview and Quantitative Scoring

- **Stage / Moment:** Cert (`stage: cert`), arrival moment (`moment: arrival`).
- **Outcome:** `denied` (`actual_granted = 0`), resolved on November 9, 2026 after a single conference distribution (`distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.003`.
- **Accuracy & Brier Score:** `correct = 1`; `brier_score = (0.003 - 0)^2 = 0.000009`.
- **Base-rate reference:** Because a statpack refresh landed after `claude-baseline` ran on `2026-08-27T15:51:20Z`, `claude-baseline`'s base-rate citations were checked against the statpack build in force at prediction time (`061c238147aa`, digest `sha256:0d05c670da5896c5e3078e0f81cbb775a2045fc05432d8d957b929849c02f891`, reconstructed via `uv run fedcourts statpack-at`). `claude-baseline` properly pooled the `sal-v3` `baseline` bracketed `reached` rates across strictly prior Terms (2017–2025) from that build, matching the stamped segment base rate methodology.

## Reasoning Quality (`0.92`)

When `claude-baseline` ran on August 27, 2026, `record/documents/` had not yet been fetched (the petition and questions presented were fetched on August 28, 2026). Rather than relying solely on the bare Supreme Court docketing entry, `claude-baseline` used targeted CourtListener MCP lookups to trace the consolidated Ninth Circuit appeals (`25-270` and `25-1026`) and the underlying Central District of California dockets (`2:23-cv-06850`, `2:24-cv-03455`, and `2:21-cv-04793`). From those records, it accurately reconstructed the pro se posture of Randy and Evgenia Quaid, the identity of the appellees (attorney Craig Granet and Montecito property buyers R. Scott and Lannette Turicchi), and the serial relitigation history following early district court dismissals.

In addition, `claude-baseline` demonstrated a strong grasp of the mechanical claim definitions—specifically recognizing that at `moment: arrival` (`distribution_count = 0`), `relist-increment` resolves to 1 upon the initial conference distribution (`0.95`), and that `summary-disposition-route` is conditioned on a grant—and explicitly accounted for the uncertainty from not having the petition text in hand.

## Predicted reasoning (`0.8`)

`claude-baseline`'s `predicted_reasoning.md` was detailed, specific, and largely borne out:
1. **Disposition and timing (`borne-out`):** Forecast that the petition would be distributed for a single conference in late October or November 2026 and denied in a one-line order within a week of that conference. In fact, the petition was distributed on October 14, 2026 for the November 6, 2026 conference and denied in a one-line order on November 9, 2026 (three days later).
2. **Single distribution without relisting (`borne-out`):** Forecast that the petition would move from zero distributions to exactly one distribution (`distribution_count = 1`) and be denied without relisting. Confirmed by `signals.distribution_count: 1`.
3. **Respondent waivers by September 28, 2026 (`not-borne-out` / partial):** Forecast that the respondents—specifically identifying attorney Craig Granet and home buyers R. Scott and Lannette Turicchi—would waive a response by the September 28, 2026 due date. Granet, the Turicchis, Susan Williams, and Bruce Berman did file waivers on September 11, 2026, exactly as predicted for those parties, but co-respondents Fidelity National Title Insurance Company and James Hepworth filed a Brief in Opposition on September 28, 2026 (followed by a reply brief on October 5, 2026).
4. **No CVSG and no summary disposition (`borne-out`):** Forecast neither a CVSG nor a GVR/summary disposition. Confirmed by `signals.cvsg_date: null` and `actual_disposition: "denied"`.
5. **No separate writing (`borne-out`):** Forecast no dissent from denial or statement respecting denial. Confirmed by `noted_dissent_from_denial: false`.

Under the rubric, `claude-baseline`'s forecast document committed to specific, falsifiable timing and procedural calls (late October/November conference, one-line denial within a week, exact distribution count of 1, and party waivers) where nearly all central claims held and the waiver prediction held for the named individual respondents while missing the corporate co-respondent's BIO.

## Leakage Assessment

- **Mode:** `forward` (`2026-08-27T15:57:31Z`, on docketing day and over two months before the `2026-11-09` denial).
- **Findings:** `retrieval_log.json` (`result_capture_coverage: 1.0`, 26 calls) shows reads of the prompt, event metadata, context, snapshot `2026-08-28.json`, `metrics/statpack.md`, one `fedcourts query` call (`retrieved_doc_date: 2026-08-24`), and CourtListener MCP lookups of pre-petition Ninth Circuit and C.D. Cal. dockets (`retrieved_doc_date`s in 2023 and 2025). No outcome material existed or was retrieved (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
