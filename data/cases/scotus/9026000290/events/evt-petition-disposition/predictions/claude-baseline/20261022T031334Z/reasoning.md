# Rationale — P(grant) = 0.004

**Inputs read:** the snapshot `2026-10-22.json`, `context.json` (forward;
band `baseline` under sal-v4; one distribution; no CVSG; Term 2026), the
`questions-presented.txt` file, and the petition (`petition.txt`, 56 pages, not
truncated). I read the QPs, the table of contents and authorities, and the
opening sections in detail.

**Anchor.** I pooled the `baseline` band's bracketed `reached` rate over the
Terms before 2026 in the sal-v4 table. It runs about 3.9–5.9% per Term, roughly
5% pooled. The relist-count cut puts relist-0 petitions at about 1.2% granted.
That figure describes petitions that *ended* undistributed, so it understates
the risk set, but this petition is at its first conference.

**Adjustments downward, all large:**
- The petitioner is pro se and filed in the paid lane. Self-represented paid
  petitions are granted at a small fraction of the segment rate.
- The procedural vehicle is very poor. The petition seeks review of the
  California Supreme Court's denial of discretionary review of a Court of
  Appeal summary denial of a writ petition. The underlying ruling is a trial
  court order sustaining a demurrer to a *seventh* amended complaint. State
  procedural grounds are likely, and the case is interlocutory.
- The claimed "conflict" is between lines of this Court's own precedent, not a
  split among lower courts. The petition also mixes RICO, §§ 1981/1983/1985,
  18 U.S.C. § 242 and California ethics claims, so no clean federal question
  is isolated.
- There is no response on the docket. The response deadline (Oct 5) passed
  before distribution, and the snapshot shows no waiver entry (it may be
  unrecorded). Distribution without a response is the ordinary path to denial.

The 0.004 figure is a floor-level number. I keep it above zero only for
tail risk.

**Increments.** The relist increment is 0.03, the residual chance of a
reschedule or a hold. The CVSG increment is 0.002. The dissent-from-denial
probability is 0.005, since pro se petitions of this kind essentially never
draw a separate writing. The summary-route probability, conditional on a
grant, is 0.3. That is roughly the GVR share of grants in the
relist cuts, and I did not move it because the conditional event is
essentially imaginary here.

**Big-case score.** I set it at 0.03 because the stakes are local and
individual.

**Uncertainty.** I did not retrieve the docket's live state beyond the
snapshot. A waiver may sit unrecorded, which would not change the call.
