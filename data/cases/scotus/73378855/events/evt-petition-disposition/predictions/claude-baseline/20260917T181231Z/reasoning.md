# Rationale for the numbers

**P(grant) = 0.01; predicted disposition: denied.**

## What I read

Provisioned inputs only, plus one corpus query and the committed statpack. I read `record/snapshots/2026-09-16.json` (the baseline named in `context.json`), `context.json` (mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025), `event.yaml` (kind `petition`, no stage recorded, so cert-stage at the distribution moment), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (15 pages, text extracted), and `brief-in-opposition.txt` (32 pages including appendices, text extracted). `documents.json` shows none of them flagged `empty_text` or truncated.

## Anchor

Band is `baseline` under `sal-v4`, which matches the statpack's *Segment base rate by salience band (sal-v4)* table, so the table is my anchor. Pooling the bracketed `reached` figure for `baseline` over the eight Terms the table renders that are strictly before Term 2025 (2017 through 2024) gives about 593 grants over a weighted n of 11,580, roughly 5.1%. That is the yardstick this cell's skill is scored against. The terminal-band figures for `baseline` in those Terms run 0.6% to 1.8%, which is the rate among petitions that never escaped the band; a petition that is in fact never going to relist behaves like that population.

## Adjustments, all downward

- **Pro se petitioner, paid docket.** The petition is filed by the petitioner himself, a disbarred Alabama lawyer (the BIO says so; the petition's own caption calls him pro se). Pro se paid petitions are granted at rates well below the paid segment's average, and nothing here distinguishes it from that class.
- **The legal theory is foreclosed by the Court's own precedent.** Question 1's premise, that a no-opinion affirmance of a punitive award violates due process, runs straight into the TXO plurality, which held that a trial judge's failure to articulate reasons for denying remittitur is not a constitutional violation after an adequate hearing. The BIO quotes it. Cooper Industries requires de novo appellate review, not a written opinion. No lower-court conflict is alleged.
- **The facts undercut the excessiveness claim.** By the petitioner's own numbers ($200,000 mental-anguish verdict plus a $160,696 summary-judgment award, against $800,000 punitive) the ratio is about 2.2 to 1, squarely within the single-digit range State Farm treats as presumptively acceptable, and the conduct found was conversion of trust funds under false pretenses. The remittitur transcript in the BIO appendix shows the trial judge addressing reprehensibility and ratio on the record.
- **Weak vehicle.** The petition is nine pages of argument, there is no reasoned opinion below, the petitioner did not appear at trial or at the remittitur hearing, and the BIO reports he has not satisfied any of the judgments. The docket also shows the petition dated January 8, 2026 but not docketed until May 21, 2026, consistent with an initially defective submission.
- **No signal of interest.** One distribution for the long conference, no relist, no amici, no CVSG. The plaintiff-respondent Watts did not file a BIO at all; the only opposition came from a co-defendant who says he has no direct interest in the award.

Taken together this petition is materially weaker than the median `baseline`-band paid petition, so I sit near the floor of the band's terminal-figure range rather than at the 5% reached-rate anchor. I did not go below 0.01 because a residual grant-family probability (mainly a GVR should some intervening punitive-damages decision issue before the conference) is never quite zero, and because one distribution is not yet a denial.

## Claims

- `disposition` 0.01, as above.
- `relist-increment` 0.10. Forecast from one distribution. The statpack's relist cut shows roughly a quarter of paid scored petitions end with at least one further distribution entry, but that pool is dominated by petitions a Justice is actually considering, and the count is an upper bound that includes reschedules. For a petition of this shape the hazard is mostly the clerical or reschedule residue at the long conference.
- `cvsg-increment` 0.005. No federal interest of any kind.
- `summary-disposition-route` 0.55, conditional on a grant. Nothing recommends this record for argument, so if the Court acted at all it would more likely be by GVR or short per curiam than by plenary review; the prior Terms' cert-order share of the grant family runs roughly 30% to 59%, and I sit above the middle of it for this case.
- `dissent-from-denial` 0.01. Separate writings on denial of pro se punitive-damages petitions from state courts are very rare, and the Justices skeptical of the Gore line favor denial here.

## Big-case score

0.05. Private dispute, modest sum, no doctrinal novelty, no institutional party.

## Retrieval and uncertainty

One `fedcourts query` for recent SCOTUS grants (recorded in `retrieval.md`) returned only well-lawyered, amicus-backed, multiply distributed petitions and emergency applications, which confirms by contrast how far this docket is from the granted population but adds no closely comparable prior. I made no CourtListener MCP calls; the forecast does not depend on anything outside the provisioned record. Where a reader should discount me: I cannot see whether a recently decided or pending Supreme Court case on punitive damages could make this docket a GVR candidate, and I have not checked for one. That is the main upside risk to a 1% number.
