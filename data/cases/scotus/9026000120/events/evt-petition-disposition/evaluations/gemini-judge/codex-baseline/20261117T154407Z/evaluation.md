# Evaluation of `codex-baseline` — `scotus/9026000120` (`evt-petition-disposition`)

## Outcome and Quantitative Summary

On November 16, 2026, the Supreme Court denied certiorari in *Gays Against Groomers, et al. v. Garcia, et al.* (No. 26-120) directly off the November 13, 2026 conference without any further relist (`distribution_count = 2`), CVSG (`cvsg_date = null`), or noted dissent (`noted_dissent_from_denial = false`).

- **Stage:** `cert` (`moment: distribution`). Baseline and skill fields (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) are left null for the harness to stamp from the committed statpack.
- **Disposition accuracy (`correct`):** `1` (`denied` vs. `denied`).
- **Probability / Brier (`brier_score`):** `P(grant) = 0.22` → `(0.22 - 0)^2 = 0.0484`.
- **Statpack build verified against:** `ca0c9e1a49e292692bdc5b092cd9f868561169b8` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`), reconstructed via `fedcourts statpack-at`. Every statpack count and marginal cut `codex-baseline` quoted matches that pinned build exactly.

## Reasoning Quality (`reasoning.md` — `0.84`)

`codex-baseline` delivered a thorough, well-researched legal and empirical analysis in `reasoning.md`:

- **Doctrinal precision and Split verification:** `codex-baseline` accurately identified why Question 1 faced a steep hurdle under *Supreme Court of Virginia v. Consumers Union of the United States, Inc.*, 446 U.S. 719 (1980), and why the asserted circuit split relying on *Kentucky v. Graham*, 473 U.S. 159 (1985), was illusory for state legislators. Rather than taking the briefs' descriptions at face value, `codex-baseline` checked the cited Fifth and Ninth Circuit authorities directly (`Minton`, `Schmidt` n.10, and the unpublished `Bols` memorandum) and rightly highlighted the structural Eleventh Amendment distinction between municipal entities (directly suable under *Monell*) and state legislatures (reachable only through *Ex parte Young* suits against state officers).
- **Vehicle and Question 2 analysis:** `codex-baseline` correctly explained why Question 2 sat downstream of Question 1, noted Respondents' *Powell v. McCormack* / *Kilbourn v. Thompson* point that Petitioners sued only five state legislators rather than any non-legislator enforcement officer (such as a sergeant-at-arms), and properly evaluated Judge Carson's concurrence alongside *Bogan v. Scott-Harris*, *Houston Community College System v. Wilson*, and Justice Thomas's concurrence in *West Virginia v. B.P.J.* (2026).
- **Base-rate discipline vs. final calibration:** `codex-baseline` handled the pinned statpack (`ca0c9e1a49e2`) carefully—distinguishing risk-set (`reached`) from terminal `elevated` figures, avoiding additive double-counting with `amicus-line.json`, and recognizing that `distribution_count = 2` came from a November 5 pre-conference `Rescheduled` entry rather than a post-conference relist. The main weakness in `reasoning.md` is calibration: after convincingly demonstrating that the second distribution was only a pre-conference reschedule, that *Consumers Union* squarely governed, that the circuit split evaporated on inspection, and that no non-legislator actor was sued, `codex-baseline` still assigned `P(grant) = 0.22`—barely discounting below the stamped segment base rate (whose `elevated` risk set is heavily populated by true post-conference relists) and overweighting speculative grant paths.

## Predicted reasoning (`predicted_reasoning.md` — `0.76`)

`codex-baseline`'s forecast document committed to three testable central claims on the cert trajectory and one conditional merits/grant-scope claim:

1. **Modal disposition without separate writing (`borne-out`):** Led with the call that the Court would most likely deny the petition without a separate writing, matching the November 16, 2026 unwritten denial order (`noted_dissent_from_denial = false`).
2. **Immediate post-conference denial without further relist (`borne-out`):** Identified a clean denial off the November 13, 2026 conference (`distribution_count` remaining 2) as the modal path, while hedging meaningfully (~30% probability) toward at least one post-conference relist.
3. **No CVSG (`borne-out`):** Specifically explained why no federal statute, program, or forum warranted inviting the Solicitor General (`cvsg_date = null`).
4. **Conditional grant route and scope (`unresolved`):** Discussed full plenary review vs. summary reversal/GVR and Question 1 vs. both questions conditionally on a grant that did not occur.

Every testable modal call held up and was grounded in case-specific procedural context rather than boilerplate, earning a solid grade above `0.75`, though noticeable hedging on post-conference relists and separate-writing paths keeps it well below the top anchor.

## Leakage Assessment

`codex-baseline` ran in `forward` mode on November 9, 2026 (`20261109T171058Z`), four days before the November 13 conference and seven days before the November 16 denial. Inspection of `retrieval_log.json` (31/33 calls captured; 2 unobserved hosted web searches for open-petition coverage) confirms no outcome-revealing material existed or was retrieved (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`).
