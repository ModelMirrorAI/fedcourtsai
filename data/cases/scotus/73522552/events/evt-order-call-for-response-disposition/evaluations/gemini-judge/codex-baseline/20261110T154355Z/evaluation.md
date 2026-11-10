# Evaluation of `codex-baseline` — *Eric Alan Isaacson v. Maribel Moses, et al.* (`scotus/73522552`, `evt-order-call-for-response-disposition`)

## Outcome and quantitative summary

- **Actual outcome**: `denied` (`actual_granted: 0`, `resolved_at: "2026-11-09"`, `noted_dissent_from_denial: false`, `signals.distribution_count: 2`, `signals.cvsg_date: null`).
- **Predicted disposition**: `denied` (`granted: 0`, `probability: 0.22`).
- **Accuracy (`correct`)**: `1`.
- **Brier score**: `(0.22 - 0)^2 = 0.0484`.
- **Baseline and skill**: `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for harness stamping against the stamped segment base rate.
- **Statpack build graded against for base-rate use**: Reconstructed via `uv run fedcourts statpack-at` for `run_id: "20261029T142045Z"` as commit `7bcde3b105cb212283905eda17b827efc188e80c` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`), which was in force when the candidate ran (as distinct from the currently committed `sal-v8` statpack).

## Reasoning quality (`reasoning_quality: 0.76`)

`codex-baseline`'s `reasoning.md` demonstrates strong record fidelity, exact base-rate anchoring against the statpack build in force when it ran (`7bcde3b105cb`, `sal-v4`), and disciplined primary-source retrieval, but is held back by a substantial calibration jump from its pre-cutoff `baseline` reached anchor to a `0.22` grant probability:

1. **Exact base-rate pooling (`7bcde3b105cb`, `sal-v4`)**: `codex-baseline` read both `metrics/statpack.md` and `metrics/statpack.json`, pooled the exact `baseline` `reached` counts across all strictly prior Terms `2017–2024` from the `sal-v4` statpack build in force at prediction time, and accurately cited the orientation cuts (`Modern discretionary-cert petitions by disposition`, paid terminal relist buckets, CVSG status, and amicus-brief counts). It also properly explained why terminal marginal cuts describe end-of-stage populations rather than forward conditioning rates at `response-requested`.
2. **Accurate reading of the staged record and primary dockets**: `codex-baseline` accurately cited the February 10, 2026 *Moses II* summary order (Pet. App. 9a–10a), the published *Moses I* opinion (79 F.4th 235, 253–56 (2d Cir. 2023)), the August 5, 2026 distribution, and the August 19, 2026 Call for a Response. It noticed the Chamber of Commerce counsel listing in the snapshot's `"Other"` block while observing that zero amicus-brief entries were visible in `ProceedingsandOrder` as of August 20, 2026, properly declining to infer a pre-cutoff brief or its side. It also retrieved the official Supreme Court dockets for *Johnson v. NPAS Solutions* (No. 22-389) and *NPAS Solutions v. Johnson* (No. 22-517), noting that No. 22-389 likewise received a Call for a Response (Dec. 13, 2022) before being denied (Feb. 21, 2023).
3. **Calibration tension (`0.22`)**: Despite establishing its `baseline` `reached` anchor from `statpack.md`, recognizing that the decision below is an unpublished summary order applying *Moses I* to a $5,000 award challenged by a pro se objector, and verifying from the No. 22-389 docket that the Court had previously called for a response on the lead Eleventh Circuit split case itself and still denied certiorari, `codex-baseline` raised its grant probability more than fourfold over the stamped segment base rate to `0.22`. That upward adjustment overweights the Call for a Response relative to the strong negative vehicle and repeat-issue signals documented in `codex-baseline`'s own analysis, producing a heavy Brier penalty (`0.0484`) when the petition was denied on the first post-response distribution.

## Predicted reasoning

Evaluated strictly against the resolved record (`outcome.json` and `2026-11-09.json`), `codex-baseline`'s `predicted_reasoning.md` (`predicted_reasoning_quality: 0.77`) was accurate on every unconditional claim and kept its conditional sections cleanly separated:

- **Disposition and separate writing (`borne-out`)**: Correctly forecast that the Court would most likely deny the petition without a separate writing (`actual_disposition: "denied"`, `noted_dissent_from_denial: false`).
- **Distributions (`borne-out`)**: Accurately noted the August 5, 2026 initial distribution and August 19, 2026 response request, and forecast one additional briefing-related distribution (`relist-increment: 0.98`) followed by disposition at the first post-response conference with no additional true relist on the modal path (`signals.distribution_count: 2`; redistributed Oct. 7, 2026 for the Nov. 6, 2026 conference and denied Nov. 9, 2026).
- **CVSG (`borne-out`)**: Correctly forecast no CVSG (`cvsg-increment: 0.015`; `signals.cvsg_date: null`).
- **Conditional grant scope and route (`unresolved`)**: Properly framed its discussion of the single categorical *Greenough*/*Pettus* question and plenary-versus-summary review (`summary-disposition-route: 0.05`) as conditional on a grant.

With all unconditional claims borne out and conditional sections properly delimited (though slightly more hedged toward a multi-relist grant path than `claude-baseline`), `predicted_reasoning.md` earns `0.77`.

## Leakage and big-case read

- **Leakage (`not_applicable`, `leakage_suspected: false`)**: Forward prediction placed on October 29, 2026, eleven days before the November 9, 2026 denial. `retrieval_log.json` shows all corpus and web lookups were confined to prior cases (`--decided-before 2025` and the 2022–2023 *NPAS* dockets Nos. 22-389 and 22-517), with no post-cutoff own-case material accessed.
- **Big-case assessment (`evaluator_score: 0.35`)**: Forming an independent read of the case's stakes, a categorical Supreme Court rule on class-representative service awards under *Greenough*/*Pettus* and Rule 23 would affect settlement practice nationwide, though this petition involves a modest $5,000 award in private consumer litigation affirmed by summary order and ended in an unremarked cert denial.
