# Evaluation of codex-baseline — scotus/73374809, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
October 5, 2026, on first consideration after the September 28 long
conference: one distribution, no CVSG, no noted dissent (`outcome.json`,
`actual_granted` 0).

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.000009 | (0.003 − 0)² |
| `segment_base_rate` | 0.0512 | see below |
| `base_rate_basis` | `risk_set` | frozen `context.band` `baseline` + `context.salience_version` `sal-v4` |
| `brier_skill_score` | 0.9966 | 1 − 0.000009 / (0.0512 − 0)² |
| `reasoning_quality` | 0.82 | see below |

**Base rate.** The prediction's frozen context carries band `baseline` and
salience version `sal-v4`, and the statpack's "Segment base rate by salience
band (sal-v4)" heading matches that version, so the basis is `risk_set`. I
pooled the bracketed `reached` figure for the baseline band, resolved-weighted,
over the rendered Terms strictly before the case's Term 2025 (OT2017–OT2024,
eight rows): 592.9 weighted grants over n = 11,580, which is 5.12%. The table
renders 10 of the pack's 10 Terms, so the rendered window is the pack's window
and there is no lookback divergence to flag. I did not use my own cell's
`record/context.json` band (it is terminal), though it happens to agree.

## Reasoning quality (0.82)

What the rationale (`reasoning.md`) gets right:

- **Correct anchor, correctly scoped.** It pooled the baseline reached rate
  over OT2017–OT2024 and arrived at 5.12%, named it as the private-petitioner
  risk-set figure rather than the terminal or pooled rate, and stated the
  pack's vintage. It also read the relist and CVSG cuts and correctly treated
  them as terminal shape rather than forward hazards.
- **Sound downward adjustment.** The move from 5.1% to 0.3% rests on Rule 10
  grounds that fit this petition: factbound disputes about patients and a USB
  drive, no identified conflict, an unclear link between any federal issue and
  the judgment under review, and a possible state procedural obstacle.
- **Epistemic discipline.** It refused to adopt the petition's medical and
  fiscal assertions, declined to assert an adequate-and-independent state
  ground without the orders, flagged the filing/docketing chronology without
  inferring untimeliness, and disclosed every external fetch (all general Court
  Rules, none case-specific).

What holds it below the top:

- **Under-reads the posture it had.** The petition's own "Opinions Below"
  says the Court of Appeal refused the appeal for lack of the lower-court
  record. The rationale notes a "possible procedural obstacle" but does not
  carry it through to the point that no federal question was decided below,
  which is the single strongest reason this petition could never be granted.
- **Some hedging adds length without information.** Several passages restate
  what was not evaluated or adopted; the forecast is clear enough without them.

The grade is of `reasoning.md` only; the forecast document and claims block
were read for context and are not scored here.

## Leakage

`mode` `forward`; `retrieved_outcome_material` false;
`influenced_prediction` `not_applicable`; `leakage_suspected` false. The
prediction was created September 17, 2026, eighteen days before the denial.
The log's three `web-search` rows are `unobserved` and so graded on their
queries, which name only the Court's Rules page; the two shell fetches that
succeeded pulled the official 2026 Rules PDF. No call names this case outside
the provisioned paths, no `retrieved_doc_date` appears, and nothing under
`data/qp-topics/` was read. The provisioned snapshot (one distribution for the
September 28 conference) shows the case was genuinely open, so the forward
cell was not mis-provisioned.

## Big case

My independent read is 0.02: a pro se licensing dispute with no split, no
federal party, and a denial without comment. The candidate's 0.15 sits higher
than mine, mostly on the tribal-health framing, but it correctly said the
petition does not substantiate it.
