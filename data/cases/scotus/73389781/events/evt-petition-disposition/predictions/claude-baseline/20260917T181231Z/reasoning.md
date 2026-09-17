# Rationale for the numbers (claude-baseline, run 20260917T181231Z)

**P(grant) = 0.015; predicted disposition: denied.**

## What I read

Provisioned inputs only: the 2026-09-16 snapshot (`record/snapshots/2026-09-16.json`), `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025, `signals_observable: true`), `questions-presented.txt`, `petition.txt` (65 pages incl. appendix), and `brief-in-opposition.txt` (85 pages; roughly half is an appendix reproducing the Mississippi Court of Appeals opinion and the petitioner's appellant brief in that court). `documents.json` reports all three with `empty_text: false`, untruncated. I also read the committed `metrics/statpack.md` and ran one `fedcourts query` (see `retrieval.md`), which returned recent grants unrelated to this subject and did not move the number.

## Anchor

The context's band is `baseline` and its `salience_version` (`sal-v4`) matches the statpack's "Segment base rate by salience band (sal-v4)" table, so the anchor is the `baseline` column's bracketed `reached` rate pooled over Terms strictly before OT2025. The table renders OT2017 through OT2024 as prior rows; pooling their `reached` figures (n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271; rates 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7%) gives roughly **5.1%** over about 11,580 weighted petitions. That is the yardstick the evaluator scores skill against. For shape: the paid-segment relist-count cut puts petitions that end at zero relists at 1.2% granted plus 0.5% GVR, and the CVSG-`none` cut at 4.0% granted plus 2.3% GVR; the modern-cert overall grant family is a few percent.

## Adjustments down from 5.1%

1. **The federal question was not presented to the court that decided the case.** This is the decisive factor. The appellant's brief in the Mississippi Court of Appeals, reproduced in the BIO's Appendix B, lists as its only constitutional provision Article 3, Section 30 of the Mississippi Constitution; it cites no federal provision and neither Bearden nor Turner. The Court of Appeals opinion (BIO Appendix A) contains no Fourteenth Amendment or Turner analysis. The federal claim first appears, in a single vague sentence ("contrary to the United States Constitution and the Mississippi Constitution"), in the petition for review to the Mississippi Supreme Court, which denied review without opinion. Under Webb v. Webb and Adams v. Robertson, that is a serious jurisdictional and vehicle defect, and the petition's own "Clean federal question" and "No state-law off-ramp" assertions are not borne out by the record it attaches. The BIO makes this point, and the petition offers nothing to answer it.

2. **The petition's factual premise is contested by the order it attaches.** The QP asserts the chancery court "made no express finding as to Petitioner's present ability to pay." The BIO quotes the contempt order finding "there is no inability to pay" where the obligor "voluntarily chose to be unemployed," that she has a work history, is in good health, and could work as much as she wanted as an insurance agent; the petition itself concedes the court reasoned she "could" work. The Court of Appeals affirmed a finding that she "possessed the present ability to make payments." Whether that is a constitutionally adequate Turner finding is arguable, but the case reads as a fact-bound dispute over willfulness rather than the clean "no inquiry at all" case the QP describes. The Court does not grant to reweigh a chancellor's credibility finding.

3. **No incarceration has occurred and the sanction is a suspended coercive order.** The petitioner appealed eleven days after the order, was never jailed, and Mississippi law (Riser v. Peterson, quoted by the Court of Appeals) treats inability to pay as a continuing defense to incarceration. That blunts the "automatic" incarceration point in QP 3 and gives the Court a ripeness-flavored reason to stay out.

4. **The asserted conflict is thin.** The petition's "split" is mostly state high courts applying their own anti-imprisonment-for-debt clauses (In re Nichols, Ex parte Hall, Carter) against state statutes permitting contempt for divorce-decree obligations. That is a disagreement about state law, not a division over what the Fourteenth Amendment requires. The federal cases cited (Cain, ODonnell, Rodriguez) involve court-imposed fines and fees or pretrial detention, not private money judgments, and none conflicts with the decision below. No court of appeals decision is on the petitioner's side of a federal question.

5. **Petition-level signals are weak.** Private petitioner against a private respondent, in a divorce matter; both sides represented by small Mississippi firms with no Supreme Court practice evident; no amicus support; intermediate state appellate court below with a two-Justice vote to grant review in the state supreme court (a modest signal that does not offset the preservation defect). The petition is short and thinly argued relative to the standard of petitions the Court grants from private parties.

## Adjustments up (small)

The subject, jailing people for money debts without a Turner-compliant ability-to-pay inquiry, is one the Court has cared about and one that some Justices have written on. If the record were what the QP describes, a summary reversal would be a live possibility. That keeps me above the 0.5 to 1% floor a purely fact-bound family-law petition would earn.

Net: 0.015, roughly a third of the band anchor. Predicted disposition `denied`.

## Claims

- `disposition` 0.015: equals `probability`.
- `relist-increment` 0.12: the docket shows one distribution (for the September 28, 2026 long conference) and no relists. About a quarter of paid scored-segment petitions pick up at least one further distribution entry (the relist cut's 1, 2 and 3+ buckets against 0), but that figure counts reschedules and skews toward stronger petitions. Here a further distribution would most likely come from a Justice weighing a statement, not from grant momentum. I set it well below the population share.
- `cvsg-increment` 0.005: no federal interest at all.
- `summary-disposition-route` 0.45: conditional on a grant. No intervening decision supports a GVR, but a per curiam Turner correction is the more plausible form any grant would take on this record; the statpack's grant family runs roughly half `gvr` in Terms where the label is applied.
- `dissent-from-denial` 0.03: conditional on denial. Separate writings on denial are rare, and the chancellor's willfulness finding plus the preservation gap make this a poor vehicle for a statement.

## Big-case score

0.2. Stakes are real for the parties and the topic is nationally salient, but the case is a two-party $21,040.72 divorce dispute with no institutional participants and a record that would not let the Court reach the broad question.

## Uncertainty and where to discount me

- I have not seen the full contempt order or the Mississippi Court of Appeals opinion in their original form; I rely on the excerpts in the petition appendix and the BIO appendix. The two sides characterize the ability-to-pay finding differently, and I have weighted the BIO's quotation of the order's text because the petition does not deny that language exists.
- The preservation defect rests on the appellant brief reproduced in the BIO appendix; I did not independently verify that the reproduction is complete. If the petitioner's reply (none is on the docket as of the snapshot) shows the federal claim was in fact argued below, the vehicle improves and my number would move toward the band anchor, but not much above it.
- A relist at the long conference is somewhat more common than at ordinary conferences because of the volume the Court is working through, which is why `relist-increment` is not lower.
- The snapshot is dated 2026-09-16, one day before this run; I did not check CourtListener for later docket entries. Nothing decided about this case is on the record I read, and the conference has not yet occurred.
