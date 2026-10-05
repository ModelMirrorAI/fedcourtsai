# Evaluation — gemini-baseline — scotus/73500220, evt-petition-disposition

## Outcome and scores

Cert-stage forward cell. The Court denied the petition on 2026-10-05, the first
order list after the 9/28/2026 Long Conference, with no call for a response,
no relist, and no noted dissent (`outcome.json`: `denied`, `actual_granted` 0,
`distribution_count` 1, `noted_dissent_from_denial` false).

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.000001 | (0.001 − 0)² |
| `segment_base_rate` | 0.05121 | sal-v4 `baseline` band, bracketed `reached` figures pooled resolved-weighted over OT2017–OT2024 (593 / 11580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band` `baseline` **and** `salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.9996 | 1 − 0.000001 / (0.05121 − 0)² |
| `reasoning_quality` | 0.35 | below |

The statpack caption renders "Most recent 10 of 10 Term(s)", so the rendered
window is the whole pack and there is no window divergence to flag. The case
Term is 2025, so the pool is every strictly-prior rendered Term with a
baseline row (2017–2024).

## Reasoning quality — 0.35

The rationale is four short paragraphs. It is right about the one thing that
mattered most and says almost nothing else.

What it gets right:

- The government's waiver is correctly identified as the dominant signal, and
  the mechanism is stated accurately: the Court will not grant without a
  response, so a Justice interested in the petition would first have it call
  for one. The petition resolved exactly that way.
- The CVSG point (the United States is already a party, so an invitation is
  structurally inapplicable) is correct.

What is missing or weak, judged as legal analysis rather than as a hit:

- **No base-rate anchor is stated.** The retrieval log shows the predictor
  queried `statpack.json` for the baseline band, but the rationale never says
  what prior it started from or why 0.1% is the right distance below it. The
  prompt's leakage-safe anchor for this band is about 5%; moving to 0.1% is a
  fifty-fold reduction that the text justifies only with "baseline rarity of
  grants in the absence of a response."
- **No engagement with the petition.** The question presented is restated,
  then called "routine" without reading the asserted split (*Farhane*,
  *Bauder*), the Third Circuit's precedential categorical holding, the
  alternative retroactivity ground, or any vehicle fact. The petition's
  substance could have cut either way and the rationale does not look.
- **Overconfidence.** 0.1% leaves essentially no room for the realistic
  non-denial path, a call for response after the Long Conference followed by
  a grant. That path did not materialize, so the Brier rewards the number, but
  a rationale that cannot describe the path it is pricing at near zero is not
  a sound one. Calibration over many such cells would punish this shape.
- `confidence` is null and the stakes rationale is one clause.

The score reflects correct identification of the decisive signal with no
supporting legal analysis and an unexplained anchor. The forecast document and
the claims block are not scored here; the harness scores the claims in code.

## Leakage

Mode `forward` (from the staged log). The prediction was created 2026-09-17
against the 2026-09-17 snapshot; the denial issued 2026-10-05. The log carries
35 calls, every marker-carrying one `unobserved` (`result_capture_coverage`
0.0), which is this engine's standing shape rather than a defect, so each call
is graded on its query. Every query is a local shell or file read of the
prompt, schemas, `event.yaml`, `context.json`, the provisioned snapshot and
QP, and `statpack.json`; there is no web, corpus, or CourtListener call at all,
and no query names a later docket state. The prose contains no outcome
material. The case was genuinely open when predicted, so
`retrieved_outcome_material` is false, `influenced_prediction` is
`not_applicable`, and `leakage_suspected` is false.

## Big case

My independent read is 0.2: the abstract question (the reach of *Padilla*
beyond deportation) has doctrinal significance, but this vehicle is a private
paid petition on collateral review with an independent retroactivity ground,
a government waiver, a first-list denial with no separate writing, and no
amicus or public attention. One process note: the blinded staging puts
`big_case_score` in the same `prediction.json` as the rest of the record, and
I had read that file before forming my own number, so the read was formed
from the record and the outcome rather than strictly in advance of seeing the
predictor's figure.
