# claude-baseline — P(grant) 0.25, predicted denied

**Cell.** Cert stage, forward. Outcome: denied on 2026-10-19 (actual_granted 0, a noted dissent from denial, two distributions). The prediction froze band `state` (sal-v4), so the segment base rate, its basis and the Brier skill score are left for the harness to stamp. Where this note compares against a base rate, it means the stamped segment base rate. No semantic grades, since this is not a merits cell. Leakage: forward, nothing post-resolution retrieved; see `leakage.notes`.

**Score.** Correct (denied). Brier = 0.25² = 0.0625.

**Reasoning quality: 0.75.** The candidate anchored properly on the frozen `state`/sal-v4 risk set, pooled over prior Terms (~99/421 ≈ 23.5%). It then weighed the offsetting factors accurately: on one side the relist, the state petitioner and 16 amicus States; on the other, no real split (McClendon in CA11 agrees with the decision below, and Arnold is a SORNA registration case), small practical stakes, an injunction narrowed to one respondent, and the district court's alternative lesser-scrutiny holding as a vehicle problem. It also explicitly raised the possibility that the relist meant a dissent from denial was being prepared, which is what happened.

Deductions:
- It quoted the relist-2 bucket (27.7% granted, 13.3% GVR) for a docket with two distributions, i.e. one relist. The statpack's relist-1 bucket (about 13.4% grant-family) is the matching row. Its main anchor was the band rate, so the error did not drive the number.
- It skipped the provisioned cert reply.
