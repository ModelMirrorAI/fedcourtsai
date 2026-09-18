# Rationale for the numbers

**P(grant) = 0.012; predicted disposition denied.**

## Inputs I read

- Snapshot `record/snapshots/2026-09-17.json` (the one `context.json` names). Paid docket No. 25-1340, Fifth Circuit (No. 25-20079), unpublished per curiam decision December 12, 2025, rehearing denied January 23, 2026. Extension application granted by Justice Alito; petition filed May 26, 2026 (docketed June 1); response due July 1, 2026; distributed July 15, 2026 for the September 28, 2026 conference. No brief in opposition, no waiver, no amicus, and no call for a response appears on the record.
- `record/context.json`: mode `forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, cutoff null.
- `record/documents/questions-presented.txt` and `record/documents/petition.txt` (40 pages, text extracted, not truncated). `documents.json` lists no brief in opposition, which matches the docket: none has been filed.
- `metrics/statpack.md`: the modern-cert disposition table, the circuit cut, the relist and CVSG cuts, and the sal-v4 "Segment base rate by salience band" table.

## Anchor

The context froze `band: baseline` under sal-v4 and the statpack's band table is computed under sal-v4, so the anchor is the `baseline` band's bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling OT2017 through OT2024 (the eight prior Terms the table renders, n = 1271, 1312, 1192, 1500, 1739, 1399, 1524, 1643) gives 592.9 weighted grants over 11,580, or **5.1 percent**. That is the rate for a paid petition that has reached the weakest band and might still climb, and it is the yardstick my skill is scored against.

## Adjustments from the anchor

I adjust well down, to about 1.2 percent, for reasons that are all visible in the provisioned record:

- **Weak vehicle.** The decision below is an unpublished per curiam affirmance of summary judgment, expressly not designated for publication. The Court rarely takes unpublished dispositions, and the panel's holding rested on applying existing circuit precedent (Hager v. Brinker, Arguello v. Conoco) to one plaintiff's facts.
- **No genuine split shown.** The petition's own split section concedes the circuits "have not reached a consensus, to the extent that they have reached the issue," and the cases it cites (Second, Fourth, Sixth Circuit) articulate "markedly hostile" style standards rather than squarely rejecting the Fifth Circuit's "force the patron to leave" formulation. The question presented is drafted around the petitioner's facts rather than as a legal rule.
- **Error-correction framing.** Part I asks for summary reversal for misapplying the summary-judgment standard. Tolan v. Cotton shows the Court occasionally does this, but it is rare, and the disputed facts here (whether the shawl was placed "quietly" or "forcibly", how long she stayed) go to elements the panel did not actually decide against her; the panel resolved the case on the third prima facie element as a matter of law.
- **No opposition, no amici, no repeat-player counsel.** The respondent did not file a brief in opposition and the Court distributed on the response deadline without calling for one. Counsel is a Houston civil-rights solo practitioner rather than a Supreme Court specialist. None of these markers is decisive, but together they describe the bottom of the baseline band, not the part of it that later relists into `elevated`.
- **Circuit cut.** The Fifth Circuit's modern grant family (granted plus GVR) is about 3.7 percent, in line with the docket overall; no adjustment from it.

The residual 1.2 percent covers a Tolan-style summary reversal on the Rule 56 point, or a small chance that a Justice pushes the case to a call for a response and then a grant. I see no pending or recent decision of the Court that would supply a GVR.

## Other claims

- **relist-increment 0.15.** The paid scored segment's terminal relist distribution says about a quarter of petitions record at least one further distribution, but that figure is an upper bound (reschedules count) and is dominated by petitions with a response on file. For an unopposed petition at its first distribution to the long conference, a second distribution mostly means a call for a response or a long-conference reschedule; I put it below the segment share.
- **cvsg-increment 0.005.** Private parties, no federal interest.
- **summary-disposition-route 0.6.** Conditional on any grant, the summary route dominates because the petition seeks it and the plenary vehicle is poor; the modern-cert table's GVR-versus-granted split (577 to 655) shows roughly half of grants resolve in the cert order in the population, and this case's specifics push above that.
- **dissent-from-denial 0.04.** Dissents or statements respecting denial are rare and concentrate on published, consequential decisions; the racial-indignity fact pattern gives a small chance of a statement.

## Retrieval and its effect

I ran one `fedcourts query` for 2020s granted SCOTUS priors; it returned substantive applications and a state criminal case, none comparable, so it did not move the number. CourtListener confirmed the docket is still open (no termination date) and carries no docket-entry rows, so the snapshot is the only entry-level record; a search for a Supreme Court docket in Hager v. Brinker returned nothing, so I have no evidence that the Fifth Circuit's controlling precedent was itself tested here.

## Where to discount me

The main uncertainty is whether the Court views the panel's factual recitation as a Tolan-type failure worth a per curiam correction; I weight that low because the panel's legal holding did not depend on the disputed facts, but a reader who reads Part I of the petition more favorably would put the number nearer 2 to 3 percent. I did not read the prior-run predictions in the sibling directories; this forecast is from the current record alone.
