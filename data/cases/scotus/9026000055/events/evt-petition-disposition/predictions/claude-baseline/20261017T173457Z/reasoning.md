# Reasoning — P(grant) = 0.03

**Inputs.** The provisioned snapshot `record/snapshots/2026-10-17.json` and
`record/context.json` (forward mode, band `baseline` under sal-v4,
distribution_count 1, no CVSG, Term 2026). No `record/documents/` were
provisioned, so I had no questions presented, petition, BIO or reply text —
my read of the issue is inference from the docket alone.

**Anchor.** The statpack's *Segment base rate by salience band (sal-v4)* table
matches my context's salience version. Pooling the `baseline` column's
bracketed `reached` figure over Terms 2017–2025 (strictly before OT2026),
weighting by `n`: ≈ 643 / 12,877 ≈ **5.0%**. That is the scored yardstick.

**Adjustments (down).**
- Paid individual immigration case from the Fifth Circuit (lower-court number
  25-60471, the agency-review series), very likely a petition for review of a
  BIA order — a category the Court grants rarely and that is often decided in
  unpublished per curiam opinions below.
- First distribution, no relist yet; the relist-0/1 cuts show most petitions at
  this stage are denied off the first conference.
- Petitioner counsel is an immigration practitioner, not a repeat Supreme Court
  advocate.

**Adjustments (up, small).** The SG filed a full brief in opposition (after two
extensions) rather than waiving; the docket shows no call for response, so the
BIO was voluntary, which mildly suggests the petition raises something the
government thought worth answering. The petitioner filed a reply. These keep me
from going much below the anchor.

Net: 0.03. Main uncertainty: I cannot see the QP; if it presents a recognized
circuit split on a recurring INA question (the kind that produced recent grants
on petition-for-review issues), the true probability could be several times
higher. Discount my number accordingly.

**Claims.** relist-increment 0.07 (first-conference denial is the modal path);
cvsg-increment 0.002 (the federal government is the respondent);
summary-disposition-route 0.35 conditional on grant (immigration GVRs are common
in the grant family); dissent-from-denial 0.03.

**Retrieval.** One CourtListener opinion search for the CA5 decision returned
nothing; I proceeded on the snapshot and statpack.
