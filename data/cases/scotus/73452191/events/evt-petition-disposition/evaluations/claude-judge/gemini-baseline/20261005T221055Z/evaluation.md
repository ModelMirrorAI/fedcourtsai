# Evaluation of gemini-baseline — scotus/73452191, evt-petition-disposition

## Outcome and scores

Cert-stage cell, forward mode. The petition (No. 25-1356, Bernard v. Ignelzi) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = 0.012² = 0.000144.
- `segment_base_rate` = 0.0512 on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's band table heading is `sal-v4`, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017 through OT2024, eight rows, n = 11,580; OT2025 excluded as the case's own Term, OT2026 empty). The table renders all 10 Terms the pack holds, so the rendered window and the configured ten-Term lookback reach the same eight rows; no divergence to flag.
- `brier_skill_score` = 1 − 0.000144 / 0.0512² = 0.945.
- `vote_accuracy` omitted (cert cell). `judgment_correct` null. No `semantic_grades` block (no semantic set declared at this stage).

## Reasoning quality: 0.50

What is sound:

- Anchors on the right number: the prior-Term baseline-band reached rate of about 5.1%, read from the committed statpack.
- Identifies the dominant signal correctly. The respondent waived, the Court did not call for a response before distribution, and the Court does not grant a paid petition without a response in hand, so an outright grant at the first conference was structurally very unlikely. This is the correct forward-looking reason to move far below the band anchor, and the one that drove the actual outcome.
- Notes the residual uncertainty honestly (a Justice might ask for a response before denial).

What holds the score down:

- The analysis is thin. It never engages the petition's own account of the decision below, which conceded that the "judge as law-enforcement officer" theory was held forfeited in the district court. Forfeiture is the single largest vehicle problem on this record and goes unmentioned.
- No engagement with the merits posture at all: the claimed four-circuit split is dismissed as "purported" without saying why (the comparators involve judges personally searching or jailing, this judge directed deputies in a pending matter, and Mireles v. Waco sits close to these facts), and the unpublished status of the decision below is not noted.
- It targets "the base rate of 1.2% for paid petitions with 0 relists" as if that were a forward probability. That bucket is a terminal-state cut, the grant rate among petitions that *ended* with zero relists, and it conditions on the petition never being relisted, which was not yet known. The number happens to be reasonable here, but the inference is the wrong shape.
- The retrieval note lists only the CourtListener lookups and the statpack reads; the log also shows two corpus queries that the note omits.

Net: right answer, right anchor, right dominant signal, but a one-paragraph rationale that leaves the legal analysis undone. Middle of the scale.

## Leakage: not applicable

Forward cell. The prediction was created September 16, 2026, before the September 28 conference and the October 5 denial, so no disposition existed to retrieve. I checked the log for a mis-provisioned decided case anyway: the two CourtListener searches on the case's own caption and the two corpus queries carry no `retrieved_doc_date`, every call is `unobserved` (coverage 0.0, an engine shape, so each is graded on its query), and the reasoning predicts denial from the waiver rather than reading it off any source. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case: 0.15

Formed from the record: a doctrinally interesting but narrow judicial-immunity question, a single landlord-tenant contempt dispute, an unpublished forfeiture-based decision below, a waiver, and a first-conference denial with no writing. Legal-press interest at most. The staged prediction.json exposes each candidate's `big_case_score`, so the three scores were visible before this read was fixed; the read rests on the record, not on them.
