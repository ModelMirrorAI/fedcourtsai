# Evaluation — codex-baseline

**P(grant) 0.12, predicted `denied`. Outcome: denied. Correct = 1, Brier = 0.0144.**

## Reasoning quality: 0.80

Careful and well calibrated in method. It reads the docket correctly: two distributions with a response request between them are not two completed conferences. It takes the anchor from the statpack with exact arithmetic and says correctly that the relist and CVSG cuts describe terminal populations, so they are not forward probabilities. It points to the agency-specific arguments (the General Counsel/Board split, severance) as the only plausible routes to a GVR, then weighs them against *Slaughter* and the *Harris* denial as the government's brief reports them. It notes that the government's alternative request for summary affirmance would count as a grant on the binary axis, and splits its grant mass across grant routes to stay internally consistent.

The main weakness: it never checked the *Slaughter* holding or the *Harris* disposition independently. It took both from the government's brief, though it disclosed this. That reliance is partly why it stopped at 0.12, a meaningful amount of grant mass given that the decisive authority pointed the other way. The analysis is sound; the shrink from the anchor was cautious.
## Outcome and quantitative scores

This is a **cert** cell (forward mode). The petition was distributed for the 9/28 conference, the Court requested a response on Aug 13, the opposition was filed Sep 14, and the petition was redistributed for the 10/16 conference. It was **denied on 2026-10-19** with no noted dissent (`actual_granted` = 0).

The prediction froze `band: elevated` under `sal-v4`, so the base rate and skill score are left to the harness stamp. I left `segment_base_rate`, `brier_skill_score` and `base_rate_basis` null and quote no rate of my own: compare against "the stamped segment base rate". `claim_scores` is the harness's as well. No votes are scored at cert. No semantic set is declared, so this file has no `semantic_grades` block.

## Leakage

Forward cell: the prediction was made 2026-09-30 and the petition was resolved 2026-10-19. I checked the captured log for this petition's own disposition and found none. No call has a document date on or after the resolution, and nothing under `data/qp-topics/` was read. The grade is `not_applicable`.

## Big case (my read, 0.55)

Removal power over NLRB members matters for the separation of powers and for labor law. But after *Trump v. Slaughter* and the *Harris v. Bessent* denial, only a narrow carve-out question for adjudicatory bodies was left. The Court denied with no noted dissent.
