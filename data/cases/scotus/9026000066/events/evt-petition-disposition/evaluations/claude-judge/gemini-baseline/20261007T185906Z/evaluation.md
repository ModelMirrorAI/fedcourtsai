# Evaluation — gemini-baseline, scotus/9026000066, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The
petition in *Smith v. Smith*, No. 26-66, was denied on 2026-10-05 after one
distribution for the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`).

| Field | Value |
| --- | --- |
| `predicted_disposition` / `correct` | `denied` / 1 |
| `probability` / `brier_score` | 0.001 / 0.000001 |
| `segment_base_rate` (`risk_set`) | 0.0502 (n = 12,720) |
| `brier_skill_score` | 0.9996 |
| `reasoning_quality` | 0.55 |

**Base rate.** The prediction froze `band: baseline` under `salience_version:
sal-v4`, and the statpack's "Segment base rate by salience band" heading names
sal-v4, so the basis is `risk_set`: the bracketed `reached` figure pooled
resolved-weighted over every rendered Term strictly before 2026 (2017–2025, nine
rows; the caption says 10 of 10 Terms are rendered, so the rendered window and
the in-code ten-Term lookback coincide and there is no window divergence to
flag). Pooled from `metrics/statpack.json`'s `prefix_est_grant_rate` ×
`prefix_weighted_resolved`: 638.0 / 12,720 = 0.05016.

## What the prediction got right and wrong

Right on every scored axis: a clean denial, forecast at 0.1%. The
direction and the magnitude of the downward adjustment from the band rate were
both vindicated.

## Reasoning quality (0.55)

`reasoning.md` is sound but thin. It identifies the right anchor (the baseline
band's reached rate, quoted as "roughly 4–5%" rather than pooled) and the right
reasons to move below it: pro se, state family-law dispute, fact-bound
procedural rulings, no mature split or federal question, the Court's
reluctance to enter domestic-relations matters. Those are the correct
considerations and they are stated accurately.

What holds the score down:

- **The size of the adjustment is asserted, not argued.** Moving from ~5% to
  0.1% is a fifty-fold reduction, and the document gives no account of why
  0.1% rather than 0.5% or 1% — no reference to the statpack's state-court or
  originating-court cuts, no calibration reasoning about residual mass. The
  number happened to score well, but the rationale would support anything
  between 0.1% and 1% equally.
- **It does not engage the docket.** The snapshot's most informative facts —
  no brief in opposition, no waiver, no call for a response, distribution to
  the long conference anyway — go unmentioned. The other two candidates built
  their adjustment on exactly those entries.
- **It does not read the questions presented closely.** Question 1's
  adequate-and-independent-state-ground framing under *Lee v. Kemna* is the
  petition's only non-trivial hook; the document does not identify it or say
  why it fails as a vehicle.
- The `summary-disposition-route` discussion is internally slightly muddled
  ("low because there is no clear intervening decision … though … a summary
  reversal is slightly possible") but that is the claims block, which is
  scored in code and not here.

Nothing is wrong; little is shown. A rationale this short gives a reader no
way to check the adjustment, which is what the score measures.

## Leakage

Mode `forward`; the prediction (2026-10-04) predates the resolution
(2026-10-05). The log holds 24 calls, all provisioned-file reads, the
statpack, the schemas, and the agent's own writes; every call is `unobserved`
(capture coverage 0.0, the engine's standing shape), so each was graded on its
query, and no query names anything outside the provisioned record. `retrieval.md`
says "No retrieval beyond the provisioned inputs." `retrieved_outcome_material:
false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.02: a two-party divorce appeal from an unpublished
state memorandum decision, denied without a writing. Formed from the record
and the outcome before consulting the candidate's own score.

## Not applicable on this cell

No `vote_accuracy` (cert stage; noted votes are never scored), no
`judgment_correct`, no `semantic_grades` (no semantic set is declared on a
cert event and `record/opinion/` is absent, as expected), no `claim_scores`
(harness-computed). The forecast document was read for context only and is
not scored.
