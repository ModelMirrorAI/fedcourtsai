# Evaluation — claude-baseline — scotus/73500220, evt-petition-disposition

## Outcome and scores

Cert-stage forward cell. The Court denied the petition on 2026-10-05, the first
order list after the 9/28/2026 Long Conference, with no call for a response,
no relist, and no noted dissent (`outcome.json`: `denied`, `actual_granted` 0,
`distribution_count` 1, `noted_dissent_from_denial` false).

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.0004 | (0.02 − 0)² |
| `segment_base_rate` | 0.05121 | sal-v4 `baseline` band, bracketed `reached` figures pooled resolved-weighted over OT2017–OT2024 (593 / 11580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band` `baseline` **and** `salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.847 | 1 − 0.0004 / (0.05121 − 0)² |
| `reasoning_quality` | 0.82 | below |

The statpack caption renders "Most recent 10 of 10 Term(s)", so the rendered
window is the whole pack and there is no window divergence to flag. The case
Term is 2025, so the pool is every strictly-prior rendered Term with a
baseline row (2017–2024); the unrounded `prefix_*` fields in
`metrics/statpack.json` give 593 weighted grants over 11580 weighted resolved.

## Reasoning quality — 0.82

What the rationale gets right, judged against the outcome and the record:

- **Anchor.** Correctly selects the risk-set (bracketed `reached`) baseline
  figures under the matching `sal-v4` heading, pools the eight strictly-prior
  Terms, and lands on 5.1%, the same number this evaluation pooled. It also
  reads the relist-0, CVSG-none, and CA3 cuts for shape only, which is the
  right use of terminal tables on a forward cell.
- **The decisive factor.** Identifies the United States' waiver as the single
  largest negative and states the mechanism accurately: the Court does not
  grant a paid petition without a response on file, so a grant path runs
  through a call for response first. That is exactly how the petition
  resolved, with no call for response and a first-list denial.
- **Split analysis.** The treatment of the asserted conflict is sound and
  specific. *Farhane* (CA2 en banc 2024) is a denaturalization case the Second
  Circuit tied to deportation; *Bauder* (CA11) is affirmative misadvice; no
  circuit has held failure to warn of civil monetary exposure deficient. That
  is a fair reading of the petition's own survey.
- **Vehicle.** Collateral review posture, denied evidentiary hearing,
  contested facts about what counsel knew, and doubtful prejudice given the
  stipulated loss and the affirmed FCA judgment are real obstacles, and the
  severity/automaticity contrast with deportation is the right doctrinal
  frame.
- **Court's trajectory.** The observation that the Court has repeatedly
  declined *Padilla* extensions since *Chaidez* is an apt prior on this
  question.
- **Candor.** The uncertainty section discloses the CourtListener throttle,
  the truncated petition, and a docket date oddity, and says where the number
  should be discounted.

What holds the score below the top of the range:

- The rationale did not reach the Third Circuit's **alternative
  retroactivity holding** (App. 3: "even if we were to hold otherwise,
  retroactive relief would be unavailable," citing *Edwards v. Vannoy*). That
  is an independent ground supporting the judgment and the strongest vehicle
  problem in the record; the rationale gestures at an "alternative ground"
  only as a fact-bound *Strickland* point. The rationale itself says the
  appendix was not read in full, which is the honest explanation but still a
  gap in the analysis.
- The 2% number is reasonable but leaves the call-for-response path priced
  inside it without saying how much of the 2% it carries; a reader cannot
  tell whether 2% is "waiver, otherwise ordinary" or "waiver, strong vehicle
  problems."

The forecast document and the claims block are not scored here; the harness
scores the claims in code.

## Leakage

Mode `forward` (from the staged log). The prediction was created 2026-09-17
against a 2026-09-17 snapshot whose last entry is the 6/17 distribution for
the 9/28 conference; the denial issued 2026-10-05. The log carries 20 calls,
all captured. The one CourtListener search was throttled and returned nothing;
the one corpus query returned unrelated 2020s granted rows the rationale says
it did not use; no call carries a `retrieved_doc_date`; no query reaches this
docket's later history; the prose nowhere reads the outcome off anything. The
case was genuinely open when predicted, so `retrieved_outcome_material` is
false, `influenced_prediction` is `not_applicable`, and `leakage_suspected` is
false.

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
