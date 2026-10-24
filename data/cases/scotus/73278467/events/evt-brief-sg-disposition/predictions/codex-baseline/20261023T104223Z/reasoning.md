# Rationale

## Prediction and information set

I assign **0.88 to any grant**, including a grant, vacate, and remand, and predict **GVR**, not plenary review. This is a cert-stage, sg-brief-moment forecast in forward mode. I used the provisioned September 26, 2026 snapshot, which contains entries through September 25, and the frozen context: sal-v4 band high, Term 2025, two distributions, and a June 30, 2026 CVSG. The two distributions were November 25, 2025 and June 29, 2026; I do not treat their long separation as evidence of numerous unrecorded relists. No later docket state was retrieved.

The central input is the complete, non-OCR `sg-invited-brief.txt`, filed September 25, 2026. The Solicitor General expressly recommends **granting the petition, vacating the judgment, and remanding in light of B.P.J. and Skrmetti**, and expressly opposes plenary review at this time (pp. 1, 8–10, 17–23). The recommendation is not a denial recommendation and does not ask for a further hold. My forecast follows its proposed procedural route closely, without treating the government's merits assertions as adjudicated facts.

I also read the questions presented and relevant portions of the petition, opposition, and cert reply. The appendix is listed as truncated; I did not independently review its full contents. No document on which the forecast principally rests is flagged as empty, truncated, or OCR-derived. The opposition and reply predate the SG brief and discuss B.P.J. prospectively; I use the SG brief's account of the intervening developments rather than treating those older descriptions as current. I have no independent knowledge of this petition's disposition and encountered none during retrieval.

## Calibration

The committed `metrics/statpack.md` paid scored-segment CVSG cut contains an estimated **164 resolved petitions**, with **29.3% granted plus 5.5% GVR = 34.8% grant family**, and 15 open. That is the starting population for this moment, not the ordinary low whole-docket cert rate. The cut pools Terms and recommendations and is not a recommendation-specific success rate. As a separate cross-check, pooling all displayed sal-v4 high-band reached rows strictly before Term 2025, Terms 2017–2024, gives approximately **34.95% over weighted n=898**, calculated from the displayed rounded rates. I exclude the petition's own Term and later Terms from that cross-check. The two calibrations overlap and are not independent evidence.

These are figures from the committed roll-up available in this checkout, not a freshly queried corpus. The displayed pack provides no corpus-wide newest-pull or newest-snapshot vintage; no claim about the live corpus's current state is made. The case evidence vintage is the September 26 provisioned snapshot, with the SG document's fetch date recorded as October 18 in `documents.json`.

The large upward move from roughly 35% to 88% is a judgment about the **specific invited recommendation and proposed intervening-precedent route**, not a measured historical SG-following rate. The government identifies the panel's reliance on Fowler and Hecox, describes their subsequent treatment, and offers a limited way to return the case without deciding the disputed Turner question. Petitioners themselves request GVR as an alternative in their cert reply. This supplies a concrete grant-side exit even if the questions are poor vehicles for plenary review.

I retain 12% for a non-grant because the opposition's objections are substantive: the judgment is interlocutory, petitioners did not properly present the Turner theory below according to the panel, the purported split is contested, and the alleged abusive search conduct may not stand or fall with the equal-protection analysis. The government argues these points defeat plenary review rather than GVR, but the Court could instead leave application of intervening law to the ongoing proceedings. I do not assume a sports or medical decision mechanically resolves every detainee-search allegation, nor that vacatur of cited precedent alone proves the outcome on remand.

## Other numbers

- **Further distribution, 0.97:** measured from the snapshot's count of two. A distribution to consider the newly filed invited brief is highly likely even if the Court decides the petition at that very conference. This claim does not mean a 97% chance of a true post-conference relist. The pack's terminal relist buckets show grant-family rates of 13.4% at one relist, 40.6% at two, and 36.8% at three or more; those are not forward hazards and do not capture this post-SG scheduling state.
- **CVSG increment, 0.00:** the invitation already occurred. This required entry is vacuous and should be masked, not scored as a new forecast.
- **Summary route conditional on a grant, 0.96:** GVR is the dominant path. A direct summary reversal or a plenary grant remains possible, but the invited brief specifically prefers remand over either a fresh plenary proceeding or an immediate definitive resolution of the prison-scrutiny issue.
- **Separate writing conditional on denial, 0.20:** denial contrary to the SG's recommendation could draw a statement, but I still expect silence more often than not. This is an aggregate existence forecast, not a Justice-specific vote forecast.

The stakes score of 0.79 reflects the reach of the constitutional and correctional questions, not the chance of review. The likeliest narrow procedural disposition does not erase their wider significance.

Two general-law web searches and one official-reporter opening attempt returned no usable content. They supplied no substantive evidence. I did not query CourtListener or the corpus and did not seek this case's subsequent history.
