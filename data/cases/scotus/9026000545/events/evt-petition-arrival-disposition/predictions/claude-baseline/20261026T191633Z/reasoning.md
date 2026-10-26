# Reasoning — P(grant) = 0.004

**Inputs read.** Snapshot `record/snapshots/2026-10-27.json` (one docket
entry: petition filed Oct 21, 2026, response due Nov 25, 2026; paid case;
petitioner Diana Y. Lugo appears pro se; CA11 No. 25-11476, decided June 8,
2026, rehearing denied July 27, 2026); `record/context.json` (forward mode,
arrival moment, band `baseline` under `sal-v4`, distribution_count 0, no CVSG);
provisioned `questions-presented.txt`, `petition.txt` and `appendix.txt`
(none OCR-derived, none truncated). The appendix shows the Eleventh Circuit's
decision is an unpublished ("NOT FOR PUBLICATION") per curiam by Judges Newsom,
Grant and Brasher, applying the en banc Lewis v. City of Union City comparator
standard, with rehearing en banc denied without a poll request.

**Anchor.** Per the arrival-moment rule, I anchor on my caption class's floor.
The caption is private v. a local transit authority (not federal or state), so
the class is `private` and the floor is the `baseline` band's bracketed
`reached` rate. Pooling the statpack's sal-v4 table over Terms strictly before
2026 (2017–2025): roughly 660 weighted grants over n≈12,900 reached, ≈5.1%
(per-Term 4.0%–5.9%). That figure covers the whole paid private population,
which includes counseled petitions with organized bar support.

**Adjustments (all downward).**
- Pro se petitioner. Paid pro se petitions are granted extraordinarily rarely;
  counsel quality is among the strongest grant predictors and the population
  anchor is dominated by counseled filings.
- Unpublished, non-precedential per curiam below affirming summary judgment —
  a poor vehicle and largely fact-bound.
- QPs 1–2 are framed as error correction (comparator analysis, de novo review
  of the record, Seventh Amendment). The comparator question has been raised
  in many petitions since Lewis and the Court has not taken it; Muldrow
  (2024) already addressed a related Title VII harm question.
- QP 3 (third-party advocacy as ADA protected activity) is the only arguably
  cert-worthy question, but the claimed split is asserted rather than
  demonstrated in the petition, and the case's record posture makes it a weak
  vehicle.

Net: ≈0.4%, well under the 5% class floor. I would not go to zero: the Court
occasionally GVRs or calls for a response even in pro se paid cases.

**Claims.**
- `relist-increment` 0.96 — from zero distributions, the petition will almost
  certainly be distributed at least once (after waiver or response); the
  residual covers withdrawal or a docket anomaly.
- `cvsg-increment` 0.002 — no federal interest.
- `summary-disposition-route` 0.30 — conditional on a grant; for a case like
  this, a grant is disproportionately likely to be a GVR rather than plenary.
- `dissent-from-denial` 0.005 — no Justice is likely to write on this denial.
- `order-writers` — tiny per-Justice values, consistent with the above.

**Uncertainty / discount.** I did not verify the petition's claimed circuit
split on QP 3 independently. No retrieval beyond the provisioned inputs and the
committed statpack.
