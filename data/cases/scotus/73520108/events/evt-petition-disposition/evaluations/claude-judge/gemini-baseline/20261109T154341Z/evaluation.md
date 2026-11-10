# gemini-baseline — P(grant) 0.35, predicted denied; outcome granted

Brier (0.35 − 1)² = **0.4225**; correct 0.

## Outcome and scoring frame

This is a **cert** cell (`stage: cert`, `moment: distribution`) for *Goldman Sachs Bank USA v. Brown*, No. 25-1408. The petition was distributed four times (9/28, 10/9, 10/16 and 11/6 conferences) and **granted** on 2026-11-06 on the plenary route, with no CVSG. All three candidates predicted `denied` from the 2026-10-05 snapshot (two distributions), so `correct` = 0 for each. The anchor is the stamped segment base rate, which the harness pools from the frozen `elevated` band under sal-v4. I quote no rate of my own, and `brier_skill_score` is the harness's as well. Votes are not scored on a cert cell. No semantic set is declared, so I wrote no `semantic_grades`.

**Leakage.** The cell is forward: predicted 2026-10-06 and resolved 2026-11-06, a month later. Nothing in the log or the prose shows this petition's disposition, and none existed when it ran. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (own read): 0.5.** A first look at FAA-versus-Bankruptcy-Code arbitrability under *McMahon*, over a clean 4th/2nd Circuit split, reaching consumer-credit arbitration clauses across consumer bankruptcies. It matters to business and statutory practice and has low general salience.

## Reasoning quality: 0.40

This was a short rationale. It used the right anchor family (prior-Term `elevated`, roughly 17–19%) and identified the correct upward drivers: the Court's FAA-enforcement record, the split with *Hill*, Latham as counsel and the ABA amicus. Its closing intuition, that the Court is skeptical of judge-made FAA exceptions, pointed the right way. But it never mentions the Sept 10 dismissal of the adversary complaint, the most salient vehicle development before the snapshot, which was docketed in the provisioned record as the supplemental briefs. Its handling of *Anderson*/*Belton* is loose: it calls them the Second Circuit "retreating" from *Hill*, which is the BIO's characterization, and adopts that characterization without testing it. The adjustment from about 18% to 0.35 is asserted, not reasoned. The direction was sensible, but the analysis was thin.

## Predicted reasoning: 0.30

I treated these as central claims: a 30% chance of a further relist, with no further relist as the central call; no CVSG; and plenary on the QP if granted. The further-relist call failed, since two more distributions followed. The no-CVSG and plenary/QP calls held but discriminate little. The dissent-from-denial and merits-reversal content is conditional on events that have not occurred, so it is unresolved. The document does not state a denial forecast in its own text, so its failed disposition call costs it less than it costs the others. It is generic, with one specific central claim that failed, so it sits slightly above the 0.25 anchor.
