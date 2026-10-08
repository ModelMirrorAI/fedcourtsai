# Evaluation — claude-baseline — Scroggins v. City of Shreveport, No. 26-80 (arrival disposition)

## The cell

Cert stage, arrival moment, forward mode. Outcome: petition **denied** on 2026-10-05 after
one distribution (conference of 9/28/2026), no CVSG, no noted dissent, respondent's response
waived 2026-08-06. The staged opinion slot is absent, the ordinary state for a cert cell; no
semantic set is declared on a cert event, so no `semantic_grades` block is written.

## Scores

| field | value | basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.000016 | (0.004 − 0)² |
| `segment_base_rate` | null | version mismatch, below |
| `brier_skill_score` | null | follows the omitted rate |
| `base_rate_basis` | null | follows the omitted rate |
| `reasoning_quality` | 0.88 | below |

**Why the rate and skill are omitted.** The prediction froze `context.band = baseline` under
`context.salience_version = sal-v3`; the committed `metrics/statpack.md` band table is headed
**sal-v4**. The evaluate prompt's rule for that mismatch is to omit `segment_base_rate` and
`brier_skill_score`, leave `base_rate_basis` null, and flag it (`flags.json`,
`data-quality`). For information only, not written into the JSON: `fedcourts
segment-anchors --term 2026 --salience-version sal-v3` prints the version-pinned baseline
risk-set pool at 5.02% (n=12720, OT2017–OT2025), identical under sal-v4, as
`docs/salience.md` says it is after the `dist-v2` rebuild. The candidate's own anchor
(≈6.5%, n≈13,163) was the pre-rebuild sal-v3 pool and no longer matches any rendered table.
This is a fact about the pack, not about the forecast.

## What the prediction got right

- Direction, shape and timing. Denied, one distribution, no relist, no CVSG, no writing:
  the forecast document (context only, not scored) even placed the conference at "the
  late-September 2026 long conference", which is where it landed (9/28/2026).
- The anchor is handled with unusual discipline: it names the band, checks that the frozen
  salience version matched the table heading **at prediction time**, takes the bracketed
  `reached` figure, and pools strictly over prior Terms. It then cross-checks the landing
  point against a second surface (the relist-0 bucket's grant-family rate) rather than
  discounting in the dark.
- The four discounts are each tied to a record fact and each is the right one: pro se filer
  on a paid docket; all three questions are error correction with no split alleged; the
  response was waived, so a grant would first require a call for a response, which the docket
  showed no sign of; and the vehicle is thin, with the rationale catching the petition's own
  *Tolan* reporter-citation error (512 vs 572 U.S. 650). That last point is the kind of
  record-level detail that separates reading the petition from summarizing it.
- The one upward factor, the published panel dissent, is weighed rather than waved at, and
  the candidate says plainly that it could not verify it (CourtListener's stored text for
  the cluster was an unrelated case) and so took the petition's description at a discount.
- The `relist-increment` claim is read correctly from a zero-distribution state as
  P(ever distributed), with a stated residual for pre-distribution attrition. The claims
  block is scored in code and not graded here; the point is the reasoning understood the
  quantity.
- The uncertainty section says which single fact would move the number and in which
  direction, and notes the corpus citation query's empty result as a coverage gap rather
  than as evidence.

## What held the score down

- "The Court essentially never grants plenary review on a pro se petition" is stated as a
  near-rule without a source. It is directionally right for paid pro se petitions, but a
  rationale this careful elsewhere should have marked it as an impression rather than a
  fact, especially since the same document relies on it for the largest single discount.
- The 15-fold discount from the anchor is asserted as "consistent with" the relist-0 rate
  "further discounted", but the arithmetic from ~1.7% to 0.4% is not shown. The landing
  point is defensible; the step is not fully argued.
- Minor: the document says the response waiver means the grant path "requires a CFR first",
  which is right, but then does not fold the small probability of a CFR into the number
  explicitly; the reader infers it from the residual.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
not_applicable; `leakage_suspected` false. The log carries 28 captured calls (coverage
1.0): provisioned-file reads, statpack greps, one corpus citation query returning no rows,
one CourtListener search returning the Fifth Circuit opinion below (`retrieved_doc_date`
2025-10-17, pre-event) and one `read_document` that returned mismatched text. Nothing
touches `data/qp-topics/` or reaches past the event date. The case was open on 2026-08-16
(first distribution 2026-08-19, denial 2026-10-05), so the forward default stands after
checking.

## Big case

My independent read is 0.03: a single-plaintiff promotion dispute against one city, pure
error correction, waived response, denied without comment. (The predictor's `big_case_score`
sits in the staged `prediction.json`, so I had seen it before writing this; my read was
formed from the petition and docket and is not an agreement number.)

## Reasoning quality: 0.88

The strongest rationale in the cell: correct anchor discipline, discounts tied to specific
record facts, an upward factor weighed and honestly caveated, a cross-check against a second
surface, and a clear statement of what would move the number. The deductions are for two
load-bearing steps asserted rather than shown.
