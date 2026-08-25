# Rationale — why 0.025

**Cell.** Arrival-moment cert cell (`moment: arrival`), forward mode, paid
petition, Term 2026, frozen band `baseline` under `sal-v3`, distribution count
0. The context's salience version matches the statpack band table's (sal-v3),
so the band table is a valid anchor.

**Anchor.** Per the arrival-moment rule I anchored on the arrival population's
own rate: the weakest (`baseline`) band's bracketed `reached` figure — the
whole paid scored segment, unconditional on trajectory — pooled over the Term
rows strictly before 2026. Pooling the statpack's "Segment base rate by
salience band (sal-v3)" rows for Terms 2017–2025 (reached rates 5.4–7.9% on
n=1176–1792 per Term, total weighted n ≈ 13,163) gives **≈ 6.5%**. I did not
use the relist-0 cut (9,659 resolved at 0 relists, 1.2% granted), which is the
rate among petitions that *ended* undistributed and understates an arrival's
future.

**Adjustments down (dominant).**
- The decision below is an **unpublished, non-precedential** Fifth Circuit
  opinion (2026 WL 766261) — the classic poor vehicle, and it cannot deepen a
  precedential split.
- The ask is **error-correction**: *Gonzalez v. Trevino* (2024) predates the
  panel decision, so the petition argues misapplication of existing precedent,
  not an open question, and no intervening decision supports a GVR as of
  docketing.
- The **claimed split is shallow**: one published Eighth Circuit case (*Murphy
  v. Schmitt*, verified on CourtListener — published, decided 2025-07-09)
  against an unpublished CA5 opinion, on a fact-intensive question (whether
  officer testimony about charging practices "bolsters" objective evidence).
- **Petition-quality signals**: the 25-page petition's "Reasons for Granting"
  section runs about two pages; the conclusion of the introduction asks the
  Court to "grant this petition for rehearing en banc" (recycled from the CA5
  filing); repeated typos ("JURSIDICTION", "FOUTH AMENDMENT", "Gozalez");
  counsel is a Houston firm, not a Supreme Court practice. These correlate
  with the low-grant tail of the paid segment.
- The QP as framed ("authorizes the use of **any** objective evidence to
  defeat probable cause") is doctrinally muddled — the *Nieves* exception
  operates notwithstanding probable cause, not to defeat it.

**Adjustments up (modest).**
- Post-*Gonzalez* application of the objective-evidence standard is genuinely
  percolating, and several Justices wrote separately in *Gonzalez*; the issue
  will recur, and the Court sometimes holds such petitions for a better
  vehicle.
- Paid petition with a developed summary-judgment record and preserved
  arguments.

Net: well below the ~6.5% arrival anchor; I land at **P(grant family) = 0.025**,
`predicted_disposition: denied`, `granted: 0`.

**Claims.**
- `disposition` 0.025 — restates the top-level probability.
- `relist-increment` 0.95 — the record shows zero distributions; nearly every
  paid petition that is not withdrawn or dismissed before conference is
  distributed at least once after the BIO is filed or waived, so from a
  zero-distribution vantage the increment is near-certain (residual: early
  settlement/withdrawal or a coverage gap in the docket record).
- `cvsg-increment` 0.004 — CVSGs run ~1.3% of the paid scored segment overall
  (173/13,630 in the CVSG cut) and concentrate in cases with a federal
  interest; a §1983 suit against a municipality has essentially none.
- `summary-disposition-route` 0.4 — conditional on a grant-family outcome. In
  the baseline band's base rates the gvr share of the grant family is roughly
  a third (0.4% gvr vs 0.8% granted); I nudge up because this petition's
  error-correction posture makes a GVR-in-light-of-a-future-decision relatively
  more plausible than plenary review, conditional on the Court acting at all.
- `dissent-from-denial` 0.02 — no published baseline; dissents/statements at
  denial are rare, this vehicle is weak, but the doctrine has active separate-
  writing interest, so slightly above negligible.

**Uncertainty and discounts.** The biggest uncertainty is the quality of the
Fifth Circuit's reasoning, which I could not read — the opinion is unpublished
and not in CourtListener's opinion index, so my read of the decision below is
entirely through the petition's characterization, with no BIO on file to push
back (none exists yet at arrival; `documents.json` lists only the petition and
QP, both extracted cleanly). If the panel's treatment of the officer testimony
is as stark as the petition claims, the split argument is better than I have
credited and 0.025 is a point or two low. My corpus citation lookup for
*Gonzalez* returned nothing (citation coverage is 159 of ~590k SCOTUS rows — a
data gap, not evidence), so the percolation read rests on my own legal
knowledge plus the verified *Murphy* search. Base rates are from the committed
`metrics/statpack.md` at the run checkout.
