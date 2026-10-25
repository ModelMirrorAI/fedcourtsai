# Evaluation — gemini-baseline

**Cell.** Interim stage (stay application 26A532, *Frank Michael Monte, III v. United States*, submitted to Justice Alito on 2026-10-10). The outcome is `denied` (`actual_granted` 0), resolved 2026-10-23, with no response request, no referral, and no amicus. Because the cell is interim, the segment base rate and Brier skill are stamped by the harness from the statpack's interim pool. I write neither, and `base_rate_basis` stays null. Vote accuracy is not scored on an interim cell. No semantic set is declared, so there is no `semantic_grades` block. `claim_scores` is computed by the harness.

**Score.** Predicted `denied` at P(grant) = 0.005, which is correct. Brier = 0.000025.

**Reasoning quality: 0.74.** This has the strongest factual development. Working through CourtListener, it established the underlying D.N.J. conviction (18 U.S.C. §§ 115 and 875(c)), the untimely collateral-relief posture, and that CA3 had entered judgment (2026-08-12) and issued its mandate (2026-10-16). That makes the near-zero grant probability well grounded rather than generic. The anchor (51/547) is correct. Two deductions:

1. It reads the statpack's escalation counts (129 response requests, 347 referrals over all substantive applications) as showing that "nearly all grants occur after" escalation. Those are marginal counts, not conditional rates, so the inference overreaches the table.
2. It says the anecdotal corpus comparisons are "uniformly denied." That rests on a handful of rows and is stated more strongly than ten rows can support.

The 0.5% figure is aggressive but well supported by this posture.

**Leakage.** Forward. Every call is unobserved (coverage 0.0), so I graded on the queries. It looked up its own docket's corpus row (26A532) and the lower-court dockets on 2026-10-22, the day before the denial, so no disposition existed to find. The lower-court entries after the cutoff (the CA3 judgment and mandate) predate the resolution and are legitimate forward signal, which it disclosed openly. Graded `not_applicable`.
