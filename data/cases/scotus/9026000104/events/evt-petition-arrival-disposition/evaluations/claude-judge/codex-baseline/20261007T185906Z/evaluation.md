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
- `brier_score` = (0.71 − 1)² = 0.0841.
- `reasoning_quality` = 0.60.
- Leakage: forward, nothing outcome-revealing retrieved, `not_applicable`.

## What the rationale got right

The base-rate work is careful and correct for the pack it ran against: the
federal band's bracketed figures pooled over the nine prior Terms (143/201,
71.1%), the disposition mix within that pool quoted accurately, and the
terminal relist-zero and no-CVSG cuts correctly rejected as arrival anchors.
It reads the caption and counsel block to confirm the frozen band is
consistent with the visible record. It is transparent that the only
external lookup failed on a rate limit and that it attempted no fallback,
and it states the consequence honestly: the forecast is class-conditional,
not vehicle-specific, and the confidence value is set low to say so.

## Why the score is not higher

The rationale makes "essentially no merits adjustment" because the
provisioned record held no petition text. That is a defensible retreat, but
it leaves on the table what was visible without any retrieval: the Solicitor
General petitioning from a Second Circuit habeas loss involving an ICE field
office director, with the ACLU on the other side, is a recognizable posture
(an immigration-detention policy struck down below), and an arrival-moment
forecaster can reason from that posture about certworthiness even with the
QP missing. One rate-limited call was the whole retrieval effort; the
sister-circuit opinions that describe the decision below were reachable by
other queries. So the number is sound as a prior and the write-up is honest
about its limits, but the analysis of *this* petition is thin, and the
outcome, a plenary grant at the first conference, was the kind of result the
visible posture pointed toward.

## Leakage

Forward cell run 2026-08-16; the case stayed open until 2026-10-01. The log
(29 calls, all captured) is repository reading: schemas, the prompt, the
statpack, the snapshot, and the predictor's own prior cells on other dockets
for format. The one CourtListener attempt was on the Second Circuit docket and
returned HTTP 429 per the candidate's disclosure. Nothing about this case's
outcome was retrieved and the reasoning reads the docket as undecided.

## Big case

My independent read is 0.85 (see `big_case.notes`). The candidate recorded no
big-case score.
