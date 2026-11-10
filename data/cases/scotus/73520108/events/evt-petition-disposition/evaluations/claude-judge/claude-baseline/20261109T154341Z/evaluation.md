# claude-baseline — P(grant) 0.30, predicted denied; outcome granted

Brier (0.30 − 1)² = **0.49**; correct 0.

## Outcome and scoring frame

This is a **cert** cell (`stage: cert`, `moment: distribution`) for *Goldman Sachs Bank USA v. Brown*, No. 25-1408. The petition was distributed four times (9/28, 10/9, 10/16 and 11/6 conferences) and **granted** on 2026-11-06 on the plenary route, with no CVSG. All three candidates predicted `denied` from the 2026-10-05 snapshot (two distributions), so `correct` = 0 for each. The anchor is the stamped segment base rate, which the harness pools from the frozen `elevated` band under sal-v4. I quote no rate of my own, and `brier_skill_score` is the harness's as well. Votes are not scored on a cert cell. No semantic set is declared, so I wrote no `semantic_grades`.

**Leakage.** The cell is forward: predicted 2026-10-06 and resolved 2026-11-06, a month later. Nothing in the log or the prose shows this petition's disposition, and none existed when it ran. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (own read): 0.5.** A first look at FAA-versus-Bankruptcy-Code arbitrability under *McMahon*, over a clean 4th/2nd Circuit split, reaching consumer-credit arbitration clauses across consumer bankruptcies. It matters to business and statutory practice and has low general salience.

## Reasoning quality: 0.62

This was the strongest-researched rationale in the cell. It anchored correctly on the frozen band (sal-v4 `elevated`, prior Terms only) and cross-checked against the relist hazard. It then built a careful case on both sides: the acknowledged split with *MBNA v. Hill*, flagged by Judge King's dissent; the Court's FAA-displacement docket; petitioner-side quality and the ABA amicus. Against those it weighed the Sept 10 dismissal, the open-Chapter-13/§105(a) distinctions and the earlier *Anderson*/*Belton* denials. It read the pre-snapshot reply and supplemental briefs, and it disclosed every source openly. The miss lies in how it weighed the evidence. It treated the relist as mostly a vehicle check prompted by the dismissal and moved down to 0.30, below where its own upward case pointed. It even named the counter-reading ("a reader who reads relists after the long conference as mostly pre-grant should sit nearer 0.40"). The Court granted, and the vehicle problem did not deter it. The analysis was sound and well documented, but the decisive judgment call went the wrong way.

## Predicted reasoning: 0.25

I treated these as central claims: the denial lean; resolution at or just after Oct 9, with 0.42 on a further distribution; plenary on the QP if granted; no CVSG; and the relist read as a vehicle check. The disposition call failed. Two further distributions followed, so the timing call failed too. The vehicle-check reading of the relist was not borne out by the grant. The plenary grant on the QP and the absence of a CVSG held, but both are low-discrimination calls for a paid petition. The conditional merits ground earns neither credit nor penalty because no judgment has been entered. A central claim failed and the rest was mixed, which puts the document at the 0.25 anchor.
