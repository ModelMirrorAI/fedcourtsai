# Why P(grant) = 0.18

**Inputs read.** Snapshot `record/snapshots/2026-08-21.json` (date cut at
2026-08-21), `record/context.json` (forward mode, band `baseline` under sal-v4,
distribution_count 1, no CVSG), and the provisioned `questions-presented.txt`,
`petition.txt` (not truncated) and `appendix.txt` (truncated; I relied on the
petition's description of the First Circuit opinion rather than the appendix).
No brief in opposition exists on my record — the response was only just called
for — so I do not infer what it will say.

**Anchor.** The sal-v4 segment table's `baseline` bracketed `reached` rate,
pooled over the Terms before OT2026 (2017–2025), sits around 5% (per-Term
4.0–5.9%, n≈1,200–1,750 per Term). The 2026 row (1.8%, n=169) is my own Term and
too early/censored to lean on.

**Adjustments up.**
- *Call for a response after a waiver.* Some Justice asked for it. No committed
  table conditions on this; my judgement is that it roughly doubles a paid
  baseline petition's chances, though most such petitions are still denied.
- *Amicus support.* Seven amicus entries by Aug 20, including a 14-state
  coalition and repeat Supreme Court litigators. The statpack's paid-segment
  amicus cut puts `2+` at 18.4% granted + 4.5% GVR (n=1,449 resolved) versus
  2.0% at `0` (n=11,109). That cut is read at disposition and is not
  conditional on band, so it overlaps with the other signals; I use it as shape.
- *Subject matter and counsel.* Institute for Justice, framing in terms the
  current Court has engaged (Espinoza, Carson, Koontz, and parental-rights
  cases). The petition asserts a split (several state high courts and federal
  circuits on one side; the First Circuit and the Alaska Supreme Court on the
  other; the Eighth Circuit having flagged the question).

**Adjustments down.**
- *Vehicle and claim.* The claim is a substantive-due-process (Pierce) claim
  reviewed for a rational basis, not a Free Exercise claim; the First Circuit
  noted that the petitioners' unconstitutional-conditions authorities arise under
  the Free Exercise Clause. The Court may prefer a religion-clause vehicle for
  this line of cases, and extending heightened protection to the Pierce right is
  a larger doctrinal step.
- *Split quality.* Much of the claimed split is old or in state courts, and
  some of it reads as dicta or framing rather than square holdings.
- *Respondent's likely vehicle arguments* (IDEA equitable services, state-law
  remedies) are unknown to me but typical.

Net: ~0.18. Main uncertainty is how much weight the call for a response and the
amicus wave carry independently; I would not be surprised at 0.10 or 0.30.

**Claims.** `relist-increment` 0.97 (masked by the harness on this moment;
redistribution after the response is near-automatic). `cvsg-increment` 0.05
(state respondent, constitutional question). `summary-disposition-route` 0.06
given a grant. `dissent-from-denial` 0.22 given a denial — a salient issue for
Justices Thomas, Alito and Gorsuch; `order-writers` puts most mass on them,
consistent with that figure.

**Retrieval.** Two corpus queries (neither informative for this case — see
`retrieval.md`); no CourtListener MCP or web lookups. I deliberately did not
check the live docket, to avoid surfacing a disposition already entered.
