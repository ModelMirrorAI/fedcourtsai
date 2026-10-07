# Rationale for the prediction

## Record and information boundary

This is a forward cert-stage distribution cell for Nunzio Calce, et al. v.
City of New York, New York, et al., docket 26-46. I read the provisioned
2026-10-06.json snapshot, event.yaml, context.json, documents.json,
questions-presented.txt, and the pertinent argument and lower-court portions
of petition.txt. The petition is listed as an untruncated, nonempty 80-page
document, including appendices. No brief in opposition is provisioned; the
snapshot shows that the requested response is not due until November 23.
I therefore have the petitioners' advocacy and the appended decisions, not
the City's cert-stage answer or the texts of the two recorded amicus briefs.

The frozen context is baseline under sal-v4, Term 2026, one distribution,
no CVSG, and observable proceedings. Its cutoff and cut_kind are null and
its provenance is as-stored. This forecast uses the supplied October 6
baseline, including the response request and extension entered after the
first distribution; it is not an attempted reconstruction of an August 19
information set. The latest proceeding shown is the September 28 extension.
I did not retrieve this petition's current docket, disposition, or subsequent
history, and no outcome of this petition was encountered or used.

## Anchor and adjustment

The committed statpack's sal-v4 table matches the frozen band. Pooling every
displayed strictly prior Term, 2017 through 2025, using the baseline band's
bracketed reached rates gives 638 estimated grant-family outcomes over 12,720
weighted resolved petitions, or 5.0157%. I computed this from the corresponding
prefix_est_grant_rate and prefix_weighted_resolved fields in statpack.json,
not the rounded display percentages or terminal-band rates. The Term 2026 row
is excluded. This is a private-petitioner anchor, not a government-petitioner
floor or an IFP rate. The pack file's latest recorded commit is September 28,
2026; I used that committed statistical artifact, not a freshly queried corpus.

The broader modern-cert counts imply approximately 2.8% grant-family outcomes;
the Second Circuit cut is about 4.9%. These are context, not replacements for
the matched risk-set anchor. The paid terminal relist buckets show roughly
1.7%, 13.3%, 40.9%, and 36.8% grant-family rates for zero, one, two, and three
or more relists. The paid CVSG cut is about 34.9%, versus 6.3% without a CVSG.
Those terminal aggregates are not transition probabilities from this case's
present state, and I do not substitute them for the increment claims.

My 60% grant-family forecast is a large, expressly judgmental departure from
the 5% anchor. The chief reason is not merely the Second Amendment subject
matter or the existence of amici. It is the combination of a potentially
outcome-determinative intervening precedent and a relatively inexpensive GVR
route, reinforced by an actual request for an opposition after the City waived
response:

- Petition pages 15-17 describe Wolford, decided June 25, 2026, as expressly
  placing historical limitations outside the threshold textual inquiry.
  That date follows the April 13, 2026 appellate judgment. Taken as presented,
  this directly bears on the ground necessary to the judgment, making
  reconsideration more plausible than a free-standing request for error
  correction. This description is the petition's account, not an independently
  verified holding in this run.
- Appendix A, pages 3a-5a, independently shows the operative reasoning below:
  plaintiffs had to prove common use at step one and lost because their
  summary-judgment record did not establish it. The evidentiary failure is
  real, but its legal significance depends on the disputed allocation of
  proof. It is therefore not clearly an independent ground insulating the
  judgment from the proposed doctrinal correction.
- Petition pages 8-12 identify a methodological split, principally contrasting
  the Sixth Circuit's Bridges analysis with the Second Circuit's approach.
  The differences in regulated weapons weaken the claim of a clean,
  outcome-level split; the vacated Teter opinion is not a live circuit holding.
- Petition pages 24-25 expressly seek summary relief or a GVR, and identify
  Viramontes as a granted related case. I use that identification only as a
  supplied reason why a hold-and-remand route is conceivable, not as evidence
  of any later decision. The petition itself distinguishes Caetano's rejection
  of founding-era and military-use restrictions from the present burden-of-
  proof question, so Caetano alone does not settle this case.
- The September 8 response request is evidence of judicial attention after
  waiver, not proof that four Justices favor plenary review. The September 28
  order grants only additional response time, not certiorari.

There are substantial denial risks: the appellate decision is unpublished;
the panel casts the case as a Rule 56 failure; materials offered for the first
time on appeal were rejected; the City has not yet answered the alleged split
or the intervening-precedent argument; and the Court can prefer another
vehicle. These considerations prevent a high-confidence grant forecast.
My illustrative disposition allocation is 45% GVR, 6% summary reversal,
9% plenary grant, 39% denial, and 1% dismissal or withdrawal. It sums to the
60% grant-family probability and makes the cert-order route 51/60 = 85%
conditional on a grant. These are judgmental allocations, not fitted estimates.

## Other claims and stakes

The 95% distribution-increment probability follows mainly from unfinished
response briefing after an already recorded distribution. It should not be
read as 95% confidence in heightened merits interest. The 1% CVSG probability
reflects the local constitutional dispute and the absence of a specific federal
administrative or statutory interest requiring the Solicitor General's input.
The 30% separate-writing probability conditional on denial reflects the
petition's direct doctrinal challenge and its discussion of prior separate
writings, balanced against the possibility of a routine vehicle-based denial.
No published transition or denial-writing baseline was assumed.

The stakes score is 0.68 independently of the grant odds: allocating the
common-use burden could affect arms restrictions well beyond electronic
weapons, although a GVR itself would produce a much narrower immediate result.

## Retrieval limitations

General-precedent web searches and an attempted official Caetano PDF opening
returned no usable content. A CourtListener MCP lookup for 577 U.S. 411 was
throttled with HTTP 429. I did not retry through REST or obtain credentials.
I completed the forecast from the provisioned record and committed base rates.
In particular, Wolford's scope and the asserted related-case grant were not
independently checked; the resulting one-sided substantive record is the
largest reason to discount confidence in the large upward adjustment. The
tooling limitation is also recorded in flags.json and retrieval.md.
