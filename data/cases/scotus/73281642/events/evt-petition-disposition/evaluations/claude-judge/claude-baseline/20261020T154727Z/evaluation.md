# Evaluation: claude-baseline

**Cell:** scotus/73281642 (Hadley v. City of South Bend, No. 25-1158), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 after three distributions (conferences of 9/28, 10/9 and 10/16) and no noted dissent from denial.

**Base rate:** the prediction froze band `baseline` under `sal-v4` (Term 2025). That makes this a frozen-band cert cell, so `segment_base_rate`, `brier_skill_score` and `base_rate_basis` belong to the harness and I left them null. Compare against the stamped segment base rate. (My own cell's `record/context.json` carries the terminal band `high`, which reflects the two later relists. The stamp does not use it.)

**Leakage:** this was a forward prediction made on 2026-09-16, before the petition's first conference. No outcome existed yet, and nothing in the log or the reasoning reads this petition as decided. Grade: `not_applicable`, not suspected.

**Big case (my read, 0.45):** the question recurs and there is a real disagreement among circuits over the police-power exception to the Takings Clause. But the Court has now declined it several times, and the stakes in this case are modest.

The candidate read the Seventh Circuit opinion below (2025-10-07) through CourtListener and confirmed that this docket was not terminated as of its last modification on 2026-06-24. Its corpus query for Baker returned no rows. All of this is legitimate forward context.

**Scores:** predicted `denied` at P(grant)=0.22. Correct (1). Brier = 0.22² = 0.0484.

**Reasoning quality, 0.80.** This is the strongest analysis of the three. It anchors on the band table (about 5.1%) and lists balanced adjustments in both directions. Above all, it identifies the decisive consideration for denial: the Court had already denied the same question from the same counsel in Lech (2020), Baker (2024) and Slaybaugh (2025), one of them after a statement by two Justices. It pairs that with the opposition's argument that the circuits converge on outcomes, and it notes the Cedar Point dictum. It also gives the strongest case for a grant (the exception was the sole ground of decision, and percolation has continued since Baker) and states an honest range of 0.12–0.35. The petition was relisted twice and then denied with no noted writing, which matches its picture of the Court giving the case a close look and passing. Points deducted: given the history of denials it collected, a fourfold lift to 0.22 is still generous. Its 0.5 conditional probability of a dissent from denial did not materialize, though that claim is the harness's to score, not mine.
