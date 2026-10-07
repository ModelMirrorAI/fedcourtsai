# Evaluation of gemini-baseline — scotus/73318742, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
Wain v. Bunnell, No. 25-1271, was distributed once (June 24, 2026, for the
September 28 long conference) and **denied** on October 5, 2026, with no noted
dissent, no CVSG, and no relist.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = 0.0001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, and the committed
  statpack's "Segment base rate by salience band (sal-v4)" table carries the
  same version, so the bracketed `reached` figures apply. Pooled
  resolved-weighted over Terms strictly before the case's Term (2025), that is
  OT2017 through OT2024 (rates 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7 percent
  on denominators 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271; n = 11,580).
  The caption shows 10 of 10 Terms rendered, so the rendered window is the
  pack's window and there is no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² ≈ 0.962.
- `vote_accuracy`: omitted, cert stage.

## Reasoning quality: 0.52

A single paragraph that reaches the right answer on a correct skeleton:
petition against a state judge, absolute judicial immunity, Sixth Circuit
affirmance, no circuit split per the brief in opposition, no federal interest.
It cites the right table and the right band, quoting the prior-Term reached
range (4.5–5.9 percent) rather than pooling a figure, and adjusts downward.

What holds the score down is how little of the record it uses. The brief in
opposition's strongest points are that the suit is official-capacity only and
so independently barred by the Eleventh Amendment and section 1983's
injunction proviso, and that the Caperton-versus-immunity theory was never
raised or decided below. Neither appears here; the analysis rests on
"well-established absolute judicial immunity principles" and labels the
petition "frivolous" and "vexatious" without showing why. The petition is
professionally printed and poses an abstract question Williams v. Pennsylvania
left open, so "frivolous" overstates it, and a reader cannot tell from this
document whether the predictor saw the vehicle defects or just the headline
doctrine. The conclusion is sound; the demonstrated analysis is thin.

## Leakage

Mode `forward`. Prediction created September 16, 2026; the event resolved
October 5, 2026, so no disposition existed to retrieve. The captured log has
`result_capture_coverage` 0.0 — every call `unobserved`, which is this
telemetry's standing shape, so each call is graded on its query. The calls are
reads of the provisioned record, two greps of the statpack, one validate run,
and one corpus query for scotus cases decided before 2026-09-17, which by its
own terms could not return this then-pending petition. No `retrieved_doc_date`
on or after resolution, no query naming this docket's disposition, nothing
under `data/qp-topics/`, and the reasoning reads the snapshot as pending.
`retrieved_outcome_material` false, `influenced_prediction` `not_applicable`,
`leakage_suspected` false.

## Big case

My independent read: 0.08. A pro se official-capacity suit against state judges
arising from a private foreclosure, denied without comment after one
distribution. The abstract doctrinal question has some interest; this vehicle
had none.
