# Reasoning — Saeed v. Arizona, No. 26-512 (P(grant) = 0.006)

**Inputs read.** Snapshot `record/snapshots/2026-11-10.json`; `record/context.json`
(forward mode, band `baseline` under `sal-v8`, distribution_count 1, no CVSG,
`cert_anchor.rate` 0.0516 over 10 lookback Terms); `questions-presented.txt`; and
`petition.txt` (281 pages, truncated at the appendix; I read the QPs, related
proceedings, jurisdiction statement and Reasons for Granting). No brief in
opposition exists: Arizona filed a waiver on Oct 21, 2026, and the petition was
distributed for the December 4, 2026 conference with no call for a response.

**Anchor.** The frozen `cert_anchor` (baseline band's reached rate, 5.2%) is the
scored yardstick. The statpack's whole-band figure for `baseline` (granted 0.8%,
gvr 0.6% over ~11k resolved) and the relist-0 bucket (1.3% granted, 0.5% GVR)
describe petitions like this one that never climb further, which is where I
expect this petition to sit.

**Adjustments (all downward).**
- *Waiver, no response requested.* Arizona waived; the Court has not asked for a
  response. The Court essentially never grants a paid petition without first
  calling for a response, so as long as no call issues the grant probability is
  near zero. My number mostly reflects the small chance of a call for response
  followed by a grant.
- *Jurisdiction and vehicle.* The petition seeks review of a state intermediate
  court's dismissal of an appeal for lack of jurisdiction, in a case where the
  petitioner had been convicted but not yet sentenced. That raises an obvious
  28 U.S.C. § 1257 finality problem. QP1 asks about 28 U.S.C. § 2241 federal
  habeas relief, but no federal habeas proceeding was ever brought; the case
  came up through Arizona's Rule 24.2 motion to vacate. So the question does not
  fit the case's posture.
- *No split.* The Reasons section asks the Court to extend *Abney* to a
  post-verdict, pre-sentence stage. It is a policy argument and cites no conflict
  among lower courts. The Reasons section is about seven pages long.
- Counsel are local criminal and DUI practitioners, not repeat Supreme Court
  advocates.

**Claims.** relist-increment 0.03: a call for response would usually produce a
later re-distribution, and a rare reschedule could also count. cvsg-increment
0.002: the respondent is a State and no federal interest is involved.
summary-disposition-route 0.3 conditional on a grant: if this petition were
somehow granted, a GVR or summary action is a meaningful share of how such
petitions get granted. dissent-from-denial 0.01: Gorsuch or Sotomayor sometimes
write on double-jeopardy denials, but this vehicle is too flawed.

**Uncertainty.** I did not read the full trial record in the appendix. The
merits of the collateral-estoppel claim might be stronger than the framing
suggests, but that would not cure the finality and vehicle problems.
