# Rationale for the probabilities

## Information set

This is a forward cert-stage forecast for Sigalovskaya v. Braden, Supreme Court
No. 25-1250, formed on September 18, 2026. I read the provisioned
`record/snapshots/2026-09-18.json`, event definition, context, questions
presented, document manifest, and substantive portions of both the petition
and opposition. The manifest marks both briefs untruncated and text-available.
The snapshot is as-stored, with no moment cutoff; I do not treat it as a
reconstruction of the first distribution. The event has no express stage or
moment, so the petition-stage default governs.

The context supplies sal-v4, elevated, Term 2025, two distributions, and no
CVSG. The docket itself records a requested response, which is distinct from
a CVSG. I retained the supplied band rather than reclassifying this private
petitioner based on the federal respondent. No own-case outcome or subsequent
history was retrieved, and I do not already know this petition's disposition.

## Quantitative anchor

The committed `metrics/statpack.md` sal-v4 table matches this cell's version.
Pooling every displayed strictly-prior Term, 2017 through 2024, for elevated's
bracketed **reached** rate gives approximately **17.24%**, with a weighted
resolved denominator of **2,810**. This calculation weights each displayed
rate by its displayed denominator; the numerator, about 484.386, is approximate
because those rates are rounded. Terms 2025 and 2026 are excluded. This is a
conditional selected-population anchor, not the terminal elevated rate.

For scale only, the modern discretionary-cert table has 1,232 grants/GVRs
among 43,700 estimated resolved petitions, approximately 2.82%. The ca2 cut's
grant-family share is approximately 4.9%. Neither substitutes for the band
anchor. The paid scored-segment terminal relist cuts rise from roughly 1.7%
grant-family at zero relists to 13.3% at one and 40.9% at two; the CVSG cut is
34.9% versus 6.3% without a CVSG. Those are terminal populations, not the
hazard of this petition receiving another distribution or CVSG. I use them
only for shape, not as increment probabilities.

These figures describe the committed pack available in this checkout, not a
freshly queried corpus. I did not pull or query the corpus and therefore do
not assert a corpus-wide latest-pull or latest-snapshot vintage. This case's
input vintage is the September 18 snapshot, whose source creation field is
September 17 and whose last listed proceeding is September 9.

## Why 16%, rather than simply repeating the anchor

**Reasons for attention.** The petition's QPs and pp. 2-4, 11-18, and 20-24
present a serious boundary question: whether a false arrest during a
warrantless home intrusion can be distinguished from Bivens because the
arresting officer allegedly fabricated the asserted probable cause. The
petition distinguishes fabrication cases involving earlier investigative
steps and independent charging decisions. It also argues that treating an
administrative complaint mechanism as sufficient to extinguish an established
remedy bypasses the new-context inquiry. The divided panel and the Court's
June 17 response request make this more substantial than a routine petition.
The petition's factual account remains allegations, not my finding that the
officers committed misconduct.

**Reasons against this vehicle.** The opposition, pp. 10-19, emphasizes that
the sole surviving claim concerns Braden's alleged fabrication, while other
agents allegedly carried out the unlawful entry and search. It marshals
post-Abbasi/Egbert fabrication decisions rather than merely denying the
existence of any broad Bivens disagreements. The petitioner has a meaningful
answer about direct arrest versus intervening decisionmakers, but the record
does not establish an unavoidable square conflict on these precise facts.
Moreover, the per curiam affirmance has no shared reasoning between its two
supporters. That can illustrate doctrinal confusion, but also makes this a
poor vehicle for resolving QP 2 alone. The government expressly opposes both
review and a hold. I give that case-specific opposition substantial weight,
without treating it as dispositive.

Egbert v. Boule, 596 U.S. 482 (2022), confirms the restrictive treatment of
new Bivens contexts and alternative remedial structures; I checked relevant
opinion passages through CourtListener (opinion 6347905). That does not
settle the disputed threshold question here: whether this context is new at
all. My forecast concerns selection for review, not a declaration that
petitioner's constitutional argument is wrong.

**Related-case route.** The opposition, pp. 17-18 and footnote 3, reports a
June 22, 2026 grant in Nielsen v. Watanabe on a related remedies question,
and discusses Herzon v. Arias as a different pending vehicle. I use that
pre-snapshot information as supplied, without retrieving either case's later
history or treating the scheduled argument as an event that has happened.
It reduces the need for another plenary grant but leaves a meaningful
hold-and-GVR possibility. The government's explanation for why Nielsen need
not affect this case is a substantial reason that denial remains the mode.

Finally, two docket distributions overstate the strength of an ordinary
post-conference relist signal here: the first preceded the response request,
and the second followed the requested opposition over the summer. Together,
these downward vehicle and signal adjustments largely offset the genuine
doctrinal interest and related-case route. My resulting P(any grant) is
**0.16**, slightly below the approximately 0.1724 band anchor.

## Other elicited judgments and limitations

The 0.30 relist-increment probability prices one further distribution above
the frozen count of two, not the existence of a prior redistribution. The
0.005 CVSG probability reflects the government's existing party participation.
The 0.60 summary-route figure is conditional on a grant and predominantly
prices a later GVR; the 0.12 separate-writing figure is conditional on denial.
These are subjective judgments, not estimates taken from unprovided hazard
tables. They match the procedural forecasts in `predicted_reasoning.md`.

The **0.63 significance score** concerns the nationwide reach of federal
officer accountability and existing constitutional damages remedies, not
the likelihood of review. Its ceiling reflects the narrow surviving claim
and vehicle complications.

I did not retrieve the appendix or independently audit every circuit case
cited in the briefs. No reply text was provisioned. General web retrieval
for Egbert returned no usable content; CourtListener supplied the relevant
primary-source passages instead. These limits warrant restraint, not a
missing-record assumption or retrieval of this petition's outcome.
