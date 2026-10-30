# Why P(grant) = 0.05

**Inputs read.** Snapshot `record/snapshots/2026-10-29.json`; `context.json`
(mode `forward`, band `baseline` under `sal-v4`, distribution_count 1, no CVSG,
Term 2026); provisioned `questions-presented.txt`, `petition.txt` (14 pp.,
not truncated) and `appendix.txt` (82 pp., not truncated). No brief in
opposition is on the record yet — the State waived, the Court requested a
response, and it is due 9 November 2026.

**Anchor.** The statpack's sal-v4 segment table, `baseline` band, bracketed
`reached` rate pooled over OT2017–OT2025 (every Term row strictly before
OT2026): about **5.1%** (weighted n ≈ 12,900). The paid-segment relist-count
bucket 1 (where a single-distribution petition sits if it never moves) and
the no-CVSG cut (4.1% granted + 2.3% GVR) bracket the same neighbourhood.

**Adjustments.**
- *Up:* the Court called for a response after the State waived. That means at
  least one Justice (or a law clerk in the pool) thought the petition worth a
  second look. The `baseline` band does not encode a response request, so
  this is information beyond the anchor. The issue is also real: state high
  courts have split on whether firearm disabilities make a domestic-battery
  misdemeanor "serious" (the petition cites Nevada's *Andersen* decision; other
  state courts have gone the other way), and the post-*Rahimi* salience of
  § 922(g)(9) adds interest.
- *Down:* the petition is very thin — about three pages of argument, one
  out-of-state case, no developed survey of the split, and a fact-heavy QP. The
  vehicle is weak: the Louisiana Fifth Circuit affirmed the conviction but
  **remanded for resentencing**, which invites a finality objection under
  28 U.S.C. § 1257; the jury-trial claim was disposed of below under the
  law-of-the-case doctrine after an earlier writ denial. The Court has denied
  petty-offense-exception petitions repeatedly, including with a published
  dissent from denial, which shows the issue can draw a writing without a
  grant. Most called-for-response petitions are still denied.
- Net: I hold roughly the anchor, 0.05. The response request and the split
  push up; the vehicle and the quality of the petition pull back down.

**Other claims.**
- `relist-increment` 0.96: the response request mechanically produces another
  distribution once the response is filed or the time expires; the residual is
  a withdrawal or some unusual disposal.
- `cvsg-increment` 0.01: state criminal case, no federal party.
- `summary-disposition-route` 0.10 (conditional on a grant): no intervening
  decision supports a GVR; a summary reversal on an open *Blanton* question is
  implausible.
- `dissent-from-denial` 0.20 (conditional on a denial): the response request
  suggests some Justice's interest; Justice Gorsuch has written on the
  petty-offense exception before. The poor vehicle pulls this down.
  `order-writers` is consistent with that: Gorsuch 0.16, and small residuals
  elsewhere.

**Where to discount me.** I know of the Gorsuch writing on the petty-offense
exception and the state-court split from general legal knowledge, not from
anything retrieved in this cell; I did not verify them through CourtListener.
I could not see the State's response, which will drive the outcome and could
raise the finality defect. The corpus queries returned nothing case-specific
(citation filter is sparse), so the forecast rests on the statpack and the
provisioned filings.
