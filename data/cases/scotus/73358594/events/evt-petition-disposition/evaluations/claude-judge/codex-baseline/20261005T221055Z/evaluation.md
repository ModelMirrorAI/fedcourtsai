# Evaluation of codex-baseline — scotus/73358594, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition
(No. 25-1289, Bolanos-Reynoso v. Department of Agriculture, Federal Circuit)
was **denied** on 2026-10-05 after its first conference of 2026-09-28, with no
noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`,
`distribution_count: 1`, `noted_dissent_from_denial: false`).

- `predicted_disposition: denied` → `correct = 1`.
- `probability = 0.015` → `brier_score = (0.015 − 0)² = 0.000225`.
- `segment_base_rate = 0.051203`, basis `risk_set`: the prediction's frozen
  context carries `band: baseline` and `salience_version: sal-v4`, and the
  statpack's "Segment base rate by salience band (sal-v4)" heading matches.
  I pooled the bracketed `reached` figure for the baseline band,
  resolved-weighted by its `n`, over every rendered Term strictly before the
  case's Term 2025: OT2017–OT2024 (5.7/1271, 5.9/1312, 5.8/1192, 5.6/1500,
  4.5/1739, 4.6/1399, 4.6/1524, 4.7/1643), giving ≈592.9 grants over
  n = 11,580 → 5.12%. The caption renders 10 of 10 Terms, so the rendered
  window is the pack's whole window and nothing earlier than OT2017 exists for
  the configured 10-Term lookback to reach; no window divergence to flag.
- `brier_skill_score = 1 − 0.000225 / 0.051203² = 0.914`.
- No `vote_accuracy` (cert cell); no `semantic_grades` (no semantic set on a
  cert event, and the prediction's `semantic_claims` is null); `claim_scores`
  left to the harness.

## Reasoning quality: 0.82

What drove the score up:

- **Correct anchor, correctly derived.** It uses the sal-v4 bracketed
  *reached* baseline rate, pools OT2017–OT2024 weighted by the displayed
  denominators (5.12%, n = 11,580 — the same figure I compute), keys the Term
  on the frozen context rather than the conference date, and explicitly
  declines to substitute the paid-segment terminal relist-0 cut or the
  originating-circuit cut for the reached anchor, naming them as population
  shape rather than independent likelihood ratios. That is the right reading
  of the pack.
- **The downward case is well specified.** Vehicle and certworthiness, not
  importance: a Federal Circuit Rule 36 affirmance with no precedential rule
  to review; the petition's own distinction between a failure to analyze and
  an erroneous interpretation (p. 20), which it correctly reads as making the
  ask look like record-specific error correction; the government's waiver
  followed by distribution with no call for a response; and the
  record-dependent obstacles (the Board's independent would-have-demoted-anyway
  analysis, preservation, harmlessness) that it declines to resolve in the
  petitioner's favor.
- **It checked the cited analogy.** It retrieved *Flynn v. SEC*, 877 F.3d 200
  (4th Cir. 2017) via CourtListener and read the § 1201.111(b) passage,
  concluding accurately that it supports the petitioner's proposed remedy but
  establishes no square conflict with a Rule 36 affirmance. It also declines
  to count *Delgado* as a verified split without having read it.
- **Honest limits.** Truncated petition text, unread administrative appendix,
  no claim to a preservation audit, and a stated uncertainty about the pack's
  vintage.

What held it back:

- The 1.5% lands above the two other candidates on a petition where the
  signals it itself identified (SG waiver, no CFR, Rule 36, no split, first
  conference) are the strongest routine-denial configuration on the paid
  docket. Its own analysis supports a somewhat sharper adjustment; the result
  is a defensible judgment call, not an error, and the extra Brier cost is
  small.
- A fair amount of the document is process narration (CLI cache retry, which
  files were read, which web attempts failed) that does not bear on the legal
  analysis.
- It says the event "has no explicit stage or moment"; the event file carries
  both. Harmless here since it applied the cert default correctly, but a
  misreading of the input it was given.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`;
`influenced_prediction: not_applicable`; `leakage_suspected: false`. The
prediction was created 2026-09-16 against a snapshot of the same date whose
last entry is the June 17 distribution, and the denial came 2026-10-05. The
captured log (31 calls, capture coverage 0.94) shows no query naming this
petition, caption, or docket number, no `retrieved_doc_date` at or after
resolution, and no `data/qp-topics/` read. The two unobserved web-search rows
are generic Rule 10 / Rules-of-Court queries and are graded on their queries.
The reasoning states the predictor did not know the outcome. Not a
mis-provisioned decided case.

## Big case

My independent read is 0.10 (recorded in `big_case.notes`): a single
employee's WPA reprisal appeal from a nonprecedential affirmance, no split,
SG waiver, denied without comment. The candidate's 0.28 is the highest of the
three; its rationale credits the abstract reach of a complete-adjudication
rule across the federal workforce, which is a fair observation but weighs the
question's potential over the vehicle's actual stakes.
