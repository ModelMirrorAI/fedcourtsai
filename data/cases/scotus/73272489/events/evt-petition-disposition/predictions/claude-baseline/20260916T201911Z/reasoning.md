# Reasoning — why P(grant) = 0.005

## What I read

- `record/snapshots/2026-09-16.json` (the provisioned baseline): a paid petition, No. 25-1235, from the Court of Appeal of California, Second Appellate District (No. B334226, unpublished opinion of August 18, 2025; rehearing denied September 3, 2025; California Supreme Court review denied November 19, 2025). Docketed April 30, 2026. Two docket entries: the petition filed February 9, 2026 (response due June 1, 2026) and a June 17, 2026 distribution for the September 28, 2026 conference. No brief in opposition, no waiver, no amicus.
- `record/documents/questions-presented.txt` and `petition.txt` (24 pages, text extracted, not truncated). The petitioner is a self-represented homeowner suing Long Beach for flood damage from a storm-water pump in February 2019. The petition complains that the trial judge excluded a 2005 stormwater report and deposition transcripts, barred impeachment of the city's witness with prior inconsistent statements, and was biased, and it frames these as due-process and confrontation violations, citing the Federal Rules of Evidence and Civil Procedure against a California state trial.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025, `signals_observable` true.
- `metrics/statpack.md`: modern cert base rates, the relist and CVSG cuts, the originating-court cut, and the per-Term segment base rate by salience band.
- No brief in opposition was provisioned because none has been filed; my read of the respondent's position is that the city has not engaged, which is itself typical of a petition the Court will deny without calling for a response.

## Anchor

The band is `baseline` under `sal-v4`, which matches the statpack table's version. Pooling the bracketed `reached` rate over Terms strictly before this case's Term (2017 through 2024) gives about 5.1 percent over a weighted n of roughly 11,600. That is the yardstick the evaluator scores against, so it is my starting point.

## Adjustments

Every case-specific signal points down, and steeply:

- **Pro se petitioner, no federal question properly presented.** The question presented is a grievance narrative, not a legal question. The federal hooks are the Federal Rules of Evidence and Civil Procedure, which do not govern a California state trial, and the Sixth Amendment, which does not apply to civil cases. What remains is a fact-bound state-law evidentiary dispute with an adequate and independent state ground.
- **Unpublished state intermediate appellate opinion, no split alleged.** The statpack's originating-court cut for the Court of Appeal of California, Second Appellate District shows granted 0.7 percent and gvr 4.6 percent over 153 resolved rows; the gvr share there is driven by criminal petitions held for intervening decisions, none of which bears on this case.
- **No response and no waiver, no amicus.** The Court has not called for a response; the respondent has not bothered to file one. This is the shape of a petition denied at first conference.
- **The 5.1 percent anchor is a risk-set rate** that includes the baseline petitions that go on to relist or draw a response. This petition has none of those features, so it sits well below its band's floor. The corpus `query` on denied 2020s SCOTUS rows returned several self-represented petitioners in the same posture, while every granted row was carried by experienced Supreme Court counsel; that confirms the qualitative direction, not a number.

I land at 0.005. I would defend anything between 0.002 and 0.01; I do not go lower because the baseline band's committed rate is the scored yardstick and a paid petition retains a small structural chance of a hold or clerical relist that a bare denial forecast would not see.

## Claims

- `disposition` 0.005, equal to the top-level probability.
- `relist-increment` 0.08. From one distribution, the relist-count cut shows most paid scored petitions end at zero relists. A pro se state tort petition has no hold candidate; the residual is a reschedule of a long-conference item.
- `cvsg-increment` 0.002. No federal interest of any kind.
- `summary-disposition-route` 0.6, conditional on a grant. If the Court granted at all, a summary order is the more plausible form than plenary review, since there is no vehicle for argument; but no intervening decision exists to GVR against, so the conditional is not higher.
- `dissent-from-denial` 0.01. Nothing here draws a separate writing.

## Stakes

`big_case_score` 0.03: a two-party local negligence dispute with no reach beyond the litigants.

## Uncertainty and where to discount me

The provisioned snapshot is dated today and matches the supremecourt.gov docket structure; CourtListener's docket-entries endpoint returned no rows for this docket, so I could not independently confirm that no waiver or response was filed after June 17, 2026. That does not change the forecast. I have no outcome knowledge of this case; the conference has not yet occurred.
