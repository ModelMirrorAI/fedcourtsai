# Why P(grant) = 0.01

## The record I worked from

- Snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names), mode `forward`, `cut_kind` null, so the snapshot is the docket as of the latest poll. Docket 25-1249, paid, Term 2025. Petition filed January 6, 2026 (received by the Clerk March 2, docketed May 5, 2026, a four-month lag that itself reads as a pro se filing corrected before docketing). Brief in opposition filed June 2, 2026; distributed June 17, 2026 for the conference of September 28, 2026. One distribution, no relist, no CVSG, no amici.
- Context: `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `signals_observable: true`, `term: 2025`. I used the frozen band rather than deriving one.
- `record/documents/petition.txt` (52 pages, text extracted) and `questions-presented.txt`. The petition is filed pro se by the petitioner, a Nevada resident, against his former spouse, seeking review of a Washington Court of Appeals, Division 1, unpublished decision (April 21, 2025) affirming a Skagit County civil protection order under RCW 7.105; the Washington Supreme Court denied review October 8, 2025. The single question presented bundles a due process attack on civil protection-order procedure (preponderance standard, hearsay, no jury or confrontation), a Second Amendment attack on the order's firearm prohibition, a Supremacy Clause preemption theory about immigration, and a bill-of-attainder theory against 18 U.S.C. 922(g)(8), 18 U.S.C. 2265, and the VAWA self-petition provisions. The reasons-for-granting section cites no conflict among lower courts; it argues the merits and distinguishes *Rahimi* on the petitioner's personal facts.
- `record/documents/brief-in-opposition.txt` was fetched with `empty_text: true` (12 pages, no text layer). I treat the BIO as content-unavailable. Its existence tells me the respondent is represented (Seattle counsel address on the docket) and opposed rather than waived, which is mildly unfavorable to the petitioner but carries little weight either way.

## Anchor

Cert stage, `moment: distribution`, band `baseline`, salience version `sal-v4` matching the statpack's band table heading. Pooling the bracketed `reached` figure for `baseline` over the rendered Terms strictly before OT2025 (OT2017 through OT2024) gives about 5.1% on a weighted denominator of roughly 11,580 petitions; OT2025's own row reads 3.9% but is this case's Term and excluded. That pooled 5.1% is the yardstick this cell is scored against, so a no-view answer would restate it. The shape cuts beside it: paid scored petitions with zero relists deny at 97.0% and grant at 1.2%; the CVSG-`none` bucket denies at 92.6%.

## Adjustments, all downward

The `reached` rate is the grant rate of every paid petition that ever sat in `baseline`, including those that went on to relist into `elevated` or `high`. Almost nothing about this petition suggests it is one of those:

1. **Pro se petitioner in a private family dispute.** Grants of pro se paid petitions from state domestic-relations proceedings are essentially unobserved in the modern docket. The originating-court cut shows state intermediate courts denying at 88 to 97 percent with grants in the 0 to 3 percent range even for counseled petitions.
2. **No split, no published opinion.** The Court of Appeals decision is unpublished and the state supreme court denied review, so there is no reasoned opinion to review and no conflict alleged. The petition is a merits brief, not a cert petition in form.
3. **Omnibus, largely non-preserved-looking question.** A single question spanning five constitutional theories, including attacks on federal statutes in a case where no federal party appears and no federal statute was applied by the courts below, is not a question the Court could grant as written.
4. **The Second Amendment hook is spent.** *United States v. Rahimi* (2024) sustained 922(g)(8) against a facial challenge; a due-process-flavored as-applied variant from a state civil order is not a hold candidate for anything I know to be pending.

Against that, the only upward considerations are that the petition is paid rather than IFP (already the population the band table describes) and that the Court has shown episodic interest in Second Amendment vehicles. Neither moves a pro se protective-order case out of the near-zero tail. I land at 0.01, roughly a fifth of the pooled anchor, and I would not defend a number above 0.02.

## The other claims

- **relist-increment 0.12.** From one distribution, the population's chance of at least one further distribution is about a quarter (3,503 of 13,911 paid scored petitions carry a count above zero), but that figure is an upper bound that includes reschedules and is dominated by petitions with a signal this one lacks. Long-conference petitions do pick up administrative reschedules, so I do not go below a tenth.
- **cvsg-increment 0.005.** No federal party, private respondent, pro se petitioner; the CVSG cut's 173 invitations are counseled petitions with a federal interest in play.
- **summary-disposition-route 0.6.** Conditional on any grant, a GVR is the only plausible form; the modern-cert table's grant family runs roughly 47% GVR overall, and this case's plenary arm is far weaker than the average grant's.
- **dissent-from-denial 0.01.** Statements respecting denial attach to counseled vehicles with reasoned opinions below.
- **big_case_score 0.15.** Stakes if decided are low: the realistic decision is a silent denial of an individual protective-order appeal, notwithstanding the nominal breadth of the question.

## Uncertainty and where to discount me

- I could not read the BIO, so I do not know whether it raises a jurisdictional or preservation defect; that would only push the number further down.
- I did not read the Court of Appeals opinion itself (a CourtListener search for the parties' name in the Washington appellate courts returned no results, consistent with an unpublished disposition); my description of it comes from the petition's own account and appendix table.
- I did not check whether any OT2026 grant touches protective-order firearm prohibitions; if one exists, the relist-increment number is too low and the GVR arm of the grant probability is slightly understated.
- Two corpus `query` calls returned recent granted and denied SCOTUS rows but the query surface has no subject filter, so they served as a tooling check rather than as comparable priors; no prior shaped the number.
- A prior claude-baseline prediction for this event exists in the directory from the July 2026 run. I did not read it; this cell is forecast from the September 16 snapshot alone.
