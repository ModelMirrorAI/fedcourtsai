# Evaluation: codex-baseline

## Cell

Cert stage, arrival moment (`evt-petition-arrival-disposition`). Outcome: `denied` on 2026-10-13 after one distribution, `actual_granted` 0, no noted dissent from denial. The prediction froze `context.band` = `baseline` under `sal-v4`, so the segment base rate, the Brier skill score and the basis are stamped by the harness. I left all three null and quote no rate of my own here: the comparison is against the stamped segment base rate. `claim_scores` is the harness's and I did not grade the forecast document or the claims. No semantic set is declared for a cert cell, so there is no `semantic_grades` block. `vote_accuracy` is omitted because this is not a merits cell.

## Scores

- Predicted `denied` at P(grant) = 0.025. `correct` = 1. Brier = 0.025² = 0.000625.

## Reasoning quality: 0.80

This is a careful, well-structured rationale. It names the correct anchor, the private-class baseline reached rate pooled over the displayed strictly prior Terms, and computes it from the committed statpack.json (≈5.02%). It explicitly declines to substitute the terminal relist-zero and CVSG buckets, and it says why. Its legal analysis is sound. It sees that novelty and widespread model legislation do not establish a split. It sees that the alternative certification request highlights an unsettled state-law question. It also notes that the panel opinion (App. A) grounds the decision in Iowa contract and statutory authority, which undercuts the petition's account of simple displacement of state law. It separates its forecast from any view on the merits. The one soft spot is calibration: it lands at half the anchor, while the factors it identifies (a concession of no conflict, a unanimous panel, rehearing denied without dissent, no amici) would support a lower figure. Its upward credit for the Erie framing is generous given its own observation that the panel applied Iowa law. Its reported fetch of Rule 10 text was benign and unproductive.

## Leakage

Forward cell. The prediction was made 2026-09-27, before the 2026-10-13 resolution. The only web activity was four generic searches/opens for Supreme Court Rule 10 text (results unobserved, graded on the query, none case-specific). There was no query for this docket's status. Graded `not_applicable`, not suspected.
