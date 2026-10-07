# Evaluation — claude-baseline

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
*Rio Grande Foundation v. Toulouse Oliver*, No. 25-1248, was **denied** on the
October 5, 2026 order list after the September 28 long conference, with two
distributions on the docket and no noted dissent (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | predicted `denied` against actual `denied` |
| `brier_score` | 0.0196 | (0.14 − 0)² |
| `segment_base_rate` | 0.1722 | sal-v4 `elevated`, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 |
| `base_rate_basis` | `risk_set` | the prediction froze `band` elevated **and** `salience_version` sal-v4; the statpack table heading names sal-v4 |
| `brier_skill_score` | 0.339 | 1 − 0.0196 / 0.1722² |
| `reasoning_quality` | 0.85 | see below |

**Baseline detail.** The prediction's frozen context is band `elevated`,
`salience_version` `sal-v4`, Term 2025. The committed `metrics/statpack.md`
band table is headed `(sal-v4)`, so the version matches and the risk-set
basis applies. The caption says the table renders the most recent 10 of 10
Terms; the Terms strictly before 2025 with a sal-v4 elevated row are
OT2017–OT2024 (eight Terms; the pack holds nothing earlier), so the rendered
window and the in-code ten-Term lookback coincide and there is no window
divergence to flag. Pooling the bracketed figures weighted by their `n`
(17.9/336, 17.5/354, 19.0/300, 20.5/342, 16.1/397, 13.8/334, 15.9/347,
17.5/400) gives 484 weighted grants over 2,810, or 0.1722; the unrounded
`prefix_*` fields in `statpack.json` give 0.172242, which is the figure
recorded. No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: all
are off-stage here (cert votes are elicited but never scored; no semantic set
is declared on a cert event).

## What the prediction got right

The call (deny, 0.14) and the forecast path (a silent denial on the
October 5 order list with no further distribution) both landed exactly. The
probability sits just under the band anchor, which the realized outcome and
the near-zero relist activity vindicate, and the Brier skill of 0.34 beats the
band baseline.

## Reasoning quality (0.85)

This is the strongest analysis of the three, and it is graded on
`reasoning.md` alone. Its merits:

- **Correct anchor, correctly handled.** It pools the sal-v4 elevated
  reached figure over OT2017–OT2024 to 17.2%, exactly the leakage-safe
  cut this cell is scored against, and explains why the relist-count and
  originating-court cuts are shape rather than anchors. It also reads the
  second distribution correctly as a redistribution after a requested
  response, not a post-conference relist.
- **The vehicle analysis is specific and drawn from the briefs.** The
  §(3)(c) construction the petition does not challenge, the panel's
  functional-equivalence suggestion about the Freedom Index, the facial
  posture on a thin chill record, and the arguably unpreserved
  major-purpose argument are all real features of the BIO, and each is the
  kind of defect that produces a denial of an otherwise interesting
  question. The absence of any claimed circuit split is correctly weighted
  as the largest structural fact.
- **The upward signals are weighed rather than counted.** The response
  request is identified as the strongest docket fact but discounted because
  it came at the first distribution before most amici filed, and the amici
  are read as one-sided repeat filers. That is the right calibration, and
  it is what keeps the number from drifting up on attention signals alone.
- **Candid about its evidence quality.** The post-AFPF revealed-preference
  pattern and the NRSC characterization are explicitly flagged as
  memory-based or second-hand, with a direction of error stated for each.

What holds it short of the top of the scale: the revealed-preference claim
(a run of post-AFPF disclosure denials) rests on unverified memory, and the
CourtListener searches that tried to confirm it returned nothing, so one of
the main downward adjustments is asserted rather than shown. The reply brief
was also not read, which the author concedes. Neither flaw changed the
outcome, but a judge grades the support, not just the landing.

## Leakage

Forward cell. The provisioned snapshot was dated 2026-09-17 with the
August 12 distribution as its last entry; the October 5 denial did not yet
exist when the cell ran. The captured log (coverage 1.0) shows CourtListener
reads of the Tenth Circuit opinion (dated 2025-09-09), three zero-hit docket
searches for comparator petitions, an NRSC v. FEC search (2026-06-30) whose
body was unavailable, and two generic corpus queries. Nothing queried this
petition's disposition and no retrieved document is dated on or after
resolution. `retrieved_outcome_material` false,
`influenced_prediction` not_applicable, `leakage_suspected` false. The
candidate's `flags.json` is not staged, so this rests on the log and the
prose rather than on the absence of a disclosure.

## Big-case read

My own read is 0.45: a real but mid-band case whose realized disposition was
a silent denial. The predictor's 0.55 is not graded here; the leaderboard
grades it by rank-agreement.
