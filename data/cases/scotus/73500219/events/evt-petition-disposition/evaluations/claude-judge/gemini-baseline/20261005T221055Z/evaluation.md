# Evaluation of gemini-baseline — scotus/73500219, evt-petition-disposition

## Outcome and scores

Cert-stage cell (event.yaml `stage: cert`). Outcome: petition **denied** on
October 5, 2026 off the single September 28 conference distribution, no
response requested, no relist, no noted dissent (`actual_granted` 0,
`distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.012 − 0)² = 0.000144.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band
  `baseline` under `sal-v4`; the statpack's segment table is headed sal-v4, so
  the versions match. Pooled the bracketed `reached` figure for `baseline`
  over every rendered Term strictly before this case's Term 2025: OT2017
  through OT2024 (the caption renders 10 of 10 Terms, so the rendered window
  is the pack window and no divergence arises), resolved-weighted,
  593 / 11,580 ≈ 0.0512.
- `brier_skill_score` = 1 − 0.000144 / 0.00262144 ≈ 0.945. The lowest
  probability of the three on a denied petition, so the highest skill.

## Reasoning quality: 0.45

The grade is for the soundness of the analysis, not for the number landing
closest, and the two diverge here.

What is sound. The candidate identified the decisive signal, the government's
waiver and the resulting improbability of a grant without a response request,
and reasoned from it directly to a low number. Its structural point that a
CVSG is inapplicable because the United States is already the respondent is
right, and its vehicle concern (a finding of harmlessness could follow even
under the petitioner's standard) is a fair reading of the posture.

Two defects keep the grade down.

First, the anchor is methodologically wrong. The candidate quoted a single
Term's reached rate (OT2024, 5.7%) instead of pooling the prior Terms, then
discarded it in favor of the terminal relist-0 bucket rate (1.2%). That
bucket is the grant rate among petitions that *ended* with no relist, which
conditions on the outcome path; the statpack's own caption and the predict
contract say a forward cell with a frozen band anchors on the risk-set
`reached` figure precisely because a petition at its first distribution can
still climb. Choosing the terminal figure "because the United States waived"
double-counts: it uses the waiver to pick a baseline that already bakes in
the no-relist outcome and then treats the waiver as a further reason for a
low number. The low number was defensible; the route to it was not.

Second, a factual mischaracterization. The reasoning says the Sixth Circuit
"described [the evidence] as overwhelming" and the forecast document repeats
that the court "deemed the government's evidence 'overwhelming.'" The
appended opinion called the evidence "considerable" (Pet. App. 25a–26a); the
word "overwhelming" appears in the government's argument as recited by the
Sixth Circuit, and the petition's point is precisely that the court never
found the evidence overwhelming. Attributing the government's framing to the
court misreads the record the candidate was given, and that misread is what
carries its "exceedingly poor vehicle" conclusion.

The document is also thin: three short paragraphs, no engagement with the
split's structure, no discussion of what was unverifiable, and corpus queries
that failed with no fallback. The direction was right and the key signal was
seen, which is why the grade is not lower.

## Leakage

Mode `forward`, `retrieved_outcome_material` false, `influenced_prediction`
`not_applicable`, `leakage_suspected` false. The prediction (created
2026-09-17) predates the resolution (2026-10-05); no mis-provisioning. The
log's `result_capture_coverage` is 0.0 (every call `unobserved`), the
engine's standing shape rather than a defect, so each call is graded on its
query: provisioned-record reads, two statpack greps, two corpus queries the
candidate reports as failed, and one CourtListener opinion search on Remmer
doctrine naming no party or docket. No query seeks this case's disposition,
no `retrieved_doc_date` is legible, and nothing under `data/qp-topics/` was
read. The reasoning treats the event as pending.

One process note, outside the grade: the log shows the candidate writing two
scratch helper files into `record/documents/` (calls 16 and 17). That is a
write outside the predictor's own path; the files are not in the record now
and nothing about it bears on leakage or on the scores here. It is recorded
in this cell's `flags.json` for a maintainer.

## Big case

My independent read is 0.3 (see `big_case.notes`), formed before weighing the
candidate's own 0.2. No agreement figure is computed here.

## Not scored here

The `claims` block and `predicted_reasoning.md` are the harness's; neither
entered `reasoning_quality`. No `semantic_grades` block: a cert cell declares
no semantic set. No `vote_accuracy`: cert-stage votes are never scored.
