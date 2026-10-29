# Rationale for the probabilities

## Information set

This is a cert-stage, response-requested cell, not an interim application. I read
the event, the case-level snapshot `2026-08-13.json`, the questions presented,
the petition's argument, its appended Ninth Circuit memorandum, and the district
court's appended summary-judgment analysis. The documents manifest reports usable,
untruncated, non-OCR petition text. No opposition or reply is provisioned, which
is expected at this moment: the request for a response is the last docket entry.
I do not infer the content of the response that may later arrive.

The frozen context is forward, sal-v4 baseline, docket-number Term 2026, one
distribution, and no CVSG, with a date cutoff of August 14. I deliberately did
not supplement it with this case's live docket or later filings. Thus my account
of its posture is as of August 13, not a claim that the docket remained unchanged
on the October 29 run date. No outcome of this petition was sought or encountered,
and I do not independently know its outcome. References to other cases' outcomes
below concern general, earlier legal context only.

## Base-rate anchor

The committed statpack's sal-v4 table matches the frozen salience version. I used
the bracketed baseline **reached** rates, not the rates for petitions ending in
that band. Pooling every displayed Term strictly before 2026, namely 2017-2025,
using the corresponding exact `prefix_est_grant_rate` and
`prefix_weighted_resolved` fields in `metrics/statpack.json`, gives 660 weighted
grant-family events over 12,913 weighted resolved petitions: **5.111%**. Term 2026
is excluded. These are the committed pack's denial-reweighted estimates, not a
freshly measured rate or a rate specifically conditioned on a response request.

For shape only, the paid-segment terminal relist buckets show grant-family rates
of about 1.8% at zero relists (10,203 resolved), 13.7% at one (2,538), 41.2% at
two (495), and 37.4% at three or more (484). The terminal CVSG cut is about 34.8%
among 164 resolved CVSG petitions versus 6.4% among 13,556 without one. These
pooled cuts are not forward transition hazards and are not multiplied into the
5.111% anchor. The record names no amicus brief; the terminal zero-amicus bucket
has about a 3.8% grant-family rate over 11,109 resolved petitions, but I give that
little independent weight because support can arrive later and the cut does not
isolate its contribution from the other signals.

## Why 12% rather than 5% or 30%

The response request after a waiver is a real positive attention signal, but it
does not establish four votes for review or agreement with the petition. No
committed response-request-conditioned table exists. I move above the baseline
principally because the requested response concerns a petition aimed at a
specifically identified, live doctrinal disagreement, not merely because an
additional distribution is likely.

There is verified interest in reconsidering the framework. In **Hittle v. City of
Stockton, No. 24-427, March 10, 2025**, Thomas, joined by Gorsuch, dissented from
denial and urged reconsideration of McDonnell Douglas at summary judgment
(official separate opinion, pp. 1, 6-9). That analogous petition was nevertheless
denied: evidence of two interested Justices is not evidence of the four needed
here. In **Ames v. Ohio Department of Youth Services, No. 23-1039, June 5, 2025**,
the Court rejected a heightened prima-facie requirement for majority-group
plaintiffs; Thomas's concurrence, joined by Gorsuch, separately invited a case
squarely presenting the framework's suitability at summary judgment (concurrence,
pp. 1, 14). The majority did not abolish the framework. Both official PDFs were
checked independently of the target docket; see `retrieval.md`.

Cross's petition expressly presents that issue, and the appended memorandum's
direct-versus-circumstantial evidence analysis gives the criticism a concrete
target. Allegations that supervisors discouraged a hijab and participated in
termination, plus comparator and video evidence, make this more than an abstract
attack. Those are allegations and contested evidentiary characterizations, not
facts I have independently adjudicated. I did not view the underlying video.

Several features keep the probability much nearer 10% than 30%:

- The Ninth Circuit decision is unpublished and applies existing doctrine;
  the petition identifies substantial criticism, but does not establish a clean
  conflict between competing binding rules on the question presented.
- The question is heavily tied to disputed facts and evidentiary inferences.
  The panel and district court relied on police findings, an asserted admission
  of fault, other driving violations, and comparator differences. Those grounds
  let a respondent argue the result survives even without the challenged
  framework. I do not treat the petition's contrary narrative as undisputed.
- The district court actually discussed the other proposed comparators, including
  uncertainty about their protected status and differences in their conduct
  (Appendix B, pp. 18a-20a). That weakens the petition's suggestion that the
  comparator evidence simply went unaddressed.
- The district court held the failure-to-accommodate claim unpleaded (Appendix B,
  p. 20a n.2). The petition's accommodation and religious-coercion narrative
  therefore does not automatically supply a clean preserved accommodation issue.
- The petition's broad assertion that an employer's legitimate explanation is
  irrelevant is advocacy, not itself a showing that the lower courts adopted
  a rule foreclosing mixed causation. An opinion changing the framework could
  still leave substantial record-specific issues on remand.

Weighing those considerations produces **P(any grant) = 0.12**, with denial the
modal disposition. This probability includes plenary grants and summary grant
routes, not the probability that Cross ultimately wins her employment suit.

## Other claims and significance

`relist-increment = 0.98` prices another distribution from the frozen count of
one, not another substantive conference review. The prompt masks this claim at
the response-requested moment. `cvsg-increment = 0.015` reflects the lack of a
distinct governmental-interest reason to seek the Solicitor General's views.
The 35% summary-route probability is conditional on a grant; its unconditional
contribution is 4.2 percentage points, leaving 7.8 points for plenary review.
Already-decided authorities alone do not make a new intervening-decision GVR
likely.

The 20% conditional denial-writing probability is a judgment call driven by the
closely relevant prior writings, tempered by the possibility that the Justices
will see no reason to repeat them. Individual order-writer figures are
unconditional and can overlap; Thomas's 14% is below the 17.6% unconditional mass
for a denial accompanied by a dissent or statement. Gorsuch's authorship chance
is much lower than his chance of joining Thomas. No cert vote lineup is claimed.

The **0.55 significance score** prices the potential nationwide consequences of
changing employment-discrimination proof rules, discounted for an unpublished,
record-intensive individual vehicle. It is not grant likelihood.

## Retrieval limitations

The corpus query worked, but its broad grant examples were not close substantive
analogues and a precise Ames citation query returned no rows with an explicit
sparse-citation warning. I did not interpret that as Ames being absent from legal
history. The CourtListener MCP lookup for Hittle was throttled (HTTP 429); I made
no direct CourtListener REST request. Usable independent legal context came from
official Supreme Court PDFs retrieved on the web. Missing opposition content and
the absence of an empirical response-request hazard are the main uncertainties,
not blockers to forecasting from the supplied record.
