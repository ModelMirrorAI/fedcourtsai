# Evaluation of codex-baseline — scotus/73318742, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
Wain v. Bunnell, No. 25-1271, was distributed once (June 24, 2026, for the
September 28 long conference) and **denied** on October 5, 2026, with no noted
dissent, no CVSG, and no relist.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the version in
  the statpack's "Segment base rate by salience band (sal-v4)" heading, so the
  bracketed `reached` figures apply. Pooled resolved-weighted over OT2017
  through OT2024, the Terms strictly before the case's Term (2025): n = 11,580.
  The caption shows 10 of 10 Terms rendered, so no lookback divergence. The
  candidate's own pooling (approximately 5.12 percent on a denominator of
  11,580) is the same computation.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.990.
- `vote_accuracy`: omitted, cert stage.

## Reasoning quality: 0.84

A careful, well-sourced rationale. It states its information set precisely,
including that the September snapshot's last entry is the June distribution
and that the summer interval is not an observed relist. The anchor is correct
and its derivation is stated as an approximation from rounded cells, which is
honest. The five case-specific adjustments are all borne out by the record:
the petition's own concession that it shows no square conflict (petition pp.
14–15), the gap between the disqualification cases it invokes and the immunity
rule it asks to change, the brief in opposition's non-preservation argument
with the petition's chronology supporting the sequence, the alternative
official-capacity and prospective-relief grounds, and the diffuse factual
presentation. Retrieving Mireles v. Waco to check the judicial-act framework
was a sensible use of the tools and is applied correctly: a dispositive ruling
is facially adjudicative, and allegations about motive and timing do not fit
the two existing exceptions.

It also marks what it could not verify (the parties' conflicting accounts of
the grounds below, read only through advocates) rather than resolving the
conflict by assumption. That is good discipline.

Deductions: the document spends several paragraphs on methodology and on
caveats about the claims block that do not advance the legal analysis of why
this petition fails, and it is less decisive than claude-baseline about which
defect is dispositive. The 0.5 percent figure is slightly better calibrated to
this outcome than 1 percent, but the reasoning supporting it is of similar
strength, and the one-candidate-over-the-other ordering here is on clarity, not
on the number.

## Leakage

Mode `forward`. Prediction created September 16, 2026; the event resolved
October 5, 2026, so no disposition existed to retrieve. The log is mostly
captured (`result_capture_coverage` about 0.93). The two uncaptured rows are
web searches, graded on their queries: one for Mireles v. Waco and one for the
Williams v. Pennsylvania opinion, neither naming this case. The captured
CourtListener calls search for and read Mireles, 502 U.S. 9 (1991), a general
authority; a citation search that returned an unrelated district-court hit was
discarded. No query names this docket or its disposition, no
`retrieved_doc_date` on or after resolution, nothing under `data/qp-topics/`.
`retrieved_outcome_material` false, `influenced_prediction` `not_applicable`,
`leakage_suspected` false.

## Big case

My independent read: 0.08. A pro se official-capacity suit against state judges
arising from a private foreclosure, denied without comment after one
distribution. The abstract doctrinal question has some interest; this vehicle
had none.
