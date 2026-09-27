# Why P(grant) = 0.94, disposition GVR

## What the record shows

Provisioned inputs read: the snapshot `record/snapshots/2026-09-27.json` (as-stored, forward mode, no cutoff), `record/context.json` (band `elevated` under sal-v4, `distribution_count` 2, no CVSG, Term 2026), and all three documents in `record/documents/` — the petition (85 pages, mostly appendix), the questions-presented cut, and the brief in opposition (3 pages). None was flagged `empty_text`.

The petition, filed July 24, 2026 by Paul Clement for Monsanto, asks a single question: whether the Court should vacate the California Court of Appeal's judgment and remand in light of *Monsanto Co. v. Durnell*, decided June 25, 2026, which held that FIFRA expressly preempts a state-law failure-to-warn claim premised on the absence of a cancer warning on Roundup's label. The jury below found for Dennis only on his strict-liability and negligent failure-to-warn claims (rejecting design defect), awarding $7 million compensatory and $325 million punitive, remitted to $21 million; the Court of Appeal affirmed on the *Pilliod*/*Bates* parallel-requirements reasoning, and the California Supreme Court denied review on March 11, 2026. The petition cites two GVRs the Court issued in identical posture on June 30, 2026 (*Salas*, *Johnson*).

The docket then runs: respondent waives (July 31); distributed for the September 28 Conference (August 5); **response requested** (August 17); brief in response filed September 2; redistributed for the October 9 Conference (September 16). The response, filed "at the Court's request," is two pages of substance and states that respondent "does not oppose" the GVR, leaving *Durnell*'s application to the California court in the first instance.

## Anchors

The committed statpack (`metrics/statpack.md`) gives the leakage-safe anchor for my band: the `elevated` band's bracketed `reached` rate, pooled over Terms 2017–2025 (all nine prior rows the sal-v4 table renders), runs 13.5%–20.5% with weighted n between 275 and 400 per Term; a simple pool is about 17%. The relist-count cut puts a paid petition at two recorded distributions at roughly 41% grant-family (27.8% granted plus 13.1% GVR), though that bucket is terminal-count and mixes true relists with redistributions like this one. The modern-cert base rate is a few percent. Neither anchor describes this petition well: the population behind them is petitions asking for plenary review of an open question, and this petition asks for a GVR on a question the Court decided this June with respondent's acquiescence.

Corpus priors (`fedcourts query --court scotus --disposition gvr`) surface the closest analogs directly: *Monsanto v. Salas* (24-1097, CA11), *Monsanto v. Johnson* (24-1098, Oregon Court of Appeals) and *Monsanto v. Anderson* (25-1042, Missouri Court of Appeals), all Clement petitions, all resolved `gvr` with cert granted June 30, 2026. *Salas* and *Johnson* were held for *Durnell* (four distributions); *Anderson*, filed March 2026, went out with two. Two of the three came from state intermediate courts, so the state-court path here is no obstacle.

## Adjustments

Up, strongly, from every statpack anchor:

- The petition seeks a GVR on a controlling decision three months old, and the Court has already issued three GVRs on the same decision in the same posture, in the same wave, for the same petitioner and counsel.
- The Court called for a response after respondent waived. That is the Court's standard step before granting relief against a waiving respondent, and it is the signal the Court does not send on a petition it intends to deny.
- The court-requested response does not oppose the GVR. With both parties asking for the same order, the only obstacle would be the Court's own view that *Durnell* does not reach this judgment.
- *Durnell*'s syllabus (read on CourtListener) frames the holding as label-based express preemption under §136v(b), and the Court of Appeal opinion in the appendix rests the affirmance on the *Bates* parallel-requirements theory *Durnell* rejected. The jury found only failure to warn. I found no independent non-label ground in the opinion's preemption section that would make the GVR pointless.

Down, modestly, for the residual paths to a non-grant:

- **Denial (about 0.03).** Possible only if the Court reads the California judgment as resting on a warning theory outside the label (point-of-sale or advertising warnings). The petition characterizes the theory as label warnings and respondent did not contest that; I discount this heavily but not to zero, since I have the petition's characterization of the verdict rather than the trial record.
- **Dismissal on settlement (about 0.03).** Bayer has been settling Roundup judgments in bulk and a plaintiff facing a near-certain vacatur has reason to deal, but there are twelve days to the Conference, respondent has already conceded the GVR, and a Rule 46 dismissal in that window would be unusual.

That leaves P(any grant) ≈ 0.94, essentially all of it GVR. A summary reversal is not requested and would be gratuitous, so `summary-disposition-route` conditional on a grant is 0.97 (the remaining mass being a plenary grant or a summary reversal). I set `predicted_disposition` to `gvr`.

## The other claims

- **relist-increment 0.22.** The two distributions already on the docket are the state I forecast from. GVR candidates with conceded responses ordinarily go out at the first Conference that considers them; *Anderson* did with two distributions. A third distribution would come from a Justice preparing a dissent from the GVR (a *Durnell* dissenter could) or from the Court batching post-*Durnell* Roundup petitions, and the relist-count cut's steep hazard past the first relist is about petitions under genuine consideration, not this shape. I hold it near one in five.
- **cvsg-increment 0.01.** No federal party; the SG already participated in *Durnell*; nothing to invite views on.
- **dissent-from-denial 0.30.** Conditional on the improbable denial, some Justice writing to explain or object seems somewhat likely, because a denial against an unopposed GVR request on a just-decided question would call for explanation. Banked, not scored.

## Where to discount me

I have not read the trial record or the full Court of Appeal opinion beyond its preemption section, so the non-label-theory escape hatch is judged from the petition's own framing. I did not verify the vote lineup in *Durnell* beyond the majority author, which bears only on the unscored possibility of a noted dissent from the GVR. My grant number is far above the band anchor the evaluator will score me against; that gap is deliberate and rests on the docket's response request, the conceded response, and the three identical GVRs in the corpus, all of which predate the snapshot and are legitimate forward signal. Retrieval was six calls, well under budget; the CourtListener SCOTUS docket index returned nothing for Monsanto-party searches, so the analog set comes from the corpus rather than from live docket text.

Corpus vintage: the `query` rows carried `last_live_polled` of 2026-08-03 for the three Monsanto GVRs; the statpack's per-Term table shows OT2026 with six resolved rows, so the pooled anchor is Terms 2017–2025. Caption class for the fallback rule would be `private` (Monsanto, a corporation), but the band was frozen so the `elevated` reached rate is the anchor used.
