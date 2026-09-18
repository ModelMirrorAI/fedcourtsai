# Rationale for the probabilities

## Record and information boundary

This is a **forward**, cert-stage petition-disposition cell. I read the event
definition, the provisioned **2026-09-17.json** snapshot, context, document
manifest, questions presented, and selected substantive portions of the petition
and brief in opposition. The frozen conditioning is **high**, **sal-v4**, Term
**2025**, with three distributions and a CVSG dated April 6, 2026. I preserve
that conditioning rather than infer a different band from the later filings.
The event has no explicit stage or moment field; its petition kind and canonical
event identifier invoke the cert instructions. The null cutoff does not supply
a historical retrieval boundary.

The snapshot records a requested response, the February 27 opposition, an
amicus filing by Samuel L. Bray, the invited United States brief filed August
31, and a September 16 supplemental submission by petitioners. I retrieved
only the two latter filings from their exact official PDF links in the snapshot.
Both predate the snapshot. The government's recommendation is a litigant's
position, **not the Court's disposition**. I did not retrieve a current docket,
any outcome, another predictor's work, or subsequent case coverage. I have no
known outcome for this petition.

## Base-rate anchor

I used the committed statpack, not a live corpus query. The statpack files'
last recorded commit is **55121cdb8, September 14, 2026, 11:02 UTC**; that is
the artifact's commit vintage, not a claimed corpus-wide pull timestamp. No
live corpus freshness is asserted here.

The correct anchor is the **bracketed reached rate for high under sal-v4**.
Pooling every displayed Term strictly before this petition's Term 2025 means
Terms **2017 through 2024**, excluding 2025 and 2026. Using the unrounded
`prefix_est_grant_rate` and `prefix_weighted_resolved` in `metrics/statpack.json`
gives **314 / 898 = 34.97%**. The denominators, newest first, are 116, 102,
105, 140, 111, 98, 99, and 127. The matching salience version and available band
make caption-floor fallback unnecessary.

For population shape, the paid-segment CVSG cut has 163 resolved cases and
approximately **34.9%** any grants (29.4% granted plus 5.5% GVR). The relist
cuts show approximately 13.3% any grants for bucket 1, 40.9% for bucket 2,
and 36.8% for bucket 3+. These are terminal-state cuts, not forward relist
hazards or independent likelihood ratios. They do not supply a probability
of another distribution from this cell's state. In particular, a distribution
following a response request or an invited brief is not interchangeable with
repeated full consideration at conference.

The broad modern discretionary-cert section implies 1,232 grant-family
outcomes among 43,700 resolved petitions, about **2.82%**. The originating-Sixth-
Circuit cut is similarly low, about 2.8% combining grants and GVRs. Neither is
the anchor for a paid petition already selected into the high band with a CVSG;
using either would discard the Court's demonstrated attention. Conversely,
adding the CVSG and distribution signals again to the high-band anchor would
double-count much of that attention.

## Why 16%, rather than 35% or a routine-denial floor

**The issue genuinely attracts review.** The provisioned QP asks whether a
beneficiary can obtain surcharge under Section 502(a)(3), with a second,
contingent question about preemption of claims under a separate agreement.
The petition's introduction and surcharge discussion argue that the Fourth
and Sixth Circuits depart from circuits recognizing the remedy after Amara.
The United States acknowledges a conflict and rejects the categorical
exclusion of surcharge (U.S. brief, printed pp. 8 and 16-18). That is stronger
evidence than an uncontested assertion in the petition. A requested response
and CVSG also establish meaningful interest, already represented in the anchor.

**The recommendation after the CVSG is unfavorable.** The United States
expressly recommends denial despite disagreeing with the Sixth Circuit's
reasoning (U.S. brief, pp. 1-2, 8, 15-18, 22). This is the decisive additional
information below the band average. The brief emphasizes a top-hat plan,
its exemption from ERISA fiduciary requirements, and the unresolved question
whether this rabbi-trust defendant has the relevant fiduciary status. It also
finds no conflict justifying review of preemption. I treat this as a persuasive
case-selection objection, not proof that petitioners necessarily lose under
every possible theory.

**The opposition supplies concrete vehicle objections.** Its introduction,
procedural account, and pp. 28-30 emphasize both the top-hat exemption and
whether any actionable violation of ERISA or the plans was established.
The lower court's reservations about liability can complicate resolution
of an abstract remedy question. I do not adopt respondent's broader assertion
that no real surcharge conflict exists: the government's brief expressly
disagrees. The U.S. brief also reports that the Fifth Circuit's Aramark panel
decision was vacated for en banc rehearing (p. 17), so I do not count that
panel opinion as undisturbed additional circuit authority.

**Petitioners have a substantial answer, preventing an extremely low forecast.**
Their September 16 supplemental reply, especially pp. 2-5 and 10-12, argues
that the Sixth Circuit decided a categorical remedial question and that
fiduciary status and ultimate liability can remain for remand. They distinguish
statutory fiduciary-duty exemptions from the enforcement provision and point
to their status as beneficiaries suing an actual trustee. Their cited examples
of broader applications of the Sixth Circuit rule are advocacy I considered,
not independently verified lower-court holdings. This answer makes a grant
plausible even against the government's recommendation. Nonetheless, I expect
the Court to prefer a case without this plan-specific complication.

My resulting **16% any-grant probability** is a judgmental adjustment, not an
estimated historical conditional rate for government opposition. There is no
such conditioned rate in the consulted pack. Most of the remaining mass is on
denial; withdrawal or dismissal is possible but not a leading explanation of
the present posture.

## Other quantities and limitations

- **Further distribution: 35%.** There may be another conference to consider
  the acknowledged conflict or a possible writing, but the government has
  supplied its requested assessment and denial can occur at the already
  scheduled conference. No additional distribution is the modal outcome.
- **CVSG increment: 0%.** Already present; the harness masks the claim rather
  than crediting a forecast of a past event.
- **Summary route given grant: 10%.** The supplied materials identify no
  intervening Supreme Court decision requiring reconsideration. Contested
  statutory interpretation and vehicle issues favor plenary treatment if the
  Court takes the case at all. This is conditional, not 10% of all outcomes.
- **Writing given denial: 8%.** An acknowledged remedies conflict leaves some
  possibility of a statement, but the vehicle objections offer a reason to
  await another case without writing. No per-Justice prediction is warranted.
- **Stakes: 0.60.** The general remedial rule potentially reaches ERISA benefit
  disputes nationally, independent of the low grant call. The specialized
  top-hat/rabbi-trust setting limits the likely practical reach of this vehicle.

The manifest marks the 118-page petition PDF's extracted text **truncated**;
the QP and BIO are nonempty and not truncated. I relied on the available
petition argument, not an assumption that the complete appendix was reviewed.
I did not retrieve the Bray brief or the March reply. The government and
supplemental briefs were not provisioned as text, but direct retrieval filled
that important gap. All briefing is advocacy. The main uncertainty is how much
weight the Court places on the broad categorical holding versus the unresolved
fiduciary-status question. An unexplained denial would not settle that merits
disagreement or confirm my account of the Court's internal reasons.
