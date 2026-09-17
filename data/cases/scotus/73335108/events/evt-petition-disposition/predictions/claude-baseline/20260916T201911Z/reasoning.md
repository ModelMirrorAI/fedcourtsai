# Why 0.005

## What I read

- The provisioned snapshot `record/snapshots/2026-09-16.json` (as-stored, generated June 17, 2026). Paid docket 25-1279, Term 2025, petitioner Henry L. Watson III pro se (not a prisoner-ID filing, but self-represented from a P.O. box in Saukville, WI). Respondent is the Wisconsin warden, represented by the Wisconsin DOJ. Three entries: petition filed (entry dated Dec 22, 2025; docketed May 13, 2026), respondent's waiver of the right to respond (June 9, 2026), and one distribution for the conference of September 28, 2026 (June 17, 2026). No CVSG, no relist, no amici.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, distribution_count 1, cvsg_date null, term 2025, signals observable.
- `record/documents/petition.txt` (27 pages, text extracted, not truncated) and `questions-presented.txt`. No brief in opposition exists because the State waived.
- Not read: anything under the evaluator-only outcome path or `data/qp-topics/`.

## The case

Watson was convicted in Milwaukee County of homicide by negligent handling of a dangerous weapon after a shooting in which he fired at a man who had drawn a gun on him and a stray round killed an uninvolved bystander. The jury acquitted him on the count involving the armed antagonist on self-defense grounds and convicted on the bystander count. The Wisconsin Court of Appeals held (unpublished) that Wis. Stat. § 939.48(3) withholds the self-defense privilege where the unintended infliction of harm on a third person amounts to negligent homicide, so self-defense was unavailable as to the bystander as a matter of state law. The Wisconsin Supreme Court denied review. The Eastern District of Wisconsin denied federal habeas relief and the Seventh Circuit denied a certificate of appealability and rehearing (Sept. 12 and 26, 2025, unpublished).

The petition's core grievance is that the jury was instructed under Wis. JI-Criminal 820 to consider self-defense on both counts, with the State bearing the burden to disprove it, yet the state courts later held the defense unavailable on Count 1. It frames this as violating Boyde, Mullaney, Winship, Lockett, Eddings, Estelle v. McGuire, and Strickland.

## Anchor

Cert-stage cell with a frozen band of `baseline` under `sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" table. Per the prompt, I anchor on the `baseline` column's bracketed `reached` rate pooled over Terms strictly before 2025. The table renders Terms 2017 through 2024 for that purpose (2025 is this case's own Term and is excluded; 2026 is empty).

| Term | baseline reached | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Weighted pool: roughly 593 of 11,680, about 5.1%. That is the yardstick the evaluator will score this cell against. It is the grant-family rate (plenary grants plus GVRs) for every paid petition that ever reached the baseline band, most of which were, like this one, private petitions at a single distribution.

## Adjustments, and why the number ends up a tenth of the anchor

The baseline pool is dominated by counseled paid petitions. This petition sits at the weak end of that pool on every dimension the Court is known to weigh:

1. **Posture.** Federal habeas review of a state conviction, denied at the COA stage in an unpublished order. The Court grants almost no petitions from COA denials, and when it acts on state-prisoner habeas it is overwhelmingly on the State's petition, not the prisoner's.
2. **The federal question is derivative of state law.** Whether § 939.48(3) bars self-defense as to an unintended victim in a negligent-homicide prosecution is a question of Wisconsin law the Wisconsin courts have answered. The federal hook (that the instruction as given told the jury to consider self-defense on Count 1 and put the burden on the State) is a fact-bound dispute about what the jury was told, resolved against the petitioner below. Estelle v. McGuire is cited by the petitioner but cuts the other way.
3. **Doctrinal fit.** Lockett and Eddings are capital-sentencing cases about mitigating evidence and have no application to a guilt-phase instruction in a non-capital case. The Eighth Amendment and Ex Post Facto references do not track any cognizable theory. Mullaney/Winship is the only serious strand, and even there the state courts' answer (self-defense was simply not an element-negating defense on Count 1 under state law) is the kind of question Patterson v. New York and Martin v. Ohio leave to the States.
4. **No split.** The petition asserts that "other jurisdictions have adopted contrary approaches" without citing a single case, and the split it describes (whether States may allocate the self-defense burden differently) is one the Court has already resolved in the States' favor.
5. **Pro se drafting.** The QPs are compound and internally inconsistent (the petition alternately says the jury was instructed to consider self-defense on Count 1 and that the jury failed to do so). The caption names the prior warden rather than the docketed respondent. The petition cites Wisconsin decisions with wrong years. None of this is disqualifying by itself, but it is the profile of petitions that draw no votes.
6. **The State waived.** A waiver is the respondent's judgment that the petition is not a threat, and the Court did not call for a response before distribution. On a paid docket that is a meaningful negative signal, since the Court routinely requests a response when any Justice wants one.
7. **Long conference.** Distribution to the September 28 conference is the ordinary path for a petition docketed in May with a June waiver. It carries no signal either way.

Nothing pulls the other way. The paid fee class is the one positive relative to the IFP mass of prisoner petitions, and the anchor already conditions on it.

Against the 5.1% anchor I therefore put P(any grant, including GVR) at **0.005**. The residual is almost entirely the GVR-in-light-of-something tail and the chance that I am misjudging how the Count 1 instruction actually read, since I have the petitioner's account of the record but not the appendix.

## Claims

- `disposition` 0.005: equals the top-level probability.
- `relist-increment` 0.05: the docket shows one distribution. The statpack's relist-count cut shows roughly a quarter of the paid scored segment ending with at least one additional distribution, but that figure is dominated by petitions the Court is actually considering, and it counts reschedules. For a pro se habeas petition the State declined to answer, the realistic path to a second distribution entry is a clerical reschedule off the long conference. I put that at about one in twenty.
- `cvsg-increment` 0.002: no federal interest whatsoever.
- `summary-disposition-route` 0.5: conditional on a grant. If this petition were granted at all, a GVR or per curiam is about as likely as plenary review, because the Court would be unlikely to set this record for argument. No intervening decision exists to drive a GVR, so I do not lean the conditional further toward summary. The prior-Term cert-order share of grants runs roughly 30 to 59 percent per the statpack's Term-table note, and I have no case-specific reason to depart far from the middle of that range.
- `dissent-from-denial` 0.01: no Justice has shown an appetite for writing on state self-defense burden allocation, and pro se habeas denials from unpublished COA orders essentially never draw a statement.

## Stakes

`big_case_score` 0.03. Even if decided, the case would settle the availability of self-defense against a negligent-homicide charge for an unintended victim under one Wisconsin statute. No institutional parties, no amici, no broader controversy.

## Where to discount me

- I did not see the appendix, so my read of what Instruction 820 actually said as to Count 1 is the petitioner's account. If the trial court really did instruct that the State had to disprove self-defense on Count 1 and the state courts nonetheless affirmed on the ground that the defense was legally unavailable, the Mullaney strand is stronger than I credit it, though still an unlikely grant on this posture.
- The QP text extraction has minor OCR noise ("Boy de" for Boyde), which I read through; it does not affect the analysis.
- CourtListener's copy of this docket carried no docket entries and its last-modified date matched the snapshot's generation date, so I could not independently confirm that nothing was filed between June 17 and today. The snapshot is the corpus's as-stored payload, and forward mode makes any later filing legitimate signal rather than leakage. I found none.
