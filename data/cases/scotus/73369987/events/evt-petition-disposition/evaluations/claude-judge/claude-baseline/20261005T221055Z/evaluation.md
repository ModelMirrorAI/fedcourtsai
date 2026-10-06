# Evaluation of claude-baseline — scotus/73369987, evt-petition-disposition

## Outcome and scores

The petition (No. 25-1296, Robinson v. Freeman) was distributed once, for the
September 28, 2026 long conference, and denied on October 5, 2026 with no
noted dissent and no response ever called for. Cert stage, `cert` on the event.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.004 − 0)² = 0.000016.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction
  froze `band: baseline` with `salience_version: sal-v4`, and the statpack's
  segment table heading is `sal-v4`, so the bracketed `reached` figures apply.
  Pooled resolved-weighted over the rendered Terms strictly before 2025
  (OT2017–OT2024, n = 11,580; the table renders all 10 Terms the pack holds,
  so the rendered window is the in-code window and nothing diverges): 0.0512.
- `brier_skill_score` = 1 − 0.000016 / 0.0512² ≈ 0.9939.

## Reasoning quality: 0.88

The strongest of the three analyses. The anchor is right and the version check
is explicit: the candidate pooled the bracketed baseline figures over
OT2017–OT2024 and arrived at the same 5.1% I compute. Every downward adjustment
names a real feature of the record and explains why it matters to a cert
decision: pro se petitioner; a facial vagueness attack on the universal
best-interests standard with no split (and the petition's own "all 50 states"
point correctly read as cutting against a conflict); a plausible adequate and
independent state ground in the C.R.C.P. 7(b)(1) particularity ruling plus the
appellate court's undeveloped-argument alternative; an unpublished decision;
the elder child aging out; and the petitioner's two earlier denied petitions
from the same custody dispute. The no-response point is correctly stated as a
sequencing fact (the Court does not grant without first calling for a
response), not as a signal. The stated floor rationale for 0.004 (tail
overconfidence under a proper scoring rule) is sound.

The uncertainty section is honest and specific: it says the state-ground
reading rests on the petitioner's own account, that the corpus query returned
nothing comparable, and that CourtListener held no rows for the prior
petitions, so the repeat-petitioner point is taken from the petition itself.

What keeps it below the top: "half the controversy is moot" overstates what
one child aging out does to a parenting-time dispute over the other, and the
three-month filing-to-docketing gap is noted but not resolved. Neither moves
the number. The forecast document and the claims block were read for context
only and are not scored here.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`; the prediction was written on
September 17, 2026, eleven days before the conference and eighteen before the
denial. All 19 calls are captured. The only dated retrieval is the corpus
query on 2026-09-17, pre-resolution and, by the candidate's account, unrelated
to this petition. The three CourtListener docket searches targeted the two
prior petitions and the petitioner's name, returned nothing, and were an
attempt to confirm pre-snapshot history, not this event's outcome. No call
reaches this petition's disposition, no `retrieved_doc_date` is on or after
2026-10-05, and nothing touches `data/qp-topics/`. The reasoning states the
outcome was unknown. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The
case was genuinely open when provisioned, so this is not a mis-routed decided
case.

## Big case: 0.05 (my independent read, formed before reading the candidate's)

A pro se challenge to Colorado's parenting-time factors, unpublished below, no
response, no amicus, denied without comment. The abstract question would be
large if ever decided; this vehicle decided nothing and drew no attention.
