# Evaluation of `codex-baseline`

## Overview and quantitative summary

This is a **cert**-stage evaluation for `scotus/9026000018` (*Westcott v. Voice of the Experienced*, No. 26-18), event `evt-petition-disposition`. The Court denied the petition on November 9, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`), after two total distributions (`distribution_count: 2`), with no CVSG and no noted dissent from denial.

- **Headline prediction:** `predicted_disposition = "denied"`, `probability = 0.12`.
- **Accuracy & Brier:** `correct = 1`, `brier_score = 0.0144`.
- **Baseline:** Evaluated against the stamped segment base rate (the harness stamps `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` from the prediction's frozen `state` band under `sal-v4`). Rebuilding the statpack in force at prediction time via `fedcourts statpack-at` (`build_sha: 1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`) confirms that `codex-baseline`'s exact weighted pool calculation from `statpack.json` over OT2017–OT2025 matches the build in force when it ran.

## Reasoning quality (`reasoning_quality = 0.92`)

`codex-baseline` produced a rigorous, well-calibrated analysis in `reasoning.md`:

- **Statistical discipline:** Computed the exact weighted `sal-v4` `state` reached pool from `statpack.json` in build `1c4f550b7b75` across OT2017–OT2025, while explicitly noting why terminal relist and CVSG buckets cannot be treated directly as forward hazards.
- **Doctrinal and vehicle analysis:** Checked *Turner v. Rogers*, 564 U.S. 431, 439–440 (2011), via CourtListener to verify the duration and recurrence prongs of the mootness exception, and balanced the upward signals (state petitioner, three mooted appeals under the 90-day PLRA cap, 11–6 en banc split with dissent, and the August 3 Call for a Response after waiver) against three distinct vehicle and split weaknesses demonstrated in the Brief in Opposition: (1) the district court's entry of final judgment in favor of Louisiana, superseding the expired preliminary injunctions; (2) the contested recurrence prong given materially different successive injunctions, policy changes, and the completed bench trial; and (3) respondents' distinction between interlocutory PLRA expiration cases and challenges to underlying short-duration conduct, plus whether the Fifth Circuit squarely decided QP 2.
- **Calibration and procedural reading:** Adjusting from the `state` risk-set anchor down to `0.12` reflected both the non-trivial attention signaled by the Call for a Response and the substantial vehicle barrier created by the final judgment in petitioners' favor. `codex-baseline` also clearly explained why `relist-increment` was `0.96`: because the requested October 2 opposition arrived after the September 28 conference named in the sole distribution entry, a scheduling redistribution was strongly expected to place the briefed petition before a later conference.

## Predicted reasoning (`predicted_reasoning_quality = 0.86`)

In `predicted_reasoning.md`, `codex-baseline`'s central testable claims all held up against the record:

1. **Denial of certiorari (`borne-out`):** Correctly forecast that the modal path was another distribution after responsive briefing followed by denial of the petition without a separate writing.
2. **One additional scheduling distribution (`borne-out`):** Specifically forecast **one additional distribution** (`0.96` probability of at least one further distribution) to place the now-briefed petition before a later conference after the October 2 opposition. On the actual docket, the petition was distributed once more on October 21, 2026 for the November 6, 2026 conference (`distribution_count = 2`) and denied on November 9, 2026.
3. **No CVSG (`borne-out`):** Correctly forecast no CVSG (`0.02` probability; `signals.cvsg_date = null`).
4. **No separate writing on denial (`borne-out`):** Forecast no separate writing as the modal outcome (`0.12` probability of a noted dissent or statement respecting denial); the November 9 denial carried no separate writing (`noted_dissent_from_denial = false`).
5. **Conditional grant route (`unresolved`):** Forecast that conditional on a grant, the Court would narrow QP 1 to the 90-day PLRA expiration and likely act via summary vacatur and remand (`0.65` conditional probability) rather than plenary review; this remained untested because certiorari was denied.

The forecast document is slightly less granular on the exact reply and conference calendar dates than `claude-baseline`'s, earning `0.86`.

## Leakage assessment

- **Mode:** `forward` (prediction timestamped `2026-10-06T00:30:13.589726Z`; event resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. Capture coverage was `0.9355` (29 of 31 calls captured; the 2 unobserved calls were provider-side web lookups for the 2011 *Turner v. Rogers* opinion, `564 U.S. 431`, which was then read via CourtListener MCP `opinion_id=9441801`). No search targeted this case's post-snapshot history or disposition, and the case remained open for over a month after the prediction ran.
