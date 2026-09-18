# Why 10%

## What I read

Provisioned inputs: `record/snapshots/2026-09-17.json` (the docket as polled September 17, 2026), `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025), `event.yaml` (kind `petition`, no stage recorded, so the cert standard governs), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (33 pages, full text), and `brief-in-opposition.txt` (12 pages, full text). None was flagged `empty_text` or truncated.

Retrieval beyond that: the Tenth Circuit opinion below (*Fuqua v. Santa Fe County Sheriff's Office*, No. 24-2152, published November 4, 2025) via CourtListener, searched for its treatment of the Sixth Circuit rule and the dissent; the CourtListener docket record for this case (last modified July 29, 2026, no entries beyond the snapshot); two `fedcourts query` corpus pulls; and the committed `metrics/statpack.md`. Details in `retrieval.md`.

## The anchor

Context freezes the band as `elevated`, so the yardstick is the bracketed `reached` rate for `elevated` in the statpack's "Segment base rate by salience band (sal-v4)" table, pooled over Terms strictly before OT2025. The table renders OT2017 through OT2024 (eight prior Terms):

| Window | Pooled `elevated` reached rate | n |
| --- | --- | --- |
| OT2017-OT2024 | 17.2% | 2810 |
| OT2020-OT2024 | 18.1% | 1729 |

So the starting point is roughly 17%. The statpack's relist-count cut for the paid scored segment is consistent: a terminal relist count of 1 runs about 13% grant family (8.2% granted plus 5.1% GVR), against 1.7% at zero relists.

## Why I adjust down, to 10%

1. **The second distribution is not a relist.** The May 5 distribution was for the May 21 conference; on May 15 the Court called for a response, which removes the petition from that conference. The July 29 distribution for September 28 is the first time the petition will actually be considered. The statpack itself warns that the stored count is an upper bound on true relists because a redistribution before first consideration adds an entry. The `elevated` band here is therefore carrying a call-for-response signal dressed as a relist. A call for response is a real positive signal (some chambers wanted the respondent's side), and it moves this petition well above the paid-docket rate of about 4%, but in my judgment it sits below the population of petitions that reached `elevated` by an actual post-conference relist.

2. **The Tenth Circuit's alternative holding undercuts the vehicle.** The petition presents Question 1 as a clean methodological split. But the majority opinion, at page 15, holds that "even if we apply the Sixth Circuit's rule, the videos do not 'blatantly contradict or utterly discredit' the complaint," walking through the footage and citing the Sixth Circuit's own *Chrestman* and *Bell* decisions. The brief in opposition leans on exactly this. A grant on Question 1 would not change the outcome on the panel's own reading, which is the kind of vehicle defect the Court routinely treats as disqualifying for a split-resolution grant.

3. **The split is contestable.** The Tenth Circuit distinguished *Bailey* (complaint referenced the video, so incorporation by reference), *Saalim* (video consistent with complaint, not considered), and *Chrestman* (videos considered but found not contradictory). The Eleventh Circuit's *Johnson v. City of Atlanta* is the strongest contrary authority. This reads as a two-versus-one disagreement with one side's cases partly explainable on incorporation grounds. The Court often lets such a split percolate.

4. **Questions 2 and 3 are error correction.** Both are argued from the omitted facts (the BB gun, the gunfire, the occupied vehicle), which under the Tenth Circuit's ruling are not before the court at the pleading stage. As pleaded (an unarmed suspect shot in the back while fleeing), *Garner* is close to the paradigm case, so the Question 3 "high level of generality" argument only has force if Question 1 is resolved for petitioners first.

5. **No amicus support, non-specialist counsel, and a changed complaint.** No amicus brief was filed in support of the petition (the docket shows none through September 17), which is unusual for a law-enforcement petition that claims a recurring national problem. Counsel of record is the New Mexico Association of Counties, not a repeat Supreme Court advocate, and no reply brief appears on the snapshot. The brief in opposition also reports that the district court has since allowed a Third Amended Complaint adding the chase and the BB gun, which muddies what pleading the Court would be reviewing and blunts the "strategic omission" framing of Question 2.

## Why I do not go lower

- The Court called for a response after the respondent waived, and that petition then drew a full brief in opposition; the petition is at the long conference in a fee-paid posture with a published, reasoned opinion and a dissent by a former chief judge of the circuit.
- The qualified-immunity and police-shooting genre is one where this Court has repeatedly intervened, sometimes summarily, and the question of extending *Scott v. Harris* to the pleading stage is genuinely open and recurring as body-camera footage becomes universal.
- The brief in opposition is short and largely fact-argumentative; it does not seriously contest that the Tenth Circuit declined to adopt the Sixth Circuit rule.

Netting those, 10% for any grant. `predicted_disposition` is `denied` because that is the modal outcome by a wide margin.

## The other claims

- **relist-increment 0.22.** From a functionally first-conference state, another distribution requires either a Justice writing, a serious grant look, or a hold. With a 10% grant chance (most modern grants follow a relist) plus some chance of a statement or a second look, about a one-in-five chance of a further distribution.
- **cvsg-increment 0.02.** No federal interest; a CVSG on a section 1983 qualified-immunity petition against county deputies would be very unusual.
- **summary-disposition-route 0.30 (conditional on grant).** The genre favors per curiams, but the threshold video-consideration question plus the alternative holding make a summary reversal awkward, and there is no intervening decision to GVR on. Plenary review is the likelier grant shape.
- **dissent-from-denial 0.07 (conditional on denial).** Possible from a Justice who has written on the costs of denying qualified immunity early, but the alternative holding gives a clean reason for a silent denial.

## Uncertainty and where to discount me

- I cannot see what prompted the call for response; if it came from a chambers seriously considering a grant rather than a routine request for an adversarial presentation, my number is too low.
- I have not read the district court opinion or the appendix, and I did not view the videos; my read of the alternative holding is from the Tenth Circuit's text.
- The corpus queries I ran returned little of use (a citation lookup on *Garner* matched nothing because that column is sparsely populated, and a recency-ranked granted-disposition pull surfaced mostly applications), so the corpus priors did not move the number; the statpack tables did the anchoring work.
- No outcome for this petition exists yet; the September 28 conference is eleven days after the snapshot. Nothing I retrieved postdates the snapshot for this case.
