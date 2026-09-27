# Rationale for the prediction

## Information set and limitations

This is a **forward**, cert-stage, distribution-moment cell. I used the
provisioned `event.yaml`, `record/context.json`, and
`record/snapshots/2026-09-27.json`, together with the questions presented,
petition, brief in opposition, and document manifest under `record/documents/`.
The manifest reports both briefs as nonempty and untruncated. The filed reply
appears on the docket but its text was not provisioned and I did not retrieve
it. Amicus filings are evidence of interest, not evidence of arguments I have
read. I also checked the relevant passage of the Third Circuit's February 2,
2026 Sargent opinion through CourtListener MCP.

I neither sought nor encountered this petition's disposition or subsequent
history and do not know its outcome. Related cases' earlier dispositions are
context, not this petition's outcome. Two attempted web calls about the general
Arlington Heights standard returned no visible content and contributed nothing.

The frozen context is `sal-v4`, `elevated`, Term 2026, distribution count two,
and no CVSG. Its cutoff and cut kind are null and its provenance is `as-stored`:
this is not a demonstrated first-distribution boundary. I used the supplied
record under the forward retrieval rules, without reconstructing an earlier
snapshot, and recorded the conditioning concern in `flags.json`.

The snapshot's newest proceeding is September 16, 2026. Its September 27
filename is the provisioned vintage, not proof of a particular underlying
`last_pulled` timestamp, which is not supplied. The statpack's latest repository
commit is dated September 26, 2026 at 12:03:37 UTC. That is an artifact vintage,
not a corpus refresh stamp. No local corpus was queried, and I make no claim
about the remote blob's newest pull or snapshot.

## Base rate: 16.89%, not the terminal-band rate

The committed `metrics/statpack.md` sal-v4 table matches the frozen context. I
pooled every displayed Term strictly before 2026: **2017 through 2025**. Reading
the corresponding exact `prefix_est_grant_rate` and
`prefix_weighted_resolved` fields for `elevated` in `metrics/statpack.json`
gives **521 / 3,085 = 0.1688816856**. The denominator is denial-reweighted and
counts petitions that reached this band, not merely those that ended there.
I did not average the displayed percentages equally, use the leading
terminal-band rates, or include the current Term.

For context only, the modern discretionary-cert disposition table gives about
2.82% any grants: (655 grants + 577 GVRs) divided by 43,700 resolved petitions.
The originating-Fourth-Circuit cut is about 2.5% any grants. Neither mixed
whole-docket figure replaces the selected band's risk-set anchor. The paid
relist cut has roughly 1.7%, 13.3%, 40.9%, and 36.8% grant-family shares for
terminal relist buckets zero, one, two, and three-plus, respectively; the CVSG
cut is about 34.9% with a call versus 6.3% without. These are terminal-state
descriptions, not forward transition probabilities, and not independent
multipliers to apply to the band rate.

Crucially, the two distribution entries do **not** show a completed conference
followed by a relist. July 22 scheduled September 28; September 16 scheduled
October 9; this forecast precedes both conferences. The band is kept exactly
as provided, but I discount the substantive inference usually drawn from an
actual post-conference relist. The statpack itself cautions that distribution
counts can include pre-consideration rescheduling.

## Why 22% any grant

**The strongest upward adjustment is a real, newly deepened doctrinal
disagreement.** The petition, pp. 1-2 and 11-16, frames a First/Fourth versus
Second/Third Circuit conflict over whether aggregate racial benchmarks are a
necessary gateway to an intentional-discrimination claim. The BIO, pp. 28-33,
argues that every circuit requires both purpose and effect and that none
requires a particular sequencing of their analysis. Both descriptions can be
partly right: the important disagreement is what qualifies as discriminatory
effect, not whether effect matters at all.

I checked that distinction against the primary opinion in **Sherice Sargent v.
School District of Philadelphia**, No. 24-3112 (3d Cir. February 2, 2026),
slip op. pp. 36-40, CourtListener opinion 11249456. It expressly disagrees with
the First and Fourth Circuits' aggregate approach and follows the Second
Circuit in permitting individualized proof. It also insists on real,
identifiable injury and does not hold intent alone sufficient. Thus the BIO's
agreement-on-elements argument does not eliminate the narrower conflict, while
the petition's sequencing formulation somewhat overstates it. This independent
check increases my grant estimate relative to accepting the BIO's no-split
characterization outright.

**The Court has shown some attention.** The snapshot records a response
request on July 28 after the respondent waived, five amicus entries in August,
a BIO on August 27, and a reply on September 10. A called-for response is a
positive signal, not four votes for certiorari. The petition, pp. 13-15, and
Sargent, slip op. pp. 37-38, describe prior Alito/Thomas dissents and Gorsuch's
concerns in related litigation. Those facts support renewed attention and a
possible denial writing, but the previous failures to obtain review also
counsel against treating ideological interest as a grant.

**The substantial downward adjustment is vehicle quality.** The BIO,
pp. 1-3 and 14-22, distinguishes the earlier Field Test policy from the
Pandemic Plan lottery actually challenged by the amended complaint. It says
the district court independently found insufficient allegations of purposeful
discrimination in adopting the latter. Importantly, the petition itself
acknowledges that alternative intent ruling at p. 9 n.6, while arguing it is
not before the Court because the Fourth Circuit did not reach it. The petition
therefore has a plausible response: reversal of the impact rule could lead to
remand for consideration of intent. But that does not erase an alternative
ground that could defeat the plaintiff after a successful Supreme Court
appeal. I treat it as a strong prudential vehicle problem, not a jurisdictional
bar or an established forfeiture of the whole claim.

The BIO further describes an unpublished per curiam affirmance, heterogeneous
effects across the four schools, and a nondiscriminatory pandemic explanation
for the lottery. I do not adjudicate these contested factual characterizations
as true. Their presence makes this a less clean means of settling the
individual-versus-aggregate proof question than the petition suggests. The
independent appendix, complaint, and reply were not read, so confidence in
resolving those disputes is limited.

The balance is **0.22**, about five percentage points above the reached-band
anchor: an independently supported split and demonstrated attention warrant
an uplift, but the alternative intent ground, imperfect question framing,
earlier denials in related litigation, and absence of a genuine observed
relist keep denial clearly more likely. This is a judgmental adjustment, not
a fitted model or a claim that the signal weights were estimated.

## Other probabilities and stakes

- **Further distribution, 0.55:** close to an even chance, with the split and
  potential denial writing supporting one real relist. The forecast starts
  above the frozen count of two; it does not recode a reschedule as deliberation.
- **New CVSG, 0.04:** possible federal civil-rights interests, but no evident
  need for an executive-branch position to assess this constitutional vehicle.
- **Summary route given grant, 0.10:** plenary resolution fits a contested
  circuit conflict better; no controlling intervening Supreme Court ruling
  requiring remand was identified. This is conditional, not a joint probability.
- **Any dissent/statement given denial, 0.55:** earlier writings on closely
  related issues make another plausible, but vehicle defects could instead
  produce an unexplained denial. No private cert votes are inferred.
- **Big-case score, 0.78:** nationwide stakes for selective K-12 admissions and
  proof of purposeful discrimination, independent of the 22% grant probability.
  The specific lottery and pleading posture limit the reach of this vehicle.

The procedural probabilities are subjective forecasts; the pack publishes no
forward-hazard baseline that determines them. A denial would not endorse the
Fourth Circuit's reasoning or resolve the underlying constitutional question.
