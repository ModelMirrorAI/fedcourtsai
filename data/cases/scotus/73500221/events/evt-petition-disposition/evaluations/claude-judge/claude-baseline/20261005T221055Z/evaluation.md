# Evaluation: claude-baseline — scotus/73500221, evt-petition-disposition

## Outcome and scoring

The petition (No. 25-1320, *Rogne v. City of Catoosa*) was **denied** on the
October 5, 2026 order list following the September 28 long conference, after one
distribution, with no response requested, no CVSG, and no noted dissent.

- **Cell:** cert stage, forward mode (prediction created 2026-09-17 against the
  2026-09-17 snapshot).
- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.0001.** P(grant) 0.01 against `actual_granted` 0.
- **segment_base_rate = 0.0512, basis `risk_set`.** Frozen `band: baseline`
  under `sal-v4`, matching the statpack heading. Bracketed `reached` figures
  pooled resolved-weighted over OT2017–OT2024 (the rendered Terms strictly before
  Term 2025; the caption renders 10 of 10 Terms, so no lookback divergence):
  about 593 / 11,580 = 5.12%.
- **brier_skill_score = 0.9619.**
- **vote_accuracy** omitted (cert stage). No `semantic_grades` block (cert
  event). `claim_scores` left to the harness.

## Reasoning quality: 0.85

A well-constructed rationale that reads like a cert-pool memo.

Strengths:

- **Correct anchor, correctly derived.** It names the band, checks that the
  table's version matches the frozen `sal-v4`, pools the bracketed figure over
  OT2017–OT2024, and quotes the per-Term range (4.5%–5.9%) and the pooled
  denominator (~11,600). This is exactly the figure the cell is scored against,
  and the document says so.
- **The dispositive question is identified precisely.** It locates the real
  issue as whether the Oklahoma Court of Civil Appeals' judgment was "on the
  merits" for purposes of 12 O.S. § 100, a state-law question the Court does not
  grant to review, and notes the petition's own Section IV concedes tolling is a
  state-law matter. That is sharper than a generic "preclusion" label.
- **Every downward signal is enumerated and weighed:** no split claimed, state-law
  question, unpublished order below, waiver of response, tangled record, solo
  counsel with no amicus. It also states the one upward consideration (the
  Court's post-*Knick* receptiveness to physical-occupation takings narratives)
  and explains why that keeps the number at 1% rather than lower.
- **Cross-check against a second population.** It compares against the
  relist-0 terminal bucket (~1.7% grant family) and explains why this petition
  is weaker than that bucket's typical member.
- **Honest about degraded retrieval.** Both CourtListener lookups were throttled
  (HTTP 429); the document says so, says what consequently was not checked (the
  Tenth Circuit order itself, the live docket), and says which numbers that
  uncertainty touches.

Weaknesses:

- The Tenth Circuit's order was not read, so the characterization of its ground
  rests on the petition's account and the appendix listing. The document
  discloses this, which limits the cost, but a candidate that read the order had
  firmer footing.
- The relist-increment and summary-route discussion is more speculative than
  the disposition analysis (those claims are scored in code, not here; the point
  is only that the justification is thinner in that section).

## Leakage

Forward cell, `influenced_prediction = not_applicable`, `leakage_suspected =
false`, `retrieved_outcome_material = false`. The 27-call log is fully captured
(coverage 1.0): provisioned-file reads, two population-shape corpus queries (one
legible `retrieved_doc_date` of 2025-02-11 on an unrelated row), and two caption
searches on CourtListener that returned `throttled`. Nothing dated at or after
the resolution, no `data/qp-topics/` read, and the prose states the conference
had not yet occurred. Not a mis-provisioned decided case.

## Big case

My independent read is 0.08 (see `big_case.notes`). The predictors'
`big_case_score` values were visible in the staged `prediction.json` before I
wrote mine; noted rather than claimed as a blind read.
