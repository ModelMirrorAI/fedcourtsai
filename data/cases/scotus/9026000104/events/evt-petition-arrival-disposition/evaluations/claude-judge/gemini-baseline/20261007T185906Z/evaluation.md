# Evaluation — scotus/9026000104, evt-petition-arrival-disposition

**Stage:** cert, arrival moment, forward mode. **Outcome:** the petition was
GRANTED on 2026-10-01 after a single distribution (conference of 9/28/2026),
by the plenary route; `actual_granted` = 1.

## Base rate: omitted for a salience-version mismatch

This candidate froze `band: federal` under `salience_version: sal-v3`. The
committed `metrics/statpack.md` now renders its "Segment base rate by salience
band" table under **sal-v4**. A band name only means something under the
version that assigned it, so under the evaluate contract the table is no
baseline for this band: `segment_base_rate` and `brier_skill_score` are
omitted and `base_rate_basis` is left null. The mismatch is recorded in this
run's `flags.json`. The candidate is not at fault — the pack was sal-v3
when it ran, as its own rationale says. I did not relabel the number as
`terminal`, which is the basis for a prediction with no frozen band, and I
did not carry a sal-v4 number as a substitute.

## Scores

- `correct` = 1: predicted `granted`, the realized disposition.
- `brier_score` = (0.70 − 1)² = 0.09.
- `reasoning_quality` = 0.45.
- Leakage: forward, nothing outcome-revealing retrieved, `not_applicable`.

## What the rationale got right

It identified the band from the caption and counsel block, read the federal
column of the right table, and reached a number in the correct neighborhood.
The inference that a Solicitor General petition in an immigration matter
signals either an invalidated enforcement policy or an entrenched split is
sound as far as it goes, and it is the right direction of adjustment. It
disclosed the rate-limited lookups and said it was forecasting from the
snapshot and the statpack alone.

## Why the score is low

The anchor is not computed. The rationale quotes four individual Term rates
(52.4%, 60.0%, 86.2%, 89.5%) and then "anchors on an overall historical
federal bracketed rate of approximately 60–70%" without pooling the rows,
which the table's own note says is the operation; the pooled figure on that
pack was about 71%, so the stated range sits below the published anchor. The
case-specific paragraph is generic: it names no question, no lower-court
holding, and no split, and ends with "the likelihood of a grant is extremely
high" while committing to 0.70, a number slightly *below* the pooled
anchor. The words and the number pull in different directions and the
rationale does not reconcile them. The write-up is short, which is fine, but
what is there is a band lookup plus a general statement about SG petitions
rather than an analysis of this petition.

## Leakage

Forward cell run 2026-08-16; the case stayed open until 2026-10-01. The log
(23 calls) carries every call as `unobserved` (coverage 0.0), which is an
engine's standing telemetry shape and not a defect, so each call is graded
on its query. Two CourtListener docket searches: one on Second Circuit
docket 25-3141 and one on this petition's own SCOTUS docket 26-104. The
candidate reports both returned HTTP 429. A docket query on a then-open
petition is ordinary forward retrieval and could not have returned a
disposition that did not yet exist. Nothing in the reasoning presupposes the
outcome.

## Big case

My independent read is 0.85 (see `big_case.notes`).
