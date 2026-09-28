# Rationale for my numbers

**P(grant) = 0.005; predicted disposition: denied.**

## What the record shows

- Snapshot `2026-09-17.json`: paid petition, docketed September 16, 2026, from the Federal Circuit (No. 2026-1409, decided May 22, 2026). One docket entry: the petition filed August 14, 2026, response due October 16, 2026. No distribution, no CVSG, consistent with the arrival moment.
- Petitioner Justin Paul Dreiling appears as his own counsel of record with a residential address in Missouri: a pro se paid filer. Respondent is the United States, counsel of record the Solicitor General.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, distribution count 0, no CVSG, Term 2026, `signals_observable: true`.
- Provisioned documents: `petition.txt` (48 pages, text extracted, not truncated) and `questions-presented.txt`. No brief in opposition exists yet. I read the petition's questions presented, statement of the case, related-proceedings list, and the first half of the argument.

## What the petition tells me

The suit below was a Tucker Act action in the Court of Federal Claims claiming that the Judicial Council of the Federal Circuit lacked constitutional authority to bar Judge Newman from voting on the petitioner's earlier en banc petition. The Court of Federal Claims dismissed for want of a money-mandating source, and the Federal Circuit granted the government's motion for summary affirmance, stating it had no power to overturn binding Supreme Court precedent limiting Court of Federal Claims jurisdiction to monetary claims. The petition asks the Court to hold 28 U.S.C. 354(a)(2)(A)(i) unconstitutional, to require the whole Federal Circuit to recuse under 28 U.S.C. 455, and to read the Tucker Act's plain language as reaching non-monetary claims, which would require overruling United States v. Jones (1889) and a century of money-mandating doctrine.

Vehicle problems are severe and are conceded in the petition itself: a footnote acknowledges that the constitutional question was not addressed by either court below and "may not be reviewable at this time." The recusal question was the subject of the petitioner's mandamus petition No. 25-1217, which this Court denied on June 22, 2026. The Tucker Act question is an ask to overrule settled precedent with no circuit split, in a nonprecedential summary affirmance. The petitioner is a serial pro se litigant against the United States (CourtListener RECAP shows Court of Federal Claims dockets 1:22-cv-00223, 1:25-cv-00491, and 1:25-cv-02133), and a companion petition No. 26-9 raising the Tucker Act point is pending.

## Anchor and adjustments

- Caption class: private petitioner (individual v. United States), so the anchor is the `baseline` band's bracketed `reached` rate, which is also the band frozen in my context under `sal-v4`, matching the statpack table's version. Pooling every rendered prior Term (2017 through 2025) gives about 5.0% over a weighted n of roughly 12,700. That is the yardstick the evaluator will score against.
- The Federal Circuit originating-court cut (paid and IFP pooled) shows granted 3.1% plus gvr 1.5%, close to the average and not a reason to move.
- I adjust far below the anchor because every case-specific feature points the same way: pro se drafting, a nonprecedential summary affirmance, no split, an admission that the lead question was not decided below, a request to overrule 19th-century precedent, and a prior mandamus denial on one of the three questions. Pro se paid petitions of this shape are granted at a rate well under one percent, and the GVR route is closed because no intervening decision bears on the questions. I settle at 0.5%, which leaves room for the residual chance the Court does something unusual with a Newman-related filing.
- CVSG: the United States is already a party, so a CVSG cannot issue. I state 0.01 rather than zero only for the harness's benefit.
- Relist-increment from a zero-distribution state: the first distribution is nearly certain once the SG waives; only a pre-distribution dismissal or withdrawal prevents it. 0.97.
- Summary-disposition-route conditional on grant: 0.35. Among grants of paid private petitions the cert-order route is common, but this petition has no GVR hook, so I shade below an even split while acknowledging that plenary review here is also implausible.
- Dissent-from-denial: 0.02. No Justice has an established interest in the questions as framed, and the statpack publishes no baseline for this claim.
- Big-case score 0.3: the underlying Judge Newman suspension is nationally newsworthy, but a decision in this vehicle would almost certainly be a narrow Tucker Act jurisdictional holding, not a ruling on judicial-council power.

## Retrieval and uncertainty

Retrieval was light. One `fedcourts query` for recent granted SCOTUS priors returned only interim applications ranked by recency, which are not comparable to this petition, so I did not use them substantively. CourtListener MCP returned no SCOTUS docket for No. 26-9 or for the petitioner, and no Federal Circuit opinion, so I could not confirm the companion petition's current status; the September 29, 2026 long conference had not occurred at my snapshot, so it was almost certainly still pending. The RECAP docket search confirmed the lower-court history the petition recites.

Where a reader should discount me: I read only about the first 30,000 characters of the 65,000-character petition text, so the second argument section (on the summary affirmance) is characterized from the table of contents and the statement of the case rather than read in full. My number is well below the scored baseline, so if the Court treats the Newman matter as a reason for unusual attention, my Brier loss will be large; I judged that unlikely given the vehicle.
