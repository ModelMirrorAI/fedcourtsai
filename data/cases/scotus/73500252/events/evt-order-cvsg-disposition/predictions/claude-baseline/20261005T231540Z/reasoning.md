# Rationale for P(grant) = 0.60

## What I read

- Snapshot `record/snapshots/2026-10-05.json` (the file `context.json` names): paid petition from CA9, docketed June 3, 2026; two distributions (6/25 and 9/28 conferences), a "Rescheduled" entry on August 20, a response requested on June 15 after respondents waived, one amicus brief in support (Bank Policy Institute, ABA, Chamber, MBA), reply filed, and the October 5, 2026 CVSG order.
- `record/context.json`: mode `forward`, band `high` under `sal-v4`, distribution_count 2, cvsg_date 2026-10-05, term 2025, signals observable.
- `record/documents/`: `questions-presented.txt` (the QP), `petition.txt` (198 pages, truncated, but the full argument section was present), and `brief-in-opposition.txt` (32 pages, complete). None was `empty_text`.
- `metrics/statpack.md`: the modern-cert disposition section, the CVSG cut, the relist cut, and the sal-v4 segment band table.

## Anchor

The context band is `high` under `sal-v4`, and the statpack's band table is `sal-v4`, so the table is the anchor. Pooling the bracketed `reached` rate for `high` over the Term rows strictly before this case's Term (OT2017 to OT2024):

| Term | reached rate | n |
| --- | --- | --: |
| 2024 | 40.5% | 116 |
| 2023 | 31.4% | 102 |
| 2022 | 37.1% | 105 |
| 2021 | 32.1% | 140 |
| 2020 | 34.2% | 111 |
| 2019 | 25.5% | 98 |
| 2018 | 35.4% | 99 |
| 2017 | 41.7% | 127 |

Pooled: about 314 of 898, or roughly 35% any-grant. The CVSG cut of the paid scored segment says the same thing from the other direction: 29.4% granted plus 5.5% GVR, about 35% any-grant over 163 resolved CVSG petitions. The modern discretionary-cert rate for the whole docket is about 1.5% granted plus 1.3% GVR; the band and CVSG cuts, not that figure, describe this petition's population. I read the pooled band figure, 35%, as the evaluator's yardstick and the starting point.

## Adjustments up (to 0.60)

1. **The SG will very likely recommend a grant.** The OCC issued a final rule in May 2026 preempting state interest-on-escrow laws (91 Fed. Reg. 29350, per both briefs), filed an amicus brief in the Ninth Circuit below calling the Ninth Circuit's ruling of serious consequence to the mortgage market, and the SG's 2023 CVSG brief in the prior round (Nos. 22-349 and 22-529) said Lusnak and the Kivett panel erred and that Flagstar was the better vehicle if the Court took one. The current administration's SG and OCC are aligned on preemption. I put P(SG recommends granting at least one of the three petitions) at roughly 0.75 to 0.80. Historically a CVSG petition the SG supports is granted a large majority of the time, and one the SG opposes only a minority; a rough mixture (0.78 × 0.72 + 0.22 × 0.22) lands near 0.61.
2. **The split is on the Court's own test, two years after it announced it.** Three published post-Cantero decisions reach opposing results (CA1 Conti: not preempted; CA2 Cantero on remand: preempted, over a dissent; CA9 here: not preempted, over Judge R. Nelson's dissent, resting on pre-Cantero Lusnak). The Ninth Circuit on remand from the Court's own GVR declined to perform the comparative analysis, which gives the Court an institutional reason to act. The petition says the Ninth Circuit denied rehearing en banc after the conflict was identified.
3. **Vehicle is conceded.** The BIO's section C says that if any of the three petitions is granted, this is the best vehicle: a final judgment with money damages and an injunction, a summary-judgment record on significant interference, and the Lusnak question. The petition says the same. The 2023 SG brief vetted the case and found no obstacle. The savings-bank argument the other petitioners raised is addressed in the petition (class excludes pre-Dodd-Frank loans) and respondents do not press it.
4. **Docket signals beyond the CVSG.** Response requested after a waiver, an industry amicus brief at the cert stage, a reschedule before the September conference, Supreme Court specialists on both sides, a paid petition.

## Adjustments down (why not higher)

1. **The OCC rule weakens prospective importance.** The BIO's strongest point: as of June 19, 2026 the OCC rule preempts these laws going forward, so the split now governs only retrospective liability in three cases. The SG could plausibly say the rule resolves the problem and the Court need not act; I give that about a one-in-four chance.
2. **The Court denied Conti earlier in 2026** (the BIO says cert was denied with a rehearing petition pending), before the Second Circuit's remand decision created the split. That shows the Court was not moved by importance alone. The reconsideration now rests on the split, which is real but, as respondents say, confined.
3. **The Court might take Cantero instead and hold this case**, as it did in 2023. Under that path this petition resolves only after the merits decision in Cantero, and resolves as a grant (GVR) only if the bank wins. That is why the number is not 0.70 even though some grant among the three is likelier than that.
4. **Pure base rate.** About two-thirds of CVSG petitions in the corpus end in denial; the case-specific signals have to carry the whole distance from 0.35 to 0.60, and they are correlated with each other (the SG's likely view, the OCC's rule, and the amici all reflect the same industry and regulator position).

## The other claims

- **relist-increment 0.95.** A CVSG petition is always redistributed after the SG files; the only route to no further distribution is settlement or withdrawal, which the stakes make unlikely.
- **cvsg-increment 0.02.** The CVSG is on the docket; the harness masks this claim on a CVSG cell. A second invitation is practically unheard of.
- **summary-disposition-route 0.25 (conditional on grant).** Mostly the held-then-GVR path if the Court takes Cantero or Conti as the plenary vehicle and the bank wins; a small share for an outright summary reversal. Computed roughly as P(other vehicle) × P(bank wins) over P(any Flagstar grant), plus a few points for a per curiam.
- **dissent-from-denial 0.25 (conditional on denial).** A denial that follows an SG recommendation to deny usually draws no writing; a denial over an SG recommendation to grant would plausibly draw a short dissent from Justice Kavanaugh or Justice Alito.
- **big_case_score 0.45.** Important to bank regulation and the method of NBA preemption, with an OCC statement that the stakes are market-wide, but doctrinally a follow-on to Cantero and concretely about escrow interest in a dozen states.

## Retrieval and its limits

CourtListener's MCP server returned the Conti docket (No. 25-1004, docketed February 23, 2026, not terminated, last modified October 5, 2026, the same day as this CVSG) but no docket entries for SCOTUS dockets and no hit for the Cantero plaintiffs' 2026 petition, so I could not confirm from the live docket whether the Court also invited the SG in those cases on October 5; the same-day modification of the Conti docket is consistent with the three being handled together. Two `fedcourts query` calls returned recency-ranked resolved SCOTUS priors with no CVSG filter available, so they informed shape (the OT2026 grants so far are government petitions and applications) rather than the number. I did not search for and did not encounter this petition's disposition; the event is live and the CVSG issued today.

## Where to discount me

The number rests heavily on a judgment about what the Solicitor General will say, which I infer from the OCC's rule and the 2023 CVSG brief rather than from anything on this docket. If the SG recommends denial on the strength of the prospective rule, the right number is nearer 0.25. The CVSG also pushes resolution out by months, so this cell will likely resolve in the first half of 2027 or, on the hold path, later.
