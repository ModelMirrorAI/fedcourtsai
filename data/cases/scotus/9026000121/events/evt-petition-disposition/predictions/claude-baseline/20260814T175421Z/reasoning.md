# Rationale — why P(grant) = 0.01

**Anchor.** The cell's frozen context (`record/context.json`) carries
`band: baseline` under `sal-v2`, matching the statpack's segment table, so
the scored yardstick is the baseline band's bracketed **`reached`** rate.
Pooled over the nine rendered Terms strictly before this case's (OT2017–
OT2025, n ≈ 13,163 weighted), that rate is ≈ **6.5%** — the grant-family rate
a live paid petition faces from the baseline band, unconditional on its
future trajectory.

**Adjustments down (large).** I put this petition well below its band's
average:

- **Vehicle.** The Maryland Supreme Court granted review and then dismissed
  the appeal on a state procedural ground (Maryland Rule 8-602), with
  reconsideration and recall-of-mandate motions denied. An adequate and
  independent state procedural ground is a classic cert-killer.
- **QP 2 presents no federal question.** It asks for summary reversal based
  on a Maryland Supreme Court decision (Sugarloaf) about state-law
  attorney-fee memoranda — outside the Court's power to review.
- **QP 1 is fact-bound and split-free.** The Caperton/Williams/Lavoie
  due-process claim is pitched as a "question of first impression" over a
  single-page judgment order signed by an allegedly recall-ineligible retired
  judge — idiosyncratic facts, no alleged circuit or state-court split, and
  an unreported intermediate decision below.
- **Stakes and presentation.** A private fraud/fee dispute between
  individuals; the QPs are run-on and error-laden, which correlates with the
  denial pool.

**Adjustments up (small).** Paid and counseled (the band's IFP-free segment
already reflects this); judicial-disqualification claims occasionally
attract individual Justices' attention. Neither moves the number much.

**Landing point.** 0.01 — near the *ended-in-baseline* rate (≈ 1.2%) rather
than the reached rate, because the reached rate's upside comes from
petitions that go on to relist or draw a CVSG, and I forecast neither here
(see `predicted_reasoning.md`).

**Claims.** `disposition` restates 0.01. `relist-increment` = 0.97: the
frozen `distribution_count` is 0 and nearly every docketed paid petition is
distributed at least once before disposition; the residual is
withdrawal/dismissal before conference. `cvsg-increment` = 0.002: the paid
segment's unconditional CVSG incidence is ≈ 1.3% (statpack CVSG cut,
173/13,404), and this purely private state-law case sits far below it.

**Uncertainty and discounts.** No brief in opposition exists yet, so the
respondents' side is unread. My read of the Maryland procedural history comes
from the petition's own statement of related proceedings, which is
adversarial. A single corpus query for Caperton-cited priors returned
nothing (sparse citation coverage — see `retrieval.md`), so the
Caperton-petition denial pattern here is from general knowledge, not a
measured corpus rate. If the record's disqualification facts are more
egregious than the petition's presentation suggests, the main risk to this
forecast is a relist or a statement respecting denial, not a grant.
