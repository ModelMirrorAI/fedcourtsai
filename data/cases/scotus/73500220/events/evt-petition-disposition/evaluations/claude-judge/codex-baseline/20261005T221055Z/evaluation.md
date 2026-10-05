# Evaluation — codex-baseline — scotus/73500220, evt-petition-disposition

## Outcome and scores

Cert-stage forward cell. The Court denied the petition on 2026-10-05, the first
order list after the 9/28/2026 Long Conference, with no call for a response,
no relist, and no noted dissent (`outcome.json`: `denied`, `actual_granted` 0,
`distribution_count` 1, `noted_dissent_from_denial` false).

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.000225 | (0.015 − 0)² |
| `segment_base_rate` | 0.05121 | sal-v4 `baseline` band, bracketed `reached` figures pooled resolved-weighted over OT2017–OT2024 (593 / 11580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band` `baseline` **and** `salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.914 | 1 − 0.000225 / (0.05121 − 0)² |
| `reasoning_quality` | 0.88 | below |

The statpack caption renders "Most recent 10 of 10 Term(s)", so the rendered
window is the whole pack and there is no window divergence to flag. The case
Term is 2025, so the pool is every strictly-prior rendered Term with a
baseline row (2017–2024). The predictor's own pooled figure (593 / 11580 =
5.1209%) is the same number this evaluation pooled from the same unrounded
`prefix_*` fields.

## Reasoning quality — 0.88

The strongest rationale of the three, because its vehicle analysis is read off
the appellate opinion in the appendix rather than off the petition's framing.

What it gets right:

- **Anchor.** Correctly selects the risk-set baseline under the matching
  `sal-v4` heading, pools only strictly-prior rendered Terms, uses the
  unrounded pack figures, and explicitly declines the terminal percentages and
  the later Term rows. It also states the pack's commit vintage and that it
  cannot assert corpus freshness, which is the right epistemic posture.
- **The waiver and posture.** Reads the June 11 waiver, the single
  distribution for a still-future conference, and the absence of any BIO or
  amicus correctly, and does not mistake the summer interval for Court
  attention.
- **Split.** Treats the petition's conflict section as advocacy: *Farhane*
  is tied to deportation and the affirmative-misadvice cases are a different
  doctrine, so there is no square conflict on failure to warn of FCA
  exposure. That matches the record.
- **Vehicle, verified against the appendix.** The three problems are the
  real ones, and each checks out in the staged petition text: the Third
  Circuit's independent holding that "even if we were to hold otherwise,
  retroactive relief would be unavailable" under *Edwards v. Vannoy* (App.
  3), with the new-rule discussion at App. 14–16; the footnote that the
  petitioners lose even under a broader *Padilla* reading because FCA
  liability is not comparable to deportation; and the unresolved advice and
  prejudice facts with the evidentiary-hearing issue left unreached. The
  rationale verified the *Chaidez* new-rule distinction on CourtListener
  rather than from memory, and the log shows that lookup.
- **Candor.** Discloses the truncated petition, the docket date conflict, the
  failed general-precedent web lookups, and that no disposition lookup was
  attempted.

What holds it just below the top:

- The move from 5.12% to 1.5% is labeled "a judgmental adjustment, not a
  fitted model," which is honest, but the rationale does not say how the
  waiver and the three vehicle problems divide the reduction, so the number
  is well supported in direction and only loosely in magnitude.
- The rationale is slightly over-reliant on the appellate account of the
  plea-advice facts (App. 6–7) without noting that the petition disputes
  that account; it flags the facts as contested, which is enough, but the
  tension is not drawn out.

The forecast document and the claims block are not scored here; the harness
scores the claims in code.

## Leakage

Mode `forward` (from the staged log). The prediction was created 2026-09-17
against the 2026-09-17 snapshot; the denial issued 2026-10-05. The log carries
35 calls with `result_capture_coverage` 0.886. The four `unobserved` rows are
web searches whose queries are general-precedent lookups for *Padilla* and
*Chaidez* (supremecourt.gov and Cornell PDF URLs) naming no target docket, so
graded on query they retrieve nothing about this case. The two captured
CourtListener calls look up 568 U.S. 342 and search that opinion for "new
rule." No call carries a `retrieved_doc_date`, no query reaches this docket's
later history, and the prose states that no disposition lookup was attempted,
which the log bears out. The case was genuinely open when predicted, so
`retrieved_outcome_material` is false, `influenced_prediction` is
`not_applicable`, and `leakage_suspected` is false.

## Big case

My independent read is 0.2: the abstract question (the reach of *Padilla*
beyond deportation) has doctrinal significance, but this vehicle is a private
paid petition on collateral review with an independent retroactivity ground,
a government waiver, a first-list denial with no separate writing, and no
amicus or public attention. One process note: the blinded staging puts
`big_case_score` in the same `prediction.json` as the rest of the record, and
I had read that file before forming my own number, so the read was formed
from the record and the outcome rather than strictly in advance of seeing the
predictor's figure.
