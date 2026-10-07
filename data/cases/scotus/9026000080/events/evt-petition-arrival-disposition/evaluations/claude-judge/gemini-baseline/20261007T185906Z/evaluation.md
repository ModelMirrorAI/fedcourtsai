# Evaluation — gemini-baseline — Scroggins v. City of Shreveport, No. 26-80 (arrival disposition)

## The cell

Cert stage, arrival moment, forward mode. Outcome: petition **denied** on 2026-10-05 after
one distribution (conference of 9/28/2026), no CVSG, no noted dissent, respondent's response
waived 2026-08-06. The staged opinion slot is absent, the ordinary state for a cert cell; no
semantic set is declared on a cert event, so no `semantic_grades` block is written.

## Scores

| field | value | basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | null | version mismatch, below |
| `brier_skill_score` | null | follows the omitted rate |
| `base_rate_basis` | null | follows the omitted rate |
| `reasoning_quality` | 0.55 | below |

**Why the rate and skill are omitted.** The prediction froze `context.band = baseline` under
`context.salience_version = sal-v3`; the committed `metrics/statpack.md` band table is headed
**sal-v4**. The evaluate prompt's rule for that mismatch is to omit `segment_base_rate` and
`brier_skill_score`, leave `base_rate_basis` null, and flag it (`flags.json`,
`data-quality`). For information only, not written into the JSON: `fedcourts
segment-anchors --term 2026 --salience-version sal-v3` prints the version-pinned baseline
risk-set pool at 5.02% (n=12720, OT2017–OT2025), identical under sal-v4. The candidate's
"~6.5%" anchor was the pre-rebuild sal-v3 pool.

## What the prediction got right

- The call and the number. Denied at 0.5%, which is a well-placed probability for a pro se,
  split-free, waived-response error-correction petition, and the second-lowest Brier in the
  cell.
- The anchor is the right one for the moment: the baseline band's bracketed `reached` rate
  over prior Terms, not the terminal rate.
- The discounts named are the correct ones: pro se filer, error correction of a fact-bound
  summary-judgment ruling under McDonnell Douglas, and the respondent's waiver read as a
  signal that the city did not fear a grant without being asked to respond. The 2-1 panel
  below is noted as a slight upward factor and weighed as such.
- It disclosed its tooling honestly: the CourtListener search was rate-limited, and it fell
  back to a web search that confirmed the case details and that the petition was still
  pending, which is the right thing to have checked and the right thing to have said.

## What held the score down

- Thinness. The whole rationale is one paragraph. No pooled denominator, no prior-Term
  window stated, no cross-check of the landing point against any second surface, no account
  of what would move the number or by how much. The right answer is reached by naming the
  right factors, but almost nothing is argued; a reader cannot tell whether 0.5% is a
  calibrated figure or a round guess in the right neighborhood.
- A misreading inside the reasoning. The document says "I assign a very low probability to
  any relists (0.05) since a waiver usually leads to a swift denial without a relist." At the
  arrival moment the frozen context shows zero distributions, so the increment in question is
  the petition's **first** distribution, which a waived-response petition receives in
  ordinary course and did receive here on 2026-08-19. The claim itself is scored in code and
  is not graded here; what is graded is that the reasoning document misunderstood the
  quantity it was reasoning about, which the other two candidates got right and explained.
  I have kept the weight of this modest, since it does not touch the headline probability.
- No engagement with the petition's text as a vehicle: nothing on the absence of record
  citations, the reporter-citation error, or the fact that the "Reasons for Granting" cite
  only this Court's own precedent. The record was provisioned and read (the log shows the
  petition and questions presented opened) but the rationale does not use it beyond the
  caption-level facts.
- "The Supreme Court rarely takes up fact-bound applications of the McDonnell Douglas
  framework, especially from pro se litigants" is correct as far as it goes, but is the kind
  of sentence that could be written without reading this petition.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
not_applicable; `leakage_suspected` false. The log carries 30 calls, every one marked
`unobserved` (`result_capture_coverage` 0.0, the engine's standing shape), so each is graded
on its query: provisioned-file reads, statpack greps, two corpus `query --era roberts
--decided-before 2026-08-16` attempts, a rate-limited CourtListener search on the case
caption, a direct `curl` to the CourtListener search API with the same caption, and one web
search for the caption plus "scotus". A caption search in forward mode on an open case is
legitimate forward retrieval; the candidate's prose says it showed the petition still
pending, which is consistent with the docket (first distribution 2026-08-19, denial
2026-10-05). No query reaches past the event date or names `data/qp-topics/`. The forward
default stands after checking.

## Big case

My independent read is 0.03: a single-plaintiff promotion dispute against one city, pure
error correction, waived response, denied without comment. (The predictor's `big_case_score`
sits in the staged `prediction.json`, so I had seen it before writing this; my read was
formed from the petition and docket and is not an agreement number.)

## Reasoning quality: 0.55

Right answer, right factors, honest disclosure, but a rationale too thin to show its
calibration, with one misread quantity inside it and no use of the petition text it had been
given.
