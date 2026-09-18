# Why 0.18

## Inputs read
- `record/snapshots/2026-09-17.json` (the provisioned baseline), `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, term 2025), `event.yaml`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (30 pp), `brief-in-opposition.txt` (25 pp); none flagged `empty_text` or truncated.
- Beyond the provisioned inputs: the petitioner's August 18 reply brief (fetched from supremecourt.gov, text extracted locally), one `fedcourts query` for recent granted SCOTUS priors, and the committed `metrics/statpack.md`. Two CourtListener MCP lookups for the related Sixth Circuit petition returned no rows. Details in `retrieval.md`.

## Anchor
The context band is `elevated` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so that table is my anchor. Pooling the bracketed `reached` figure for `elevated` over the eight Term rows strictly before OT2025 that the table renders (OT2017 to OT2024):

| pooled Terms | weighted n | reached grant rate |
| --- | --- | --- |
| 2017-2024 | 2810 | 17.2% |

That is the population this petition is in (it reached `elevated`, and may yet reach `high`), and it is the yardstick the evaluator scores against. For reference, the modern-cert overall grant family is a few percent and the `baseline` band's pooled reached rate is ~5%.

I did **not** anchor on the relist-count cut's `1` bucket (granted 8.2%, gvr 5.1%) even though `distribution_count` is 2. The second distribution is the routine redistribution after a call for response; the petition has been considered at zero conferences. The statpack itself warns the count is an upper bound on true relists. The CFR is the real signal here, and the band already folds it in.

## Adjustments up from 17%
- **A genuine, mature, conceded split.** Fifth, Ninth, and D.C. Circuits (with the Tenth strongly implied) against the Eighth Circuit and now the Arkansas Supreme Court (with the Sixth implied). The BIO does not deny the split exists on the discrimination question; respondent conceded it below. The 5-2 division in the Arkansas Supreme Court tracks the split exactly.
- **Final judgment, clean posture, expert counsel.** The petition is by the UCLA Supreme Court Clinic (Stuart Banner), which picks vehicles carefully, and it pre-empts the obvious objection that the Court denied the issue in Fleming (2010) by noting Fleming's interlocutory posture.
- **The BIO's vehicle argument is legally weak.** Its "independent grounds" point conflates alternative grounds for *other claims against other defendants* (the section 1983 and state-law counts) with an adequate independent ground for the judgment on the section 504 count; the reply's Coleman v. Thompson answer is correct. The BIO also does not engage the reasoning of the circuits on the other side.
- **Court appetite.** The Court has recently taken modest-stakes disability-statute coverage questions (Stanley v. City of Sanford and A.J.T. v. Osseo in OT2024; Cummings in OT2021), so small dollars alone do not sink a clean statutory split.
- **The call for response** shows at least one chambers flagged the petition. This is already inside the band, so I count it only lightly.

## Adjustments down
- **The QP does not match the case.** The petition asks about independent contractors suing "for discrimination"; the case is a *retaliation* claim by a *non-disabled parent* who was an *employee of a staffing agency*, not a contractor of the district. The reply concedes the "for discrimination" words are "superfluous". To reach the QP the Court would have to assume section 504 supplies a private retaliation claim to a non-disabled associate, an antecedent question the Sixth Circuit has answered in the negative (Smith v. Michigan Dep't of Corrections, per the BIO), and which the BIO says this Court declined to review in June 2026. Justices are reluctant to grant where the headline question sits on top of an unsettled threshold question the parties did not litigate below. This is the largest downward factor.
- **Stakes and support.** A $7,000 general verdict, a parent-teacher dispute, no amicus brief at the cert stage despite a split the petition says has been "a frequent topic of analysis in the law reviews". For a claimed important question, silence from the disability-rights bar is informative.
- **State-court origin, general verdict.** Even if the section 504 holding were reversed, the undifferentiated damages award and vacated injunction would complicate the remedy; the Court sometimes prefers to wait for a federal-court vehicle where the split is between federal circuits.
- **The Court passed once before** (Fleming, 2010), though on an interlocutory posture.

Net: the split is real and the counsel is strong, which would ordinarily carry an `elevated` petition above its band rate; the vehicle mismatch and the lurking retaliation-standing question pull it back. I land almost on the anchor, marginally above: **0.18**.

## The other claims
- `relist-increment` 0.30: the Court's practice of relisting before granting means P(relist) is bounded below by roughly P(grant); I add ~0.12 for relists that end in denial (a possible statement, a vehicle re-check). The statpack's relist cut buckets by terminal count, so it gives shape rather than this hazard.
- `cvsg-increment` 0.09: the segment-wide CVSG rate is about 1% (173 of ~13,900 in the paid scored segment), but this is a serious petition about a federal statute the government administers and is itself sued under, so the conditional rate is several times that. Not higher because the Court more often just decides such splits.
- `summary-disposition-route` 0.04: nothing to GVR against; a split is resolved by argument.
- `dissent-from-denial` 0.05: statutory, non-ideological, no amici.

## Where to discount me
- I could not verify the disposition of the related Sixth Circuit petition (the BIO's No. 25-1028) on CourtListener; I have taken the BIO's footnote at face value. If it is wrong, the downward vehicle adjustment is somewhat overstated.
- The pooled band rate is over eight Terms; the two most recent rows (13.5% for OT2025 excluded as the case's own Term; 17.9% for OT2024) suggest a rate near the pool, so the choice of window does not move the anchor much.
- I have no view of the conference itself; a single interested chambers can produce a relist and a CVSG that would move this number materially after the fact.
- `big_case_score` 0.25 rests on the QP, posture, and parties only.
