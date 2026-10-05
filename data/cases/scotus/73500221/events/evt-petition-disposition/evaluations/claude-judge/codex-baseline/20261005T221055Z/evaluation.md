# Evaluation: codex-baseline — scotus/73500221, evt-petition-disposition

## Outcome and scoring

The petition (No. 25-1320, *Rogne v. City of Catoosa*) was **denied** on the
October 5, 2026 order list following the September 28 long conference, after one
distribution, with no response requested, no CVSG, and no noted dissent.

- **Cell:** cert stage, forward mode (prediction created 2026-09-17 against the
  2026-09-17 snapshot).
- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.000144.** P(grant) 0.012 against `actual_granted` 0.
- **segment_base_rate = 0.0512, basis `risk_set`.** Frozen `band: baseline`
  under `sal-v4`, matching the statpack heading. Bracketed `reached` figures
  pooled resolved-weighted over OT2017–OT2024 (the rendered Terms strictly before
  Term 2025; the caption renders 10 of 10 Terms, so no lookback divergence):
  about 593 / 11,580 = 5.12%. The candidate computed the same pool from the
  pack's exact prefix fields and quoted 5.1209%, which agrees with mine.
- **brier_skill_score = 0.9451.**
- **vote_accuracy** omitted (cert stage). No `semantic_grades` block (cert
  event). `claim_scores` left to the harness.

## Reasoning quality: 0.88

The most evidence-grounded of the three rationales.

Strengths:

- **It read the lower-court order.** The candidate fetched the petition's own
  appendix (filed May 18, 2026, linked from the provisioned snapshot) and read
  the Tenth Circuit's order from it: expressly nonprecedential, affirmance on
  limitations grounds, the contested savings-statute element being whether the
  earlier state action failed "otherwise than on the merits," and the panel's
  reading of the state appellate decision as a merits rejection of the damages
  claim rather than a mootness dismissal. That is the single fact that settles
  the vehicle question, and the other candidates inferred it from the petition.
- **The inference drawn from it is right and carefully stated:** the immediate
  obstacle is the effect of a completed state adjudication under a state savings
  provision, not a fresh exhaustion requirement of the kind *Knick* removed, so
  the Court would have to untangle a particular record before reaching the
  constitutional framing. It also notes that calling the earlier decision wrong
  does not make it non-merits.
- **Correct anchor, with the basis choice explained.** It uses the bracketed
  reached figure over OT2017–OT2024, computes it exactly (593 / 11,580), and
  says why the terminal figure would be the wrong conditioning. It flags that
  the counts are weighted risk-set estimates rather than independent draws.
- **Epistemic hygiene.** It separates the petitioner's allegations from
  established findings, states that the band is retained from the frozen context
  rather than re-derived, describes what each failed retrieval did and did not
  contribute, and says plainly that it holds no outcome knowledge.

Weaknesses:

- Some of the document is spent on matters that do not bear on the number
  (corpus-freshness disclaimers, the pack's missing build timestamp,
  administrative notes). It is careful rather than wasteful, but a reader has to
  work to find the analysis.
- A few hedges are so broad they carry no information ("I am not claiming that
  no split exists anywhere").
- The appendix review was selective (pages 1a–4a and 14a–21a), which the
  candidate discloses; the parts read were the dispositive ones.

## Leakage

Forward cell, `influenced_prediction = not_applicable`, `leakage_suspected =
false`, `retrieved_outcome_material = false`. The 35-call log (coverage 0.91)
shows provisioned-file and statpack reads; three `web-search` rows marked
`unobserved` and graded on their queries (a *Knick* opinion lookup and two
supremecourt.gov PDF URLs, one being this petition's appendix); a CourtListener
`ca10` search bounded `filed_before 2026-02-18`; and a direct fetch of the
May 18, 2026 appendix PDF read in memory. All of it is pre-petition lower-court
material dated months before the resolution, and each fetch is disclosed in
`retrieval.md`. Nothing dated at or after the resolution, no `data/qp-topics/`
read. Not a mis-provisioned decided case.

## Big case

My independent read is 0.08 (see `big_case.notes`). The predictors'
`big_case_score` values were visible in the staged `prediction.json` before I
wrote mine; noted rather than claimed as a blind read.
