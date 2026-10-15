# Evaluation: gemini-baseline, Purdy v. Kansas (No. 26-221), evt-petition-disposition

**Cell.** Cert stage, forward mode. The petition was denied on 2026-10-13 at its first distribution (`actual_granted` 0, no noted dissent, no relist, no CVSG).

**Scores.** The candidate predicted `denied` with P(grant) = 0.04, so `correct` = 1 and Brier = (0.04 − 0)² = 0.0016. The prediction froze `context.band` = `baseline` under `sal-v4`, so the harness pools the risk-set anchor. The stamped segment base rate and the Brier skill score are the harness's, and I write neither. Vote accuracy is not scored on a cert cell. This is not a merits cell, so there is no semantic block.

**Reasoning quality: 0.45.** The direction is right and so are the main signals: a paid private petitioner, the baseline band, Kansas's response waiver, and no relist. The number sits sensibly just below the roughly 5% band anchor. The rationale is thin, though. It is one paragraph that names "vehicle issues" only generically ("e.g., harmless error, preservation"). It never engages the actual posture: this is a K.S.A. 60-1507 postconviction ineffective-assistance claim, and the Kansas Court of Appeals rested on an independent Strickland prejudice holding. That posture is the strongest reason this petition was denied, and the record put it in front of the candidate. The rationale also gives no reason for 0.04 over the anchor beyond "matching" it, and it does not cite any statpack figure. The call was correct, but it was reached with little analysis that would generalize.

**Leakage.** Forward cell, graded `not_applicable`. The log's result capture is 0.0, so every call is unobserved and I graded each on its query. Two kinds of call stand out. One is a corpus topic query with `--full`. The other is a set of CourtListener searches on the petitioner's name and the lower-court caption. All of them ran on 2026-10-05, eight days before the disposition existed, so they could not have retrieved it. The reasoning shows no sign of knowing the outcome.

**Big case.** My own read is 0.25: a recurring Confrontation Clause question in a poor collateral-review vehicle (see `big_case.notes`).
