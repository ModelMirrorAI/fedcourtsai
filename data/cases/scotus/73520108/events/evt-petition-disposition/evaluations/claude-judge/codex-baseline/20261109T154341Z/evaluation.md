# codex-baseline — P(grant) 0.38, predicted denied; outcome granted

Brier (0.38 − 1)² = **0.3844**; correct 0.

## Outcome and scoring frame

This is a **cert** cell (`stage: cert`, `moment: distribution`) for *Goldman Sachs Bank USA v. Brown*, No. 25-1408. The petition was distributed four times (9/28, 10/9, 10/16 and 11/6 conferences) and **granted** on 2026-11-06 on the plenary route, with no CVSG. All three candidates predicted `denied` from the 2026-10-05 snapshot (two distributions), so `correct` = 0 for each. The anchor is the stamped segment base rate, which the harness pools from the frozen `elevated` band under sal-v4. I quote no rate of my own, and `brier_skill_score` is the harness's as well. Votes are not scored on a cert cell. No semantic set is declared, so I wrote no `semantic_grades`.

**Leakage.** The cell is forward: predicted 2026-10-06 and resolved 2026-11-06, a month later. Nothing in the log or the prose shows this petition's disposition, and none existed when it ran. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (own read): 0.5.** A first look at FAA-versus-Bankruptcy-Code arbitrability under *McMahon*, over a clean 4th/2nd Circuit split, reaching consumer-credit arbitration clauses across consumer bankruptcies. It matters to business and statutory practice and has low general salience.

## Reasoning quality: 0.60

This was a disciplined rationale. It pooled the frozen sal-v4 `elevated` band over prior Terms with explicit numerators. It was careful not to double-count the relist and not to read terminal relist buckets as hazards. Its account of the split, the King dissent and the FAA framework was accurate. It weighed the BIO's Chapter 13/§105(a) distinctions and the Sept 10 dismissal from the supplemental briefs it retrieved. It put more weight on the upward case than the other candidates did, which left it the closest to the outcome. It is somewhat less substantive than claude-baseline: it did not read the reply and treated the opposing objections only at a summary level. It also leaned on the vehicle concern, which the grant shows did not decide the case. The probability was a reasonable one for an informed reader, and its reasons were sound, but it still landed on denial.

## Predicted reasoning: 0.22

I treated these as central claims: denial; no further distribution, with resolution in October–November; the unstable pleading as the reason to pass; no CVSG; and plenary on the QP if granted. The disposition failed. The point forecast of no further distribution failed, since two followed, although the October–November timing held. The vehicle rationale the document put forward as the main reason to pass failed. The plenary/QP and no-CVSG calls held but discriminate little. The document was specific, and its specific central calls failed, so it sits a little below the 0.25 anchor.
