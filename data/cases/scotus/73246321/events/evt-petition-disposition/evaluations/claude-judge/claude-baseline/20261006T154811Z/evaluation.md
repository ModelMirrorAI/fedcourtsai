# Evaluation: claude-baseline — Francis v. Allstate Insurance Co. (scotus/73246321, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list
after the September 28 Long Conference, on a single distribution, with no noted
dissent (`actual_disposition: denied`, `actual_granted: 0`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band
  `baseline` under `sal-v4`, and the statpack's per-Term table carries the same
  version in its heading, so the bracketed `reached` figure applies. Pooled
  resolved-weighted over the rendered Terms strictly before the case's Term
  2025 — OT2017–OT2024, eight rows, n = 11,580 — the rate is 5.12%. The
  caption renders 10 of 10 Terms, so the rendered window is the pack's whole
  window and no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.990.

No votes are scored on a cert cell; `vote_accuracy` is omitted. No semantic
set is declared on a cert event, so there is no `semantic_grades` block.

## Reasoning quality: 0.88

The rationale is the strongest of the three on legal substance and the most
disciplined on method.

What it got right:

- **Anchor handled exactly as the contract asks.** It matched the frozen band
  and version to the statpack heading, pooled the eight prior-Term `reached`
  rows to 5.1% over n = 11,580 (the same figure I compute), showed the
  terminal figure beside it to explain why it is not the one scored, and said
  plainly why the risk-set population (which includes counseled petitions that
  later climbed bands) overstates this petition's chances.
- **Doctrinally correct frame.** The dispositive point is that the judgment
  below is a state appellate court's enforcement of its own filing deadlines —
  an adequate and independent state ground — and that the petition neither
  alleges inconsistent application nor shows the federal question was raised
  below. That is the right reason this petition could not be granted, and the
  rationale states it directly rather than resting on pro se status alone.
- **Reads the petition, not just its category.** It notes the argument section
  is two paragraphs citing one case, alleges no split, and that the three
  questions are generalized policy grievances. It also closes the GVR route
  explicitly (no intervening decision), which is the one grant path a weak
  petition can take.
- **Calibration reasoning.** It explains why it does not go below 0.5%: the
  occasional surprise hold or GVR, and a proper score not rewarding a zero it
  cannot justify. That is sound.
- **Honest caveats.** OCR garbling, the cover-page/docket inconsistency about
  the court below, the odd "filed Oct 14 2025 / docketed Apr 24 2026" dates,
  and the unprovisioned appendix are each named with their likely effect on
  the number.

Where I discount:

- "The Court does not review a state court's enforcement of its own filing
  deadlines" is stated more absolutely than the adequacy doctrine warrants; the
  following clause (no inconsistent-application argument) rescues it, but the
  rule should have been stated as a presumption with its exception.
- The characterization of the judgment below rests on the petition's own
  statement of the case, which the rationale acknowledges; the lower-court
  orders were not provisioned, so the AISG point is well-founded but not
  verified against the orders.
- The "roughly a quarter" relist figure it cites is consistent with the
  statpack's paid scored-segment relist table (about 25% with one or more
  additional distribution entries), so no deduction there.

The forecast document and the claims block were read for context only and are
not scored here.

## Leakage: not applicable (forward)

The prediction was created 2026-09-16, before the September 28 conference, so
the outcome did not exist to be retrieved. The captured log (21 calls, full
result capture) shows provisioned inputs, schemas, the statpack, and one corpus
query over the general denied population whose legible document date
(2026-09-10) precedes resolution and does not concern this case. The log also
shows a listing of the event's `predictions/` tree (directory names only); the
rationale states the earlier run was not read, and in any case that tree held
no outcome. No external call names this docket, nothing under `data/qp-topics/`
was read, and the reasoning does not presuppose the result.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false.

## Big-case read: 0.02

An individual's insurance dispute lost on a Georgia procedural default, pro se,
respondent waived, denied on the first conference with no separate writing.
Nothing here reaches beyond the parties. (The predictors' own scores were
visible in the staged `prediction.json` before I recorded this; the read is
mine, but I note the exposure.)
