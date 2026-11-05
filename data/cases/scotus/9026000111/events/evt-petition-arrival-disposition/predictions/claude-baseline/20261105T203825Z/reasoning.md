# Reasoning — scotus/9026000111 (No. 26-111, Herzon v. Arias), arrival moment

**P(any grant) = 0.80. Predicted disposition: GVR (grant, vacate, remand), most likely after a hold for *Nielsen v. Watanabe*, No. 25-417.**

## Inputs used
- Snapshot `record/snapshots/2026-07-24.json`: a paid docket. It shows the extension application 25A1226 (granted by Justice Jackson) and the petition filed July 23, 2026. Counsel of record for petitioners is **D. John Sauer, Solicitor General**. The lower court is CA1, No. 23-1618, decided Aug. 15, 2025, with rehearing denied Feb. 24, 2026. There are no distributions and no CVSG, which is the arrival state.
- `questions-presented.txt`: whether *Bivens* should be extended to a Fourth Amendment excessive-force claim arising out of executing an arrest warrant outside the home.
- `petition.txt` (98 pp., truncated at the cap). I read the tables, introduction, statement and the start of the argument. The petition alleges a multi-sided split: CA1, CA7 and CA10 allow the claim; CA5 and CA9 bar it outside the home; CA4 bars it for warrant arrests. The CA1 panel was divided, and Judge Lynch dissented, including from the denial of panel rehearing. As an alternative to plenary review, the SG expressly asks the Court to **hold the petition for *Nielsen v. Watanabe*** (cert. granted June 22, 2026; an Eighth Amendment *Bivens* case).
- `same-question.json`: empty list (nothing above the 0.5 threshold). No related dockets staged.
- Corpus row for No. 25-417 (*Nielsen*): granted, not yet decided, SG among counsel.
- No BIO yet. A live docket check (below) shows the response was extended to Dec. 7, 2026.

## Anchors
- The frozen `band` is **`baseline`**, with `cert_anchor.rate` = 0.0515 (sal-v7, 10 Terms). This is the yardstick I am scored against. The caption names individual DEA task-force officers ("Noah A. Herzon, et al."), not a sovereign, so the caption rule reads it as private. **In substance this is a federal-government petition**: the SG files for federal officers sued in their personal capacities. So the economically relevant anchor is the `federal` class floor. Pooling its bracketed `reached` rate over Terms 2017–2025 gives roughly 155/212 ≈ **73%**. Term 2026 (4/4) is excluded as the case's own Term and too thin. I flag the band mismatch in `flags.json`.
- The statpack's whole-docket federal band row gives granted 52.5% and gvr 21.0%. The GVR share among SG petitions is substantial, which matches a hold-then-GVR posture.

## Adjustments
- **Up:** this Court has not extended *Bivens* in 46 years and has summarily reversed extensions (*Goldey v. Fields*, 2025, per curiam). There is a deep, acknowledged split, a dissent below, and the SG's institutional interest in officer liability. The hold request is decisive. Held petitions are almost never denied while the lead case is pending. If *Nielsen* tightens the new-context analysis, as I expect, a GVR so CA1 can apply it is the natural result. If the Court instead wants to resolve the Fourth Amendment split directly, it could grant plenary review or summarily reverse.
- **Down:** the posture is interlocutory (CA1 reversed summary judgment and remanded). Respondent has taken two response extensions, to Dec. 7. *Nielsen* might be decided on grounds that do not reach the "new context" step for Fourth Amendment claims, which would leave a denial open. The petition also concedes that *Nielsen* concerns a different amendment.
- Net: 0.80. That is above the federal floor because of the hold request and this Court's consistent hostility to *Bivens*. I kept residual weight on a denial.

## Other claims
- relist-increment 0.96: zero distributions so far. Any petition that is not withdrawn will be distributed at least once after the response comes in.
- cvsg-increment 0.005: the SG is the petitioner, so a CVSG is effectively impossible.
- summary-disposition-route 0.62 (conditional on a grant): a GVR after *Nielsen*, or a summary reversal, is more likely than plenary review. I put about 0.38 on a plenary grant.
- dissent-from-denial 0.30 (conditional on a denial): a denial here would plausibly draw a writing from Thomas or Gorsuch (*Bivens* critics) urging review.

## Uncertainty / discount
I could not see the BIO. The petition text is truncated, so I did not read the end of the split discussion. The timing of *Nielsen* and its breadth are the main uncertainty. The 0.80 sits far above the frozen 5% anchor, which is deliberate: the band misreads this caption.
