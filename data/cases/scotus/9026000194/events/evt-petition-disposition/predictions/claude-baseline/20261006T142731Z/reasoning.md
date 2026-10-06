# Why P(grant) = 0.12, and the other numbers

## What I read

- Snapshot `record/snapshots/2026-10-06.json` (the file `context.json` names). Paid docket No. 26-194, docketed August 14, 2026, from the Second Circuit (No. 24-2504, 172 F.4th 145, decided April 6, 2026; rehearing denied May 13, 2026). Seven docket entries: petition filed (Aug 11); respondent's waiver (Aug 17); distributed for the September 28 conference (Aug 19); **response requested** (Aug 20, due Sept 21); respondent's motion to extend the response to October 21, granted (Sept 1 and 3); one amicus brief at the cert stage, from the Official Committee of Unsecured Creditors in the Vanderbilt Minerals Chapter 11 case, counsel of record Jeffrey Lamken of MoloLamken (Sept 21).
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, `signals_observable` true, no cutoff.
- `record/documents/questions-presented.txt` and `petition.txt` (167 pages, text truncated at about 150k characters, which covers the full petition body and the Second Circuit opinion in Appendix A plus most of the bankruptcy court's decision). No brief in opposition exists yet, so I have only the petitioner's framing of the split and the panel opinion itself.
- `metrics/statpack.md`: the modern discretionary-cert section, the relist and CVSG cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table.
- One `fedcourts query` for recent granted SCOTUS priors (see `retrieval.md`); it returned recency-ranked grants, mostly emergency applications, and did not change any number.

## The anchor

My context carries `band: baseline` under `sal-v4`, and the statpack's band table is computed under `sal-v4`, so the table is my anchor. Pooling the bracketed `reached` figure for `baseline` over every rendered Term strictly before 2026 (OT2017 through OT2025) gives 637.4 weighted grants over 12,720 weighted petitions, a **5.0%** anchor. That is the rate a paid private petition that had reached the baseline band faced, and it is the yardstick my skill will be scored against.

The CVSG cut (none: granted 4.0%, gvr 2.3%) and the relist-count cut (one distribution: granted 8.2%, gvr 5.1%) describe terminal states, so I read them for shape only. In particular I did not anchor on the relist-1 bucket: my single distribution was superseded by the call for a response and says nothing yet about relisting.

## Adjustments up

1. **The Court called for a response after respondent waived.** That is the strongest signal on the docket. A response request means at least one chambers thought the petition could not be denied on the papers. The statpack publishes no response-requested cut, so I am relying on general knowledge of the Court's practice: the Court calls for a response in a small minority of waived paid petitions, and the grant rate conditional on a call sits in the high single digits to low teens, several times the paid base rate. This alone moves me from about 5% to about 10%.
2. **An acknowledged, outcome-determinative circuit split on a federal statute.** The Second Circuit expressly endorsed Koch Refining (7th Cir.) and the petition pits that against Ozark Restaurant (8th Cir.) and Williams (9th Cir.), with the Eleventh Circuit calling the § 544(a) theory "tenuous at best" and the Third Circuit in Whittaker (2026) noting the doubt. The panel's own opinion (Appendix A) confirms it rested the affirmance on § 544(a) and declined the § 541(a) ground, so the holding is squarely on the question presented.
3. **A serious cert-stage amicus.** A creditors' committee from an unrelated mass-tort bankruptcy, represented by a top Supreme Court advocate, filed within the response window. That signals the question matters to the mass-tort bankruptcy bar beyond this yacht dispute, and it is the kind of amicus that can nudge a chambers toward a closer look.
4. **The Court's recent appetite for Bankruptcy Code text.** Purdue Pharma (2024) rejected a Second Circuit reading that let the Code reach creditors' claims against non-debtors without textual warrant; the petition frames this case as the flip side of that coin, and the current Court's method favors the Eighth Circuit's reading.

## Adjustments down

1. **Vehicle: the § 541(a) alternative ground is live.** The bankruptcy court rejected the trustee's § 541(a) theory, the district court affirmed on § 541(a), and the Second Circuit affirmed on § 544(a) while expressly declining to reach § 541(a) (Appendix A, note 3). Nordlicht (2d Cir. 2024) treats reverse veil-piercing claims as general claims that can belong to the estate, so on remand the trustee has a strong path to the same judgment. The opposition will say the question is not outcome-determinative, and that argument has real force at the cert stage.
2. **Unsympathetic facts and an estoppel backstop.** The debtor is Ho Wan Kwok, found by a New York court to have hidden assets through "a shell game"; the panel described a "mountain of evidence" that the LLC was a shell. The collateral-estoppel ruling independently establishes the estate's ownership of the yacht itself, leaving only the escrow and the second vessel genuinely in play on the alter-ego ruling. The Court dislikes cases where a reversal would reward evident evasion and change little.
3. **The split is old and the Court has lived with it.** Ozark Restaurant and Koch Refining are 1987 decisions; the Court has denied review of the general-versus-personal framework for nearly four decades. A long-tolerated split needs a strong vehicle, and this is not one.
4. **Counsel asymmetry.** Petitioners are represented by a Connecticut bankruptcy boutique with no Supreme Court practice; respondent is represented by a Washington appellate practitioner who will write a vehicle-focused opposition.
5. **Band.** The salience scorer put this petition in the baseline band at the snapshot; the band does not see the call for a response, which is why I move off it, but the paid-private population it belongs to grants rarely.

Net: anchor 5%, up to roughly 10% on the call for a response, up further on the split and amicus, back down on the vehicle problems. **0.12.**

## The other claims

- **relist-increment 0.95.** The response request took the petition off the September 28 conference, so a fresh distribution after the October 21 opposition is procedurally required. The residual is a dismissal or withdrawal before redistribution.
- **cvsg-increment 0.06.** No federal party and a question the Court can judge from the briefs. Private bankruptcy petitions do occasionally draw a CVSG, hence not lower.
- **summary-disposition-route 0.05.** No intervening decision bears on the question; a grant would be plenary.
- **dissent-from-denial 0.05.** A technical standing question with bad facts; cert-stage writings on bankruptcy standing splits are rare.
- **big_case_score 0.35.** The question affects who controls creditor claims in every large bankruptcy, which is why a mass-tort creditors' committee appeared; public newsworthiness outside the bankruptcy bar is limited to the Kwok connection.

## Where to discount me

- The response-requested conditional rate is from my general knowledge of the Court's practice, not from a committed statpack cut. If the true conditional rate for a baseline-band paid petition is nearer 7% than 12%, my number is too high.
- I have not read the opposition, which does not exist yet. Everything I say about the § 541(a) alternative ground is my own read of the panel opinion and the petition's candid account of the lower-court rulings.
- The CourtListener MCP server returned HTTP 429 (daily rate limit) on my first call, so I could not confirm the live docket beyond the provisioned snapshot. The snapshot is dated today (October 6, 2026), so I expect no gap, but any entry after the September 21 amicus is unseen. This degraded the cell; it did not block it.
- I carry no knowledge of this petition's disposition. The Second Circuit decision is dated April 2026, after anything I could have learned in training, so nothing here is contaminated by a known outcome.
