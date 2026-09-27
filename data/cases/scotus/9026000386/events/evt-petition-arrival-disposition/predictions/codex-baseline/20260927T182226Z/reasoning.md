# Rationale

## Record and information boundary

This is a forward, cert-stage arrival prediction for Marlin D. Lowery v.
Cheboygan Area Schools, et al., Supreme Court docket 26-386. I read the
event definition, the provisioned `2026-09-23.json` snapshot, `context.json`,
`documents.json`, `questions-presented.txt`, and the full provisioned
`petition.txt`. The snapshot is date-cut before September 23, 2026; the
context freezes zero distributions, no CVSG, observable proceedings, Term
2026, and the `baseline` band under `sal-v4`. Zero distributions is the
arrival moment, not evidence that the Court has declined to engage.

The snapshot records docketing on September 22, a petition entry dated June
26, and a response deadline of October 22, 2026. The petition text includes
an August 21 signature date. I retain these different dates as supplied and
do not infer delay-based adverse treatment or a timeliness defect. The
provisioned document manifest reports 23 petition pages, extracted text,
and no truncation; it reports a September 24 fetch. A later fetch date is
not later case evidence by itself. No BIO is provisioned; that is not a
concession, waiver, or extraction failure. Although the petition lists
lower-court appendices, their actual opinions are not included in this
text. I therefore cannot independently establish the grounds of dismissal,
preservation, jurisdictional obstacles, or the breadth of the Sixth Circuit
holding. I do not assume any particular procedural bar.

No case-specific external search was made. I do not know this petition's
outcome, did not retrieve an outcome, and did not consult another prediction.
General-law web searches and official-source opens returned no usable
content; no substantive conclusion rests on those unsuccessful attempts.

## Anchor and adjustment

The paid filing and private petitioner make the private-caption arrival
floor appropriate. Governmental respondents do not turn Lowery into a state
petitioner. The committed `metrics/statpack.md` sal-v4 table matches the
context version. Pooling every displayed strictly prior Term, 2017–2025,
using the exact baseline `prefix_est_grant_rate` and
`prefix_weighted_resolved` fields in `metrics/statpack.json`, yields
638 grant-family outcomes over 12,720 weighted resolved petitions:
**5.0157%**. This is the bracketed reached rate, not the terminal baseline
rate and not the rate for petitions that ended undistributed. It is the
starting point, not my final assessment.

These are committed-pack figures, not a fresh live-corpus measurement. The
statpack's last recorded commit is `96ebdd342`, dated September 26, 2026,
12:03:37 UTC. I did not load a corpus blob or obtain corpus-wide newest-pull
and newest-snapshot stamps; that commit date is artifact vintage only.
The case-specific evidence vintage is the provisioned snapshot and cutoff
above, not an assertion about a current docket poll.

The modern-cert disposition section gives a roughly 2.8% all-fee grant-family
rate, and the Sixth Circuit cut likewise reports about 2.8%. Those are
broader descriptive comparisons, not substitutes for the private paid
arrival floor. The paid-segment relist and CVSG cuts show that terminal
multi-distribution and CVSG populations have materially higher grant rates.
They do not establish a forward hazard from this petition's zero state.

I reduce the arrival anchor to **P(any grant) = 0.004** for these record-based
reasons:

- The questions presented combine a challenge to Michigan unemployment
  provisions under a 1970 federal enactment, an interpretation of a later
  Michigan amendment, and an allegation of sex-disparate treatment. The
  reasons-for-review section identifies no opposing appellate holdings on
  a common federal question. A plea for uniform treatment is not evidence
  of an actual inter-circuit conflict.
- The petition's own statutory excerpts create a substantial unanswered
  fit problem. Its page 13 quotation of Michigan subsection (i)(5)
  addresses workers for an institution of higher education, while pages
  6–7 describe Lowery as a public-school bus driver. Its pages 12–13
  reproduce a federal exclusion for a school that is not an institution
  of higher education. The petition does not adequately bridge those
  distinctions. This is a criticism of the advocacy on the supplied
  pages, not an independently verified holding about current eligibility
  law or the effect of all subsequent amendments.
- The sex-discrimination theory rests on the allegation that a female bus
  driver obtained benefits while Lowery did not. The provisioned material
  does not establish comparable eligibility circumstances, a sex-based
  rule, or a lower-court rule contradicting the precedent he invokes.
  It therefore looks more like a record-specific dispute than a clean
  legal conflict warranting review.
- The petition asserts that the federal issue was preserved and ignored,
  but the actual opinions needed to assess that assertion are unavailable.
  I treat the account as advocacy rather than an adjudicated fact. No
  intervening controlling decision or concession supporting a GVR is
  identified in the supplied record.

The nonzero residual allows for a materially different picture in the
missing opinions, an overlooked legal issue, or a later development.
Self-representation is not itself a reason to discount the claim; the
specific legal framing and evidentiary gaps drive the adjustment. I have
not treated the petition's workforce statistics as independently verified.

## Other claims and significance

`relist-increment = 0.96` means at least one distribution after the frozen
count of zero. It mostly forecasts the first distribution, not an actual
second conference. My modal path is one distribution followed by denial,
with no repeat distribution. The residual allows withdrawal, dismissal,
or another route ending without a recorded conference distribution.

`cvsg-increment = 0.002` reflects the federal-state subject matter but the
lack of an established national conflict or apparent need for invited
executive-branch views in this individual dispute. This is a subjective
hazard, not the terminal CVSG bucket's grant rate.

`summary-disposition-route = 0.30` is conditional on a grant, not an
unconditional 30% chance. Although the petition asks for a GVR as a fallback,
it identifies no intervening decision. A meaningful federal statutory
question, if found suitable, would more likely receive plenary review.
The relatively substantial conditional minority for summary relief reflects
the possibility of a readily correctable omission in the unavailable
opinions. At my grant probability, the joint summary-route probability is
0.0012. `dissent-from-denial = 0.005` is conditional on denial; the supplied
record suggests no established dispute likely to draw a separate writing.

The significance score is **0.22**, independent of grant likelihood. A
broad ruling on school employees' benefits could matter beyond this
claimant, but the present vehicle combines an individual benefits history
with unverified disparate-treatment allegations. Missing opinions limit
confidence in both the legal framing and the breadth of any possible ruling.

A contact-scrubbing defect in the provisioned petition is noted in
`flags.json` without reproducing the contact information. It did not affect
the prediction.
