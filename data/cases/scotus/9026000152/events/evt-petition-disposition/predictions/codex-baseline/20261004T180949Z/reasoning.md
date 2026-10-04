# Basis for the prediction

## Record and information boundary

This is a forward, cert-stage distribution cell for Dora L. Adkins v. Rosslyn Syndicate, LC, docket 26-152. I read the event definition, the provisioned `record/snapshots/2026-10-04.json`, `record/context.json`, and all three provisioned document files: `documents.json`, `questions-presented.txt`, and `petition.txt`. The frozen context supplies Term 2026, salience version `sal-v4`, band `baseline`, one distribution, and no CVSG. I use that conditioning directly. The snapshot is as stored with no cutoff, not a reconstructed first-distribution snapshot.

The petition is a paid filing, expressly presented pro se. I do not apply an IFP base rate or treat self-representation as a substitute for reading the petition. The snapshot records a May 8 petition and motion to expedite, an August 14 supplemental brief, and a September 16 distribution for the October 9 conference. It records no BIO or requested response. Silence here means only that those entries are absent from this snapshot, not that the respondent conceded anything or that the docket could not later change.

The document manifest reports nine petition pages, untruncated and with nonempty extracted text. The appendix is separately linked in the snapshot but is not provisioned; neither is the supplemental brief's text. Thus the lower courts' reasoning and the precise show-cause order are known only through the petitioner's account. No BIO text was supplied, and I cannot weigh an opposition that I have not read. These limitations are recorded in `flags.json`.

## Anchor and adjustment

The committed `metrics/statpack.md` publishes a matching `sal-v4` segment table. For the frozen `baseline` band, I pool the bracketed reached rates across every displayed strictly prior Term, 2017 through 2025, excluding 2026. Using the corresponding unrounded `prefix_est_grant_rate` and `prefix_weighted_resolved` fields in `metrics/statpack.json` gives 638 weighted grants over 12,720 weighted resolved petitions, or 5.0157%. This is the private-petitioner risk set, including petitions that subsequently strengthened into higher trajectory bands, not the much lower terminal-baseline rate. These are the committed pack's estimates, not a newly refreshed corpus census; no live corpus vintage or case `last_pulled` was retrieved. The case-specific evidence is the October 4 snapshot and documents fetched that day.

For population context, the modern-cert table reports 655 grants plus 577 GVRs among 43,700 weighted resolved petitions, roughly 2.82%. That broad figure is not my scored anchor. The Fourth Circuit cut reports 1.3% granted and 1.2% GVR among 3,370 weighted resolved petitions; it likewise is not a substitute for the band-conditioned population. The paid-segment terminal relist buckets show grant-family shares of approximately 1.7%, 13.3%, 40.9%, and 36.8% for zero, one, two, and three-plus relists. The CVSG cut shows approximately 6.3% without a CVSG and 34.9% with one. These terminal categories describe population shape and cannot directly estimate the future relist or CVSG hazard from this cell's current state.

I adjust sharply downward from the 5.02% anchor to **P(any grant) = 0.3%** because of the actual petition's presentation:

- Questions I, III, IV, and V largely ask whether the courts correctly handled this individual's affirmance, rehearing, emergency motions, and proposed pleadings. The petition supplies no competing appellate decisions establishing a legal conflict.
- The petition's `Opinions Below` section describes the appellate opinion and district court orders as unreported. Its table of authorities cites its own litigation rather than a body of conflicting precedent. These are concrete weaknesses in the record presented, not proof that no relevant authority exists elsewhere.
- Question II is the strongest potential general issue, concerning due process and a show-cause order. But the petition's statement of the case says that, as of April 30, no final ruling on that order had issued. On that account, the asserted denial of an opportunity to respond is not clearly established merely by simultaneous affirmance and initiation of a show-cause process. I do not assume either that a restriction was later imposed or that the process was legally adequate.
- The alleged chemical exposure and need for emergency relief could be very serious for the petitioner. They are allegations, however, and the supplied materials do not turn the underlying factual dispute into an identified nationally recurring conflict. The motion to expedite is the petitioner's request, not an affirmative indication of Court interest.

The downward adjustment is judgmental, not a fitted estimate for pro se petitions or this litigant. I retain nonzero probability because the missing appendix and supplemental brief could reveal a more substantial procedural problem than the petition alone establishes. I have no prior knowledge of this petition's eventual disposition and did not seek it.

## Other probabilities and stakes

The 3.5% chance of another distribution allows for additional consideration or scheduling changes while making zero further distributions the modal path. It is an increment above the one already shown, not a prediction of the terminal count. The 0.1% CVSG forecast reflects the absence of a developed federal-government interest or a demonstrated legal conflict in the materials supplied, rather than treating the existing absence of a CVSG as conclusive.

The 30% summary-route forecast is conditional on a grant. No intervening authority was identified in the supplied petition to motivate a GVR, so plenary consideration of the procedural question is the more plausible of the rare grant paths; summary correction remains a minority possibility. The 0.3% separate-writing forecast is conditional on denial and concerns existence only. Neither conditional probability is multiplied by the grant or denial probability in the structured claims.

The significance score of 0.13 reflects limited apparent systemic reach on this record, independently of the very low grant probability. A broad decision on safeguards for filing restrictions could matter beyond this litigant, but the questions presented and available account are dominated by an individual dispute. I do not equate low public significance with low personal stakes.

## Retrieval and execution limits

Two general-law web calls sought Supreme Court certiorari guidance, without searching this litigant or docket. Both returned no usable content. No web-derived legal proposition or case outcome informs the forecast. I used no CourtListener lookup and no live corpus query; the provisioned petition and committed statpack were sufficient for this conservative forecast. The complete retrieval accounting is in `retrieval.md`.

The first `fedcourts paths` invocation failed because the default uv cache location was read-only. Redirecting the cache to `/tmp/uv-cache` allowed the path resolver to succeed without changing repository code or inputs.
