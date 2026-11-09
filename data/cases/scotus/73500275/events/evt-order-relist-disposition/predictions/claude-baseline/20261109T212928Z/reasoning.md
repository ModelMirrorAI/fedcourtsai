# Reasoning: ON24, Inc. v. Leadersel Innotech ESG, No. 25-1376 (first-relist moment)

**P(any grant, GVR included) = 0.33. Predicted disposition: denied, but a GVR after a hold for Robinhood is the main way this petition gets granted.**

## What the record shows
- Snapshot `2026-11-09.json`: a paid petition from an unpublished Ninth Circuit memo (Jan. 7, 2026; en banc rehearing denied Mar. 9, 2026, with no noted dissent per `lower-court-docket.txt`). The memo reversed the dismissal of Section 11 claims on five of six statements and remanded, so the posture is interlocutory.
- Respondent waived a response. The petition was distributed for 9/28, and the Court called for a response on 7/22. The BIO came in on 9/21 and the reply on 10/6. The petition was distributed for 11/6, then distributed again for 11/13 on 11/9. That last entry is the relist that opens this cell. `context.json`: band `elevated` (sal-v8), `distribution_count` 3, no CVSG. The 9/28 distribution was overtaken by the call for a response, so 11/6 was the first real conference and this is a true first relist.
- Documents read: QP file, petition (truncated at the cap, appendix side), BIO, cert reply, decision below. Counsel of record for petitioners is Brian Matsui of Morrison & Foerster.

## Decisive outside fact: the Robinhood companion
The petition, BIO and reply all tie QPs 2–3 to *Robinhood Markets, Inc. v. Sodha*, No. 25-944. In that case the Ninth Circuit itself vacated submission here pending its *Sodha* ruling. I fetched the 25-944 docket from supremecourt.gov (forward mode, so this is allowed):
- The Court called for the SG's views on 6/1/2026, and the SG filed on 10/7/2026. Per a search snippet, the SG recommends **granting Robinhood's first question**, which is the Section 11 misleading-omissions prong without asking whether an affirmative statement was rendered misleading. ON24's QP2 mirrors it.
- Robinhood was distributed for 11/6 and then for **11/13**, the same two conferences as this petition. The two are moving in lockstep.

This is not a `Vide` link (`record/related/` is absent and `vide_links` is empty). The connection comes from the parties' own briefs and the public docket.

## Number
- Anchor: `cert_anchor.rate` = 0.251 (band `elevated`, 10-Term lookback). Cross-check against the statpack relist cut (paid scored segment): bucket 1 has n≈2,532 resolved with a grant family of 13.5%. Buckets 2 (n≈495) and 3+ (n≈483) have grant families of about 41% and 37%. The CVSG cut (Robinhood's situation, not this one's) has a grant family of about 35%.
- Decomposition:
  - P(Robinhood granted) ≈ 0.75, given the SG supports a grant and the Court relisted it after the SG brief.
  - If Robinhood is granted, P(ON24 held) ≈ 0.7, and P(ON24 granted outright on QP1) ≈ 0.05. QP1 is the *Facebook v. Amalgamated Bank* risk-disclosure issue, which the Court took and then dismissed as improvidently granted in 2024. The interest is real, but this is an unpublished interlocutory memo whose fact-bound "risk had begun to materialize" finding is the same vehicle trouble that sank *Facebook*.
  - If ON24 is held, P(GVR) ≈ 0.55. That is P(Robinhood reverses) ≈ 0.65 × P(the Court GVRs a held case given a reversal) ≈ 0.85. The BIO's argument that the panel did run the Macquarie "renders misleading" analysis could support a plain denial even after a pro-issuer Robinhood ruling.
  - If Robinhood is denied, ON24's grant chance is about 0.05.
  - Total ≈ 0.75 × (0.7 × 0.55 + 0.05) + 0.25 × 0.05 ≈ 0.34, which I round to 0.33. That sits a little above the band anchor because of the companion signal.
- Uncertainty: I did not read the SG brief itself, only a search snippet of its recommendation. Whether the SG backed both Robinhood questions or only the first matters little, since ON24's QP2 tracks the first. Held petitions often end in denial when the lead case is distinguishable, and the timeline runs to about June 2027.

## Increments
- Relist: if ON24 is held, or Robinhood is relisted again, ON24 will be distributed again. It is denied outright at 11/13 only if the Court denies Robinhood or chooses not to hold. I put that at ≈0.25, so relist-increment = 0.75.
- CVSG: the Court will not call for the SG's views twice on the same question while the SG has just filed in the companion case, so 0.02.
- Summary route | grant: almost every grant path here is a hold-then-GVR, so 0.82.
- Dissent from denial | denial: business-securities petition, so a dissent is unlikely, at 0.04.
