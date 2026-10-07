# Evaluation of claude-baseline — scotus/73318742, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
Wain v. Bunnell, No. 25-1271, was distributed once (June 24, 2026, for the
September 28 long conference) and **denied** on October 5, 2026, with no noted
dissent, no CVSG, and no relist.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = 0.0001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the version in
  the statpack's "Segment base rate by salience band (sal-v4)" heading, so the
  bracketed `reached` figures apply. Pooled resolved-weighted over OT2017
  through OT2024, the Terms strictly before the case's Term (2025): n = 11,580,
  about 593 weighted grants. The caption shows 10 of 10 Terms rendered, so no
  lookback divergence. The candidate's own pooling (about 5.1 percent over the
  same eight rows and the same denominator) matches mine.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² ≈ 0.962.
- `vote_accuracy`: omitted, cert stage.

## Reasoning quality: 0.88

The strongest of the three documents, and the one whose reasons for denial
best match the record. It reads the petition and the brief in opposition
closely and gets the vehicle right: the suit names two state judges in their
official capacities only, so the Sixth Circuit's affirmance rests on Eleventh
Amendment and section 1983 proviso grounds the petition does not contest; the
Caperton-versus-immunity theory was neither pleaded nor decided below; the
petition's own section heading concedes there is no developed split; the
decision below is unpublished; and the serial-litigation posture reads as a
collateral attack on a foreclosure judgment. I checked each of these against
the brief in opposition and they are there as described, including the
Eleventh Amendment, Ex parte Young, declaratory-decree, and futility grounds
and the non-preservation argument.

The anchor work is correct: it identifies the version match, pools the
bracketed reached figures over the right window, and explains why the terminal
figure is the population it expects this petition to end in. The adjustment is
ranked, with the independent alternative ground placed first as the dispositive
defect, which is the right order. It also states the honest counterweight (a
real open question, a concrete campaign-finance allegation) and why it does not
survive the vehicle problems. The limitations section is candid about not
having read the Sixth Circuit opinion directly and about the Brier cost at the
floor.

Small deductions: the document is somewhat long for what it decides, and the
"Other claims" discussion is a forecast of the claims block rather than
support for the headline number (that block is scored elsewhere and I have not
weighed it here).

## Leakage

Mode `forward`. Prediction created September 16, 2026; the event resolved
October 5, 2026, so no disposition existed to retrieve. The log is fully
captured (`result_capture_coverage` 1.0). Beyond provisioned-record and
statpack reads, it shows one corpus query rejected by the CLI (an unsupported
`--text` option, no ranged read) and two CourtListener opinion searches for
the Sixth Circuit decision below, No. 25-5722, both disclosed in `retrieval.md`
as returning zero hits. The decision below predates the petition and is not
outcome material for this event. No `retrieved_doc_date` on or after
resolution, no query naming this petition's disposition, nothing under
`data/qp-topics/`. `retrieved_outcome_material` false, `influenced_prediction`
`not_applicable`, `leakage_suspected` false.

## Big case

My independent read: 0.08. A pro se official-capacity suit against state judges
arising from a private foreclosure, denied without comment after one
distribution. The abstract doctrinal question has some interest; this vehicle
had none.
