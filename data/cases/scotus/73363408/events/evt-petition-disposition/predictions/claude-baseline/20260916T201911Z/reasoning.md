# Rationale for the numbers

**P(grant) = 0.003; predicted disposition: denied.**

## What I read

- `record/snapshots/2026-09-16.json` (the provisioned baseline, named by `context.json`). Paid docket 25-1293, OT2025 term; petition filed January 2, 2026 and docketed May 19, 2026 after the Clerk gave the petitioner 60 extra days to file a Rule 33.1 booklet; respondents waived a response on May 27, 2026; distributed July 1, 2026 for the September 28, 2026 conference. One distribution, no relist, no CVSG. The petitioner appears as his own attorney with no counsel of record, so this is a pro se paid petition. The lower court is the Court of Appeals of Wisconsin, District II, with the Wisconsin Supreme Court denying review on October 6, 2025.
- `record/documents/questions-presented.txt` and `record/documents/petition.txt` (42 pages, text extracted, not truncated). No brief in opposition exists because respondents waived, so `documents.json` lists only the petition and the QP cut.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, `signals_observable` true, no cutoff.
- The committed `metrics/statpack.md`: the modern discretionary-cert section, the relist and CVSG cuts, and the per-Term segment base rate by salience band (`sal-v4`, which matches my context).

## Anchor

The context's band is `baseline` and the segment table's salience version matches, so the anchor is the `baseline` column's bracketed `reached` rate pooled over the Terms strictly before OT2025 that the table renders (OT2017 through OT2024). Weighting each Term's rate by its `n`:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled: roughly 593 grants over 11,580 weighted petitions, about **5.1%**. That is the yardstick the evaluator scores this cell against, and it is where I start.

For shape, the relist cut shows relist-0 petitions in the paid scored segment resolving denied 97.0%, granted 1.2%, gvr 0.5%, and the CVSG-none bucket resolving granted 4.0%, gvr 2.3%. The originating-court section lists the Court of Appeals of Wisconsin, District II at 8 of 8 resolved petitions denied, which is far too thin to carry weight on its own but points the same way.

## Adjustments down from 5.1% to 0.3%

The baseline band's reached rate is a mixture that includes counseled petitions with real splits that simply have not yet moved up a band. This petition has none of the features that make up the granted part of that mixture, and it has several that put it in the near-zero tail:

1. **Pro se petitioner.** The petitioner signs as his own counsel. Pro se paid petitions grant at a small fraction of the counseled rate; this alone takes most of the anchor away.
2. **Respondents waived.** The Court almost never grants without calling for a response, and a waiver on a pro se petition signals the respondents saw nothing that needed answering. A grant from this state would require a call for a response first, which would show up as a further distribution I do not expect.
3. **Posture: an untimely state appeal, an adequate and independent state ground.** The Wisconsin Court of Appeals dismissed the appeal as untimely under state law; the Wisconsin Supreme Court denied review without opinion. The petition's federal theory, that due process required the trial judge to announce the right to appeal, is the reason the appeal was late, but the dismissal rests on state procedural law, and the petition's own appendix listing suggests the federal claim was first raised in the petition for review. Vehicle problems of this kind are ordinarily fatal even to a well-presented question.
4. **No split, novel theory.** The petition asks the Court to extend the criminal-sentencing admonishment line (Rodriguez, Peguero, Garza) to civil dismissals under the Fourteenth Amendment. It cites no lower court that has adopted the rule; its long string of state cases concerns the enforceability of voluntary appeal waivers, which is a different question. It leans on Hunter v. United States, No. 24-1063, a criminal plea-agreement appeal-waiver case, as a reason to "complete the picture," which is not how the Court selects cases.
5. **Procedural history of the filing.** The petition was filed on January 2, 2026 but not docketed until May 19, 2026, after the Clerk extended time to cure the booklet format. That is common for pro se filers and not disqualifying, but it is consistent with the overall profile.
6. **Caption oddities.** The docket caption names the City of Omro while the responding party is EMC Insurance and an adjuster; the petition's own party list includes city officials and a foundation. This is the docket's real state, not a data problem, but it reinforces that the case below was a sprawling pro se tort suit rather than a clean vehicle.

I land at 0.003 rather than a hard zero because the baseline rate has a tail of unexpected grants, GVRs among them, and because I cannot rule out something on the record I have not seen. Nothing I read pushes the number up.

## The other claims

- **relist-increment 0.04.** One distribution shown, for the long conference. With a waiver on file there is no pending filing to redistribute for. The residual covers a reschedule or a mechanical redistribution from the long conference's volume, which the `dist-v2` count would register as a further distribution, plus a small chance of a call for a response. The relist cut shows most petitions are never relisted and a first relist barely raises the odds of another; from a first-conference, waived-response, pro se state is where the hazard is lowest.
- **cvsg-increment 0.001.** No federal interest; the CVSG cut's 173 cases are overwhelmingly counseled petitions touching federal law.
- **summary-disposition-route 0.6.** Conditional on any grant. Plenary review of this question is not plausible, so the conditional mass sits with a summary route, but no intervening decision of this Court supplies a GVR hook either, so I do not go higher than 0.6.
- **dissent-from-denial 0.005.** Nothing here draws a statement.
- **big_case_score 0.03.** A private tort dispute over a home; the QP would announce new constitutional doctrine if taken, but the case would resolve almost nothing beyond its facts.

## Retrieval and its limits

This is a forward cell. I ran one corpus priors query (recorded in `retrieval.md`) which returned recency-ranked resolved SCOTUS rows from the last two weeks, mostly fast-resolving matters unlike this petition, so it did not inform the number. I did not use the CourtListener MCP server: the snapshot is dated today, the conference is twelve days out, and nothing on CourtListener would change a call this far from the margin. I did not read the outcome, and I do not know it.

## Where to discount me

My number is driven by the pro se, waiver, and state-ground features, each of which I weight from general knowledge of the Court's practice rather than from a committed cut, since the statpack has no pro se or waiver cut. If the corpus later carries such cuts and they show a higher rate than I assume, my 0.003 is too low; but the structure of the anchor puts the whole band at 5.1% and I am confident this petition sits well inside its bottom decile.
