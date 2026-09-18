# Rationale for P(any grant) = 0.42

## Information set

This is the cert-stage, CVSG-moment forecast for Jerry Aldridge, et al. v.
Regions Bank, Supreme Court docket 25-590. I read the event definition,
`record/snapshots/2026-04-07.json`, the questions presented, relevant portions of
the petition and its appended Sixth Circuit opinion, and the brief in
opposition, particularly its introduction and split/vehicle arguments. The
frozen context is forward mode, OT2025, high band under sal-v4, two
distributions, and a CVSG dated April 6, 2026. The snapshot stops strictly
before April 7; it is not a September docket update.

The manifest identifies the November 14, 2025 petition as truncated, although
its argument through the conclusion and the relevant appellate-opinion passages
are available. The February 27, 2026 opposition is not marked truncated. Both
have extracted text. Their July 16 fetch date does not change their filing
dates. The snapshot records a reply and Samuel Bray's amicus brief, but their
texts are not provisioned. No government merits recommendation is among the
inputs. I do not infer its content, or its present filing status, from that
absence. I did not retrieve this petition's current docket or disposition and
do not know its outcome. The forecast is based on this frozen pre-decision
record, with outside retrieval restricted to general precedents.

## Empirical anchor

I used the committed `metrics/statpack.md` and corresponding JSON, not a fresh
corpus query. Their salience table matches sal-v4. Pooling every displayed Term
strictly before OT2025, OT2017 through OT2024, gives **314 weighted grants out
of 898 weighted resolved high-band reached petitions: 34.97%**. I computed
this from the JSON's `prefix_est_grant_rate` and `prefix_weighted_resolved`
fields, rather than averaging rounded percentages or including OT2025/2026.

The paid-segment CVSG cut provides a closely aligned descriptive check: among
163 resolved petitions it shows 29.4% granted plus 5.5% GVR, approximately
34.9% in the grant family. That cut pools Terms and terminal status; it is not
a second independent update or a strictly-prior, CVSG-only estimator. The
matching prior-Term high-band reached pool remains the numerical anchor.
The all-modern-cert counts imply only about 2.8% in the grant family, and the
Sixth Circuit marginal cut is similarly low; neither describes this already
selected CVSG petition. I therefore do not average either into its prior.

The paid-segment relist cut shows approximately 1.7%, 13.3%, 40.9%, and 36.8%
grant-family rates at terminal relist counts 0, 1, 2, and 3+, respectively.
Those terminal buckets neither measure the probability of another distribution
from this state nor justify adding the CVSG and distribution signals twice.
The 0.96 increment forecast instead reflects the expected return to conference
after the requested government's submission. The initial distribution before
the response request is especially weak evidence of substantive reconsideration.

These are statistics from the committed pack as supplied in this checkout,
not claims about a freshly pulled corpus. The pack does not state the newest
corpus pull stamp or newest stored snapshot date, so I cannot certify its blob
freshness. The case-specific vintage I actually used is the truncated April 7
snapshot, not an inferred current `last_pulled` date.

## Why modestly above the anchor, but below one-half

**The conflict is substantial.** The first QP concerns surcharge under
29 U.S.C. Section 1132(a)(3), not merely whether these participants should
recover on their particular facts. Petition pages 3-6 and 34-36 describe a
multi-circuit disagreement. More importantly, the supplied appellate opinion
itself expressly aligns with the Fourth Circuit's rejection of surcharge
(Pet. App. 32a-34a). The opposition acknowledges the Fifth Circuit's later
Aramark decision permitting surcharge against ERISA fiduciaries (BIO 21-25),
although it argues that this case falls outside that rule. That supplies a
reason to view the disagreement as live rather than simply a collection of
obsolete pre-Montanile cases. I have not independently checked Aramark's
subsequent rehearing status; the opposition describes it as pending when filed.

**There is a serious doctrinal question, not an obvious summary correction.**
General-precedent retrieval confirmed Amara's treatment of monetary surcharge
against a trustee-like fiduciary as equitable relief, while stressing that
the defendant's status matters. See CIGNA Corp. v. Amara, 563 U.S. 421,
441-442, 444 (2011), CourtListener lead opinion 9441561. Montanile, 577 U.S.
136, 148 n.3 (2016), cautions that Amara's Section 502(a)(3) discussion was
not essential and did not displace earlier equitable-remedies precedents
(CourtListener lead opinion 9821183). I do not treat that footnote as an
unambiguous resolution of all fiduciary surcharge claims, as the opposition
urges. This interpretive tension supports eventual review somewhere, but
does not compel review here.

**Vehicle objections restrain the forecast.** The top-hat-plan exception
and Regions' contested fiduciary status distinguish the case from ordinary
plan-beneficiary litigation. The lower court also questioned whether any plan
term or statutory duty had been violated, but expressly bypassed that issue
and decided the remedy question (Pet. App. 32a). This is a real antecedent
problem, not an established independent holding that automatically forecloses
review. Petition pages 26-28 answer that an actual trust relationship suffices
and that plan-term violations can support relief notwithstanding the statutory
fiduciary-duty exemption. Pages 35-36 emphasize the final judgment and the
Court's ability to decide remedies while leaving liability for remand. Those
are meaningful answers, but they do not make this a clean ordinary-fiduciary
vehicle. The BIO's argument for waiting for a clearer case remains persuasive.

**The second question contributes less.** The alternative state-law preemption
question adds stakes because petitioners describe a remedial gap, but the
opposition identifies no asserted circuit conflict on that question (BIO
27-28). It also entangles the separate trust contract with the plan itself.
I view it as a weaker independent route to certiorari than surcharge.

Taken together, a developed conflict and the explicit reasoning below warrant
a modest upward adjustment from roughly 35% to **42%**, while the vehicle
problems prevent a grant-majority prediction. This is a judgmental adjustment,
not a fitted estimate. The CVSG is already in the conditioning state and is
not added again as a free-standing bonus. The unobserved government
recommendation is the largest source of uncertainty.

## Other fields and limitations

The 10% conditional summary-route estimate leaves room for a hold and later
GVR if another case supplies a controlling rule, but no such rule is established
by these inputs. The 12% conditional separate-writing estimate reflects some
possibility of concern over the remedial conflict, with quiet denial still
overwhelmingly more likely. The CVSG increment is already vacuous; zero records
no forecast of a new invitation, not doubt that the April 6 invitation occurred.

The stakes score is **0.58**, independently of the grant probability: the first
question could affect ERISA remedies well beyond these executives, while the
top-hat/trust setting could confine a decision's practical reach. I omit cert
votes rather than manufacture an unobservable lineup.

Web attempts to retrieve general Amara material returned no usable content;
CourtListener MCP supplied the relevant precedent passages successfully. No
current-case outcome information surfaced. The manifest's petition truncation
is disclosed in `flags.json`; absent reply and amicus texts further limit the
assessment without implying that those filings lack merit.
