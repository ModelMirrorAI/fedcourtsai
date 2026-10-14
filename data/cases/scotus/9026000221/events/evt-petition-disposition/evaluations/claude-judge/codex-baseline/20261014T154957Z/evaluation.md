# Evaluation: codex-baseline, Purdy v. Kansas (No. 26-221), evt-petition-disposition

**Cell.** Cert stage, forward mode. The petition was denied on 2026-10-13 at its first distribution (`actual_granted` 0, no noted dissent, no relist, no CVSG).

**Scores.** The candidate predicted `denied` with P(grant) = 0.03, so `correct` = 1 and Brier = 0.0009. The prediction froze the `baseline` band under `sal-v4`, so the stamped segment base rate and the skill score are the harness's. The candidate pooled its own anchor by hand (5.016% reached, OT2017–2025); I did not check it or substitute one, and the board reads the stamped figure. Vote accuracy is not scored on a cert cell, and there is no semantic block.

**Reasoning quality: 0.85.** This is a careful, well-structured rationale:
- It anchors correctly on the sal-v4 baseline band's reached rate over strictly prior Terms. It explicitly declines to use the whole-docket rate and the terminal relist/CVSG buckets as forward hazards, and that is the right handling of those cuts.
- It names the vehicle problems the denial most plausibly turned on, and it reads them from the decision below (App. 13a–20a), not from the petition's advocacy:
  - the state postconviction Strickland posture, with an express alternative prejudice holding resting on the confession;
  - the contested testimonial character of a very young child's statement under Ohio v. Clark;
  - the AEDPA asymmetry that weakens the claimed circuit split.
- It credits the real strength of the petition, the Smith v. Arizona truth-use analogy, without overweighting it.
- It treats the response waiver as modest, not dispositive, evidence.

The deductions: the move from 5.0% to 3% is judgmental and not quantified, which the candidate says itself. Some of the precedent verification ran through tools that returned partial results.

**Leakage.** Forward cell, graded `not_applicable`. Its captured retrieval was:
- general precedent (Clark, Smith);
- two web attempts that returned nothing usable;
- local reads, including a `find … -not -path 'data/qp-topics/*'`, which excludes that path and is not a read.

Nothing about this petition's disposition was sought, and it did not yet exist on 2026-10-05.

**Big case.** My own read is 0.25 (see `big_case.notes`).
