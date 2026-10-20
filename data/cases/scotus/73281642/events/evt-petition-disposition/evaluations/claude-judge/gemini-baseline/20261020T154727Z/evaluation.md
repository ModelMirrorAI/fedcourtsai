# Evaluation: gemini-baseline

**Cell:** scotus/73281642 (Hadley v. City of South Bend, No. 25-1158), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 after three distributions (conferences of 9/28, 10/9 and 10/16) and no noted dissent from denial.

**Base rate:** the prediction froze band `baseline` under `sal-v4` (Term 2025). That makes this a frozen-band cert cell, so `segment_base_rate`, `brier_skill_score` and `base_rate_basis` belong to the harness and I left them null. Compare against the stamped segment base rate. (My own cell's `record/context.json` carries the terminal band `high`, which reflects the two later relists. The stamp does not use it.)

**Leakage:** this was a forward prediction made on 2026-09-16, before the petition's first conference. No outcome existed yet, and nothing in the log or the reasoning reads this petition as decided. Grade: `not_applicable`, not suspected.

**Big case (my read, 0.45):** the question recurs and there is a real disagreement among circuits over the police-power exception to the Takings Clause. But the Court has now declined it several times, and the stakes in this case are modest.

**Scores:** predicted `denied` at P(grant)=0.12. Correct (1). Brier = 0.12² = 0.0144.

**Reasoning quality, 0.50.** The direction is right and the probability is well calibrated in hindsight. The analysis behind it is thin, though. It cites a baseline rate of "~5.7%" without showing how it pooled that figure. It calls the circuit split "clean" and the vehicle free of "apparent vehicle problems" without engaging the opposition's strongest argument: every circuit reaches the same result for reasonable damage during a lawful search, and the split is only in the reasoning. The upward adjustments rest mostly on who the counsel are and on Justice interest, asserted generally. The candidate missed the strongest signal for denial, which is that the Court had already denied the same question in Lech, Baker and Slaybaugh. The log shows it read only the first 100 lines of the brief in opposition. It ended up near the right number, but by moderating its view on relist count rather than by weighing the record.
