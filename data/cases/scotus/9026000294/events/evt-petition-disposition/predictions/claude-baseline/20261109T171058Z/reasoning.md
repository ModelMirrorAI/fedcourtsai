# Reasoning — Owens v. Taliban, No. 26-294 (P(grant) = 0.30)

## Inputs
- Snapshot `record/snapshots/2026-11-09.json` (forward mode, no cutoff). I also checked the Court's live docket page on 2026-11-09; it matches the snapshot.
- `record/documents/petition.txt` and `questions-presented.txt`, both read. `lower-court-docket.txt` says en banc rehearing was denied. Its "dissent noted: no" is wrong: the petition's appendix shows five judges dissenting from the en banc denial (Sullivan, J., joined by Livingston, C.J., Bianco and Park, JJ.; Menashi, J., separately). I go with the petition's appendix. No decision-below text was staged.
- No brief in opposition. The respondent, the Taliban, has filed nothing: no response and no waiver. The one amicus brief on this docket is from Afghanistan's pre-Taliban UN mission chargé (VIDED across all three dockets).
- `record/related/`: 26-292 (Havlish) and 26-293 (Ashton), both `Vide` companions from the same consolidated Second Circuit judgment. Havlish also has an amicus brief from Iowa and other States, and a motion for leave to file a supplemental brief (Oct 30). The live dockets show all three redistributed on Nov 9 for the 11/13 conference.
- `same-question.json` lists no other petitions above the threshold.

## Anchor
`context.json` gives band `elevated` (sal-v8) and `cert_anchor.rate` = 0.248, pooled over 10 prior Terms. In the statpack's elevated-band table, the per-Term reached rates run 21–28%, which agrees. Cross-checks: the relist-count cut has bucket 1 at 8.3% grant + 5.2% GVR (n≈2,532) and bucket 2 at 28.3% + 12.9% (n≈495). The amicus 1-brief bucket is about 10% grant. A CVSG puts the grant rate at about 29%, against about 4% without one.

## Adjustments
Upward:
- After its first conference (11/6) the petition was relisted, not denied, along with both companions. The record has no response to wait for, so the relist looks like real interest. Possible reasons: preparing a CVSG, a call for a response, or a dissent from denial.
- The question is a clean statutory one: who decides FSIA "foreign state" status, given Altmann and Samantar and, in the background, Loper Bright's hostility to deference. The petition claims a split with the Third Circuit (OI European Group v. Venezuela), the First Circuit (Ungar) and the Sixth Circuit (O'Bryan).
- Five en banc dissenters, including the Chief Judge. Three coordinated petitions from repeat Supreme Court counsel (King & Spalding), plus a multi-State amicus brief on Havlish.
- The stakes are large (see big_case_score).

Downward:
- No adverse party has appeared. The Court almost never grants without a response, so plenary review would probably need a CVSG or an appointed amicus first. That adds steps where it can fall off.
- The question involves executive recognition and foreign affairs (Zivotofsky territory), where the Court tends to defer to the political branches. The government's position will likely be decisive, and the government told the district court that DAB is Afghanistan's central bank. That cuts against petitioners if the SG weighs in.
- The "split" may be thin. The other circuits may have reached the same answer without facing executive statements this direct.
- The posture is unusual: prejudgment attachment of central-bank funds.

Net: a bit above the 0.248 anchor, at 0.30. The most likely near-term step is a CVSG (0.35) or another relist, not an immediate grant. A CVSG followed by a grant counts toward the 0.30.

## Increments
- `relist-increment` 0.6: the count is 2, with the 11/13 conference already distributed. Another distribution comes after any CVSG (once the SG's brief is in), any further relist, or any call for a response. Only a grant or a denial on 11/13 avoids one, and I put those together around 0.4.
- `summary-disposition-route` 0.04 (conditional on a grant): no intervening decision to GVR on, and a no-response summary reversal is implausible.
- `dissent-from-denial` 0.3 (conditional on a denial): a relisted case with a five-judge en banc dissent. Gorsuch and Thomas are the most likely writers, given their skepticism of deference to the executive.

## Retrieval and uncertainty
CourtListener MCP not used. Retrieval was two WebFetches of supremecourt.gov dockets and one corpus query (generic granted priors, not much use). I'm most unsure what the 11/6 relist means: it could be a hold for a CVSG, or a denial with a written dissent being drafted.
