# Evaluation — claude-baseline

**Cell:** scotus/73500235 (Walid bin ‘Atash v. United States), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 (`actual_granted` 0, no noted dissent from denial, three distributions).

**Baseline:** the scored prediction froze band `elevated` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and quote only "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. Votes are not scored on a cert cell, and no semantic set is declared, so no `semantic_grades` block is written. The claims block is scored in code and is not graded here.

**Prediction:** `denied`, P(grant) = 0.09. **correct** = 1, **Brier** = (0.09 − 0)² = 0.0081.

## Reasoning quality: 0.85

The strongest of the three. It anchors on the pooled elevated-band reached rate (about 17% over OT2017–OT2024), then moves down for reasons that turned out to matter:
- It reads the two distributions as reschedules, not post-conference relists, and declines to apply the relist-bucket grant rate. That is the right reading of the docket, and the statpack warns about exactly this.
- It names the structural vehicle point as decisive: the court-martial rule has been repealed, R.M.C. 705(d)(4)(B) is the only live rule with that language, and the D.C. Circuit has exclusive review. So the *Dean* conflict cannot recur or percolate.
- It counts the interlocutory mandamus posture against a grant, along with the Court's steady post-*Boumediene* denials of Guantanamo petitions.

It also weighs the upward pressures fairly: the stakes, the Wilkins partial dissent, the three-tribunals argument, and the companion petition. It says where to discount it, including that the Guantanamo pattern comes from memory rather than a corpus cut. Its dissent-from-denial estimate (0.15) matched the silent denial. Minor weakness: halving the anchor is still a judgment call with no stated empirical basis, and the companion-alignment reading of the reschedules rests on a footnote.

## Leakage

Forward. The log's captured calls (coverage 1.0) cover one corpus query and two empty CourtListener searches for the companion docket. Nothing about this case's disposition, which did not exist until 2026-10-19. `not_applicable`, not suspected.
