# Evaluation: gemini-baseline

**Outcome:** petition denied on 2026-11-16, with a statement of Justice Thomas respecting the denial. Cert-stage cell (relist moment). The segment base rate and skill are the harness's to stamp.

**Scores:** predicted `denied` at P(grant) = 0.22. `correct` = 1; Brier = (0.22 - 0)^2 = 0.0484. This was the lowest grant probability of the three candidates and the best-calibrated against the outcome.

## Reasoning (`reasoning_quality` 0.82)

The rationale is the strongest of the cell. It starts from the frozen high-band anchor and moves well below it for stated, checkable reasons:

- It decomposed the five distributions into three pre-conference reschedules, one real conference and one real relist, and declined to read the raw count as four relists.
- It found no bottom-line circuit conflict on the challenged locations and tied that to concrete comparators: the Court's choice of the narrow private-property question in Wolford and the denial in Schoenthal (same counsel, public transit) after four distributions.
- It identified the omnibus nine-category question, three categories of which were upheld unanimously below, as a vehicle problem.
- It read the relist as more consistent with a separate writing on denial than with a grant, and named Justice Thomas as the likely writer. That is what happened.

What it got wrong: it put 0.62 on a further distribution, reasoning that a writing takes several conferences to circulate. The Court denied at the first relist conference. The three reschedules, which the candidate itself had flagged, were an available hint that a writing was already in preparation before the 11/6 conference; the rationale did not draw that inference. Figures quoted from the statpack were not re-derived here; the candidate's frozen anchor matches its stamped `cert_anchor`.

## Predicted reasoning (`predicted_reasoning_quality` 0.7)

Central claims, in the document's order of weight: further relists (two to four more conferences), no CVSG, denial, and a writing on denial by Thomas. The denial and the Thomas writing held, and the writing claim was specific and at real risk. The procedural-path claim, which the document leads with, failed outright: no further distribution occurred. The CVSG claim held but carried little risk. The grant-scope and summary-route content was conditional on a grant that did not happen and earns neither credit nor penalty. One central claim failing against two specific ones holding places it a little under the 0.75 anchor.

## Leakage

Forward cell, predicted a week before resolution. Every log row is `outcome_only`, so calls were graded on their queries: provisioned files, related dockets, and Wolford/Koons lookups. Nothing reached this petition's disposition, which did not yet exist. `not_applicable`.

## Note on the writing

The docket styles the writing a "statement respecting the denial"; `outcome.json` records `noted_dissent_from_denial: true`. I graded the forecast documents against the docket text and left the claim scoring to the harness.
