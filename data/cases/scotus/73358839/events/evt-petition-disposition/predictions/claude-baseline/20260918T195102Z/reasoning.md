# Rationale for my numbers

**P(grant) = 0.08; predicted disposition: denied.**

## What I read

- `record/context.json`: `mode: forward`, `band: elevated` under `sal-v4`, `distribution_count: 2`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `snapshot_date: 2026-09-18`.
- `record/snapshots/2026-09-18.json`: paid petition for a writ of certiorari **before judgment** to the Fifth Circuit (No. 24-40792), docketed May 18, 2026 as No. 25-1290. Entries: petition filed (May 6); amicus briefs from America's Future et al. (May 21), Advancing American Freedom et al. (May 26), the Buckeye Institute (June 15), and West Virginia and 24 other states (June 17); **the federal respondents waived their right to respond** (May 26); distributed for the June 18 conference (June 2); **rescheduled** (June 5); distributed for the **September 28, 2026** conference (Sept 9). No relist in the true sense: the reschedule came before the case was first considered.
- `record/documents/questions-presented.txt` and `petition.txt` (46 pages, text extracted, not truncated). QP1: whether the CTA's regulation of corporations merely because they exist exceeds the Commerce Clause. QP2: whether its suspicionless reporting mandate violates the Fourth Amendment. The petition's own vehicle section frames the ask conditionally: "If this Court grants review in NSBU, it should also review this case." It concedes the Fifth Circuit has held the appeal in abeyance since August 2025 pending FinCEN's final rule, that the district court's preliminary injunction is stayed by this Court's January 2025 order, and that as of filing "FinCEN has not issued a final rule."
- Retrieval (see `retrieval.md`): the companion docket 25-1201 shows the SG obtained three extensions, filed a brief in opposition on August 21, 2026, and both cases were distributed together on September 9 for the September 28 conference; petitioners replied September 9. Public reporting and the Federal Register show FinCEN issued a **final rule on August 11, 2026 (effective August 14)** permanently removing the reporting requirement for all U.S.-formed entities, and that the SG's opposition argues the final rule leaves the case without practical significance / moot. The NSBU reply argues voluntary cessation cannot moot a constitutional challenge to a statute that remains on the books.

## Anchor

Cert stage, `moment: distribution` (the event carries no stage or moment field, so it reads as cert by construction). The context's band is `elevated` under `sal-v4`, which matches the statpack's band table heading, so the table is my anchor. Pooling the bracketed `reached` figures for Terms strictly before OT2025 (OT2017 through OT2024, all eight rendered prior rows) gives roughly **17%** (about 484 grants over a weighted risk-set denominator of about 2,810). That is the yardstick the evaluator scores me against.

Cross-checks from the paid-segment cuts: the relist cut's bucket 2 (27.8% granted) would apply if the two distribution entries were two conference considerations, but they are not; the statpack itself warns the stored count is an upper bound because a reschedule before first consideration adds an entry. The honest bucket for a petition at its first conference is 0 (1.2% granted, terminal). CVSG cut: `none` (4.0% granted). Originating circuit ca5 (1.6% granted overall, but this is a cert-before-judgment petition, which the cut does not separate).

## Adjustments from the anchor

Down, substantially, for three reasons that compound:

1. **The mandate no longer applies to any petitioner.** FinCEN's August 2026 final rule exempts all domestic entities; every named petitioner and NFIB's members are domestic. The SG, as respondent in the companion, urges denial on that ground. The Court very rarely grants to decide the constitutionality of a statutory mandate the executive has formally stopped applying to the petitioners, whatever the merits of the voluntary-cessation argument. The rule also removed the "emergency docket" urgency that was the petition's main argument for deviating from normal practice under Rule 11.
2. **Cert before judgment is almost never granted standalone.** The petition itself asks for a grant only as a companion to 25-1201, and the Fifth Circuit appeal is in abeyance with the injunction stayed. So P(grant here) is roughly P(grant in 25-1201) times P(the Court also takes the companion). I put the first at about 0.15 (the Court has a demonstrated interest in the Commerce Clause question and Justice Gorsuch's January 2025 concurrence favored resolving it, against the SG's mootness objection and the collapse of practical stakes) and the second at about 0.5 (the Court has often consolidated CBJ companions, but a plaintiff-side CBJ petition from a preliminary-injunction posture is a weaker vehicle, and the Court could simply hold it and deny it later). Product about 0.075, plus a sliver for an independent grant, gives 0.08.
3. **The government waived a response here** rather than defending on the merits, which is consistent with treating this petition as a pure tag-along.

Up, modestly: 25 states and several organizations as amici, a genuine disagreement between the Eleventh Circuit and the district court here, and a Justice already on record favoring review of this case. The `elevated` band already prices most of this in, so I do not add much beyond it.

Net: **0.08**, well below the 17% band anchor. I hold this view with moderate confidence (0.7): the main way I am wrong is if four Justices treat the executive's regulatory retreat as a reason to settle the Commerce Clause question now rather than a reason to wait.

## Claims

- `disposition` 0.08 — equals `probability`.
- `relist-increment` 0.40 — forecasting from the 2 distribution entries shown (0 true relists). Most petitions at a first conference are not relisted, but a separate writing from Justice Gorsuch or Justice Thomas, or a one-conference hold alongside the companion, is plausible for a petition of this profile. Note the increment could also register through another reschedule if the two petitions are again re-paired.
- `cvsg-increment` 0.01 — the SG is the respondent; a CVSG is functionally impossible.
- `summary-disposition-route` 0.05 (conditional on grant) — petitioners won below, so there is nothing to GVR; a grant would be plenary and consolidated.
- `dissent-from-denial` 0.30 (conditional on denial) — a statement respecting denial is the likelier form; the base rate for separate writings on denial in the paid segment is low, and I move up for the amicus profile and a Justice already on record.

## Where to discount me

- I did not read the SG's brief in opposition or the NSBU reply themselves; I relied on a trade-press summary and the OSG docket page. If the SG's brief in fact defended the statute on the merits rather than pressing mootness, my P(grant) is too low by perhaps a few points.
- My P(grant in the companion) is a judgment call about how the Court weighs voluntary cessation at the cert stage, and it drives most of the number.
- `distribution_count: 2` in the frozen context overstates true relists (one entry is a pre-consideration reschedule). I forecast the increment from the frozen count as the contract requires, but a reader comparing against the relist cut should use bucket 0, not bucket 2.
- No brief in opposition exists in this docket (the government waived), so the respondent's position here is inferred from the companion case.
