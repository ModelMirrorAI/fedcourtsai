# codex-baseline — P(grant) 0.24, predicted denied

## Outcome and scoring

Cert cell (`stage: cert`). The petition (No. 25-1427, *Independent Specialty Insurance Co. v. Apex Hospitality Group*) was distributed once (Aug 12 for the Sept 28 conference), a response was requested Aug 17, and on Oct 19, 2026 counsel filed a joint stipulation to dismiss under Rule 46; the petition was dismissed Oct 20. `actual_disposition` = `dismissed`, `actual_granted` = 0.

The prediction froze `context.band` = `baseline` (`sal-v4`), so the segment base rate, `brier_skill_score` and basis are the harness's to stamp; I wrote none of them — refer to the stamped segment base rate. `correct` is 0 on the exact-label axis (`denied` vs. `dismissed`), even though the binary no-grant call was right. No votes are scored on a cert cell; no semantic set is declared.

**Leakage:** forward cell, predicted 2026-10-06 against a 2026-10-05 snapshot; the event resolved 2026-10-20. Nothing in the log or prose surfaces the stipulation or dismissal. `not_applicable`, not suspected.

**Brier:** (0.24 − 0)² = 0.0576.

## Reasoning quality: 0.70

Strong points: careful reading of the provisioned record (it noticed the district-court discrepancy and followed the appended judgment), an explicit pooled anchor (593/11,580 ≈ 5.1%, strictly prior Terms), and independent verification on CourtListener that *GE Energy* left the governing-law question open and that *Setty* shows a real but narrower disagreement — it explicitly discounted the petition's 4–1 split characterization. It correctly identified this as a follower petition asking for a hold, with the GVR channel as the main route to a grant, and treated the response request as attention rather than votes.

Weaknesses: the move from 5% to 24% is the largest of the three and is "judgmental" without decomposition; it did not look up the lead petition's status, which is the load-bearing variable for a held follower. It did not consider early termination (settlement/dismissal) of either petition — the path this case took — though no candidate could reasonably have put much weight on it. The no-grant direction was right; the probability was the least well calibrated of the three.
