# Evaluation: codex-baseline

**Cell:** scotus/73281642 (Hadley v. City of South Bend, No. 25-1158), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 after three distributions (conferences of 9/28, 10/9 and 10/16) and no noted dissent from denial.

**Base rate:** the prediction froze band `baseline` under `sal-v4` (Term 2025). That makes this a frozen-band cert cell, so `segment_base_rate`, `brier_skill_score` and `base_rate_basis` belong to the harness and I left them null. Compare against the stamped segment base rate. (My own cell's `record/context.json` carries the terminal band `high`, which reflects the two later relists. The stamp does not use it.)

**Leakage:** this was a forward prediction made on 2026-09-16, before the petition's first conference. No outcome existed yet, and nothing in the log or the reasoning reads this petition as decided. Grade: `not_applicable`, not suspected.

**Big case (my read, 0.45):** the question recurs and there is a real disagreement among circuits over the police-power exception to the Takings Clause. But the Court has now declined it several times, and the stakes in this case are modest.

The candidate searched for the 2024 Baker statement, which is precedent and not this case. It disclosed that those attempts and a CourtListener search for Baker returned nothing usable (one HTTP 429). It excluded `data/qp-topics` from a `find` with `-not -path`, which is not a read.

**Scores:** predicted `denied` at P(grant)=0.30. Correct (1). Brier = 0.30² = 0.09.

**Reasoning quality, 0.72.** The work is careful and transparent. It derives the anchor reproducibly (593/11,580 = 5.12% over OT2017–2024), separates terminal-state cuts from the forward anchor, and engages the opposition's best point: the circuits disagree in reasoning but converge on the result. It correctly identifies that as the pivotal uncertainty. It also states its information boundary and the limits of its retrieval honestly. The weakness is the size of the upward adjustment, about 6× to 30%, which the candidate itself calls judgmental. The candidate gives weight to the 2024 statement respecting denial in Baker but does not ask what the Court's repeated denials on this question say about how likely four votes are. That pattern is what in fact decided the petition. The 44% relist estimate was sound (the petition was relisted twice).
