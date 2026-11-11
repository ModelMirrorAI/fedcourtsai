# Evaluation — gemini-baseline, evt-petition-arrival-disposition (scotus/9026000359, No. 26-359)

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution (respondent waived 2026-10-09; distributed 2026-10-14 for the 11/6/2026 conference); no CVSG, no noted writing.

## Scores
- denied vs. denied → **correct = 1**.
- P(grant) 0.01 → **Brier = 0.0001**.
- Segment base rate, skill, and basis are the harness's; refer to the stamped segment base rate. No votes scored (cert stage).

## Reasoning quality — 0.45
The right anchor (pooled prior-Term `baseline` reached rate) and the right main reason for moving down (QPs allege conflict with "well-established principles," not a split). Beyond that the analysis is thin. It asserts the decision below is unpublished on speculation ("such local disputes usually are"), which the staged record does not support; the petition does not say so, and nothing provisioned establishes it. It does not engage with the petition's substance. Its discussion of relists treats the zero-distribution arrival state as if a first distribution were a relist, which conflates distribution with relist (I note the confusion only as a reasoning flaw; the claims block is scored in code). The final number is reasonable, but the support is generic.

## Predicted reasoning — 0.45
Central claims: denial; no further relists; no CVSG; no separate writing. These held. But the document is short and generic. It commits to nothing beyond the modal outcome for a baseline paid petition: no timing, no waiver or response path, no conference. The conditional QP-4 takings call is untested. That puts it right in direction and generic, around the 0.5 anchor, with a small deduction for its muddled framing of distributions.

## Leakage
Forward; created 2026-09-27. Its log is fully unobserved (coverage 0.0), so I graded calls on their queries. They were provisioned-input reads, a statpack grep, and two generic corpus queries run while the case was pending. Nothing targets this petition's disposition. `not_applicable`, `leakage_suspected = false`.
