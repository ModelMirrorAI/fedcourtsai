# Evaluation of codex-baseline — scotus/73500219, evt-petition-disposition

## Outcome and scores

Cert-stage cell (event.yaml `stage: cert`). Outcome: petition **denied** on
October 5, 2026 off the single September 28 conference distribution, no
response requested, no relist, no noted dissent (`actual_granted` 0,
`distribution_count` 1).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.06 − 0)² = 0.0036.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band
  `baseline` under `sal-v4`; the statpack's segment table is headed sal-v4, so
  the versions match. Pooled the bracketed `reached` figure for `baseline`
  over every rendered Term strictly before this case's Term 2025: OT2017
  through OT2024 (the caption renders 10 of 10 Terms, so the rendered window
  is the pack window and no divergence arises), resolved-weighted,
  593 / 11,580 ≈ 0.0512.
- `brier_skill_score` = 1 − 0.0036 / 0.0512² = 1 − 0.0036 / 0.00262144 ≈ −0.373.
  Negative: the forecast sat above the baseline on a petition that was denied,
  so it did worse than parroting the band rate.

## Reasoning quality: 0.72

What is sound. The anchor is exactly right: the candidate identified the
sal-v4 match, pooled the risk-set `reached` figure over OT2017–OT2024 from the
unrounded JSON counts, and explicitly refused the terminal-band and
terminal-relist cuts as forward anchors, which is the statpack's own reading
rule. It read the appended Sixth Circuit opinion with care and correctly
reported that the court assumed the most demanding harmlessness burden and
rested on a fact-bound harmlessness finding, which is the right vehicle
diagnosis. It verified the petition's principal contrasting authority
(Dutkel) through CourtListener and drew a measured conclusion from it: the
split is real but the Ninth Circuit rule is a tampering case, so the
petition's camp is less cleanly established than it claims. The document is
candid about its limits (truncated petition, no brief in opposition, failed
web searches, no live docket check) and explains each conditional claim
separately.

What is weaker, given the outcome. The decisive signal on this docket was the
Solicitor General's waiver on June 8 followed by fourteen weeks with no
response request before the long conference. The candidate saw it and called
it "modest negative attention evidence," then still netted *above* the band
anchor (0.06 against 0.0512) on the strength of the split. That ordering of
weights is the error: in a federal criminal case a waived, un-requested
petition sits well below the band mean, and the Court does not grant such a
petition without first calling for a response. The forecast of a 0.18
further-distribution chance was likewise on the high side for that posture.
The analysis is thorough and well-sourced, but its net adjustment ran the
wrong way on the one feature that mattered most.

## Leakage

Mode `forward`, `retrieved_outcome_material` false, `influenced_prediction`
`not_applicable`, `leakage_suspected` false. The prediction (created
2026-09-17) predates the resolution (2026-10-05) by three weeks, so the case
was genuinely open; no mis-provisioning. The log shows two uncaptured web
searches on general doctrine (Olano; Rule 10) that name no party, and two
CourtListener calls on Dutkel only. No call carries a `retrieved_doc_date` on
or after the resolution, no query reaches this docket, and nothing under
`data/qp-topics/` was read. The reasoning treats the event as pending.

## Big case

My independent read is 0.3 (see `big_case.notes`), formed before weighing the
candidate's own 0.45. No agreement figure is computed here.

## Not scored here

The `claims` block and `predicted_reasoning.md` are the harness's; neither
entered `reasoning_quality`. No `semantic_grades` block: a cert cell declares
no semantic set. No `vote_accuracy`: cert-stage votes are never scored.
