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
- `brier_score` = (0.78 − 1)² = 0.0484.
- `reasoning_quality` = 0.85.
- Leakage: forward, nothing outcome-revealing retrieved, `not_applicable`.

## What the rationale got right

The anchor is computed correctly: the federal band's bracketed `reached`
figures pooled over the nine Terms strictly before OT2026 (143/201, about
71%), on the table version the pack carried at the time. The adjustment is
grounded in actual retrieval: it identified the question presented
(§ 1225(b)(2)(A) mandatory detention versus § 1226(a) bond for interior
arrests), the decision below's reporter cite, and a 7–2 circuit split, all
from sister-circuit opinions that cite the decision below. I confirmed with
one CourtListener search that those citing opinions exist in the circuits
and on the dates the rationale names, every one filed before the prediction
ran. The rationale also found the companion government petition from the
Sixth Circuit and used it the right way: as vehicle risk against *this*
docket rather than as a reason to raise the number.

The decomposition (granted or consolidated 0.60, held 0.35 with a
GVR-or-deny split, no grant anywhere 0.03, dismissal 0.02) is explicit and
each piece is defensible. The uncertainty section is candid about what is
judgment and what is published, and it says plainly that no petition text
was provisioned and where the QP characterization came from instead.

## Where it could have been sharper

The held-vehicle branch looks heavy in hindsight: when the Solicitor General
files parallel petitions on one percolated question, the Court's usual move
is to grant the lead vehicle and consolidate or grant companions rather than
hold them, and this petition was granted at its first conference. A number
in the low 0.80s was available on the same facts. That is a calibration
quibble, not an analytical flaw; the rationale named the vehicle-selection
question as its main uncertainty, which is the honest thing to do.

## Leakage

Forward cell run 2026-08-16; the case stayed open until 2026-10-01. The log
(29 calls, all captured) shows opinion searches and document reads on the
citing sister-circuit opinions, with retrieved document dates between
2026-06-24 and 2026-07-30, a docket lookup on companion No. 25-1415 showing it
pending, and corpus queries over past grants. No call reached this petition's
own disposition, no document date is on or after the resolution, and the
reasoning treats the docket as undecided. No mis-provisioning: the
prediction's frozen context shows zero distributions and the grant came six
weeks later.

## Big case

My independent read is 0.85 (see `big_case.notes`), formed from the docket
record and the public posture of the question.
