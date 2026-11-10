# Evaluation — codex-baseline, scotus/9026000462 (Hauber v. Honkamp Krueger & Co.), evt-petition-disposition

**Stage:** cert (forward, `moment: distribution`). **Outcome:** denied 2026-11-09, no noted dissent, no CVSG, two distributions.

## Scores
- Predicted `denied` at P(grant) = 0.03 → `correct` = 1, `brier_score` = 0.0009.
- `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left for the harness stamp; I quote no rate of my own. Votes are not scored on a cert cell.

## Reasoning quality — 0.75
The rationale is careful and transparent. It pools the correct anchor: the bracketed baseline `reached` rate over prior Terms from the statpack JSON. It is explicit about what the record could not show, since the petition text was empty and there was no QP and no BIO. Like claude-baseline, it correctly reads the Sep 9 distribution as the sealing motion's, and it flags that. Its weakness is that it makes only a timid adjustment down, to 3%, mainly because the petition text was missing. The record it did have was a pro se paid petitioner, a waiver, and an Eighth Circuit affirmance on a discovery sanction. Those observable features all point strongly toward the bottom of the band, and the rationale weighs them as "modest". The epistemic humility is principled, but it leaves the probability less sharp than the available evidence supported. Declining to give a `big_case_score` for lack of the QP was defensible but overcautious.

## Predicted reasoning — 0.6
Central claims: (1) a denial without writing, in November or December, which held; (2) one additional distribution and then denial, with nothing further, which held: Oct 14 distribution, denied Nov 9; (3) no CVSG and no requested BIO, which held; (4) the conditional plenary-over-summary call, which stays unresolved. The distribution call is the document's one discriminating, specific claim, and it was right. Everything else is close to the default for any pro se paid petition, and the timing window is broad. The document declines to name any question. It is correct and partly specific but mostly generic, so it sits a little above the 0.5 anchor.

## Leakage
Forward. The prediction was made 2026-10-08 and the denial issued 2026-11-09. Result capture is 0.96. The one uncaptured call fetched the petition PDF URL listed in `documents.json`, a pre-decision filing, and I graded it on its query. A CourtListener search was restricted to the Eighth Circuit opinion filed before 2026-03-24. There is no disposition query and no `qp-topics` read. Graded `not_applicable`, so `leakage_suspected` = false.

## Semantic grades
Cert cell: no semantic set is declared, so none was written.
