# Reasoning — scotus/9026000648 (No. 26-648), arrival moment

**P(any grant) = 0.40; point call: denied.**

## What I read

- Snapshot `2026-11-18.json`: paid petition filed Nov 13 2026, docketed Nov 17, response due Dec 17 2026. No distribution, no response, no amicus brief, no CVSG. That emptiness is the arrival moment's definition, not a gap.
- `questions-presented.txt` and `petition.txt` (truncated at the cap; I read the front matter, the question presented, and Reasons section I and the start of II; I did not get a clean read of the vehicle section III).
- `decision-below.txt` (CA2, June 30 2026, Pérez, J., with Sack and Preska; published, 180 F.4th 434 per the petition) — I checked it is the judgment the petition describes: the consolidated *Plumbers* / *Mulhern* appeals affirming dismissal / summary judgment against EPCA preemption challenges to New York City Local Law 154 and the State's all-electric buildings law.
- `lower-court-docket.txt`: rehearing en banc sought and denied Aug 26 2026, no noted dissent.
- `context.json`: band `baseline` (sal-v8), `cert_anchor.rate` 0.0517, amicus-line `none` arm 0.0268, mode `forward`.

## Anchor

Private (trade-association / union) petitioners, so the caption-class floor is `baseline`'s bracketed reached rate. The frozen `cert_anchor.rate` is 5.2% (the statpack table's prior-Term rows run 4.2%–6.0%). That is the rate for an arbitrary paid petition at arrival. I am far above it, for reasons specific to this petition.

## Why far above the anchor

1. **An express, acknowledged circuit split on a pure question of federal statutory law.** The Second Circuit's opinion itself says it departs from the Ninth Circuit's *California Restaurant Ass'n v. City of Berkeley* (89 F.4th 1094) and that it "reluctantly believe[s] it necessary to create a split among the Circuits" (I confirmed that language is in the provisioned decision below, not only in the petition's characterization). Per the petition, no party below tried to distinguish Berkeley's ordinance. Court-acknowledged splits on express-preemption provisions are the core of the cert docket.
2. **The United States is on the petitioners' side.** The decision below lists DOJ as amicus supporting the plaintiffs in No. 25-977, and the petition says the government has since sued municipalities (D.N.J., N.D. Cal.) and supported challengers in the Fourth, Seventh and D.C. Circuits. A lower court's rejection of the government's reading of a federal statute, with the SG likely to support review if asked, is a strong grant signal.
3. **Importance and recurrence.** Gas-appliance bans are spreading; the petition identifies pending appeals in the Fourth (argument set Dec 8 2026), Seventh, Tenth and D.C. Circuits (argued Sept 8 2026). Heavy cert-stage amicus support (gas utilities, builders, restaurant groups, possibly States on both sides) is likely, which would move the petition out of the `none` amicus arm.
4. **Clean posture, as far as I can see.** Final judgments on a question of law; rehearing en banc denied; a joint petition covering both a city and a state law; experienced counsel.

## Why not higher than 0.40

- **The split is 1–1 and percolation is imminent.** Three or four more circuits will rule within a year. The Court often waits when the question is actively moving through the courts of appeals, and respondents (New York City's Corporation Counsel and the State's Solicitor General — capable opposition) will press exactly that, and will argue Berkeley's piping ban and later Ninth Circuit decisions (the petition's table cites *Rinnai America v. SCAQMD*, 9th Cir. 2026, which I did not read) make the conflict narrower than claimed. If the D.C. and Fourth Circuits side with the Second Circuit before conference, the Ninth Circuit becomes a lone outlier whose own losing party (Berkeley) repealed rather than sought review — that weakens, though does not remove, the case for review.
- **The Ninth Circuit en banc vote** drew a dissent from denial of rehearing on behalf of eight active judges (the petition's count); the Court may see the conflict as one that could self-correct.
- **The government changed sides** between Berkeley and this case, which gives respondents a talking point and slightly reduces deference to its view.
- **Base-rate humility.** Even well-lawyered acknowledged-split petitions are denied a large fraction of the time; I have no response, no amici and no distribution to read yet. A CVSG is possible, which would delay but (given the government's stated position) probably help.

Net: I put this in the range of a strong-but-not-certain petition, roughly 35–45%, and write 0.40. Because the probability is under one half, the point label is `denied`, with `granted=0`.

## Other claims

- `relist-increment` 0.97: the snapshot shows zero distributions; any distribution after it resolves this true, and only a Rule 46 dismissal or withdrawal before distribution would prevent one.
- `cvsg-increment` 0.10: the United States' position is already public and emphatic, which makes an invitation less necessary; but the Court does sometimes invite the SG on federal-program preemption questions, and a newly changed government position is something it might want stated formally.
- `summary-disposition-route` 0.04 (conditional on grant): no intervening decision to GVR on that I know of; a grant here would be plenary. Small residual for a GVR should a relevant decision or statutory change intervene.
- `dissent-from-denial` 0.15 (conditional on denial): an acknowledged split left standing on a textualist preemption question is the kind of denial that occasionally draws a noted dissent (Thomas, Gorsuch or Kavanaugh the likeliest), but most denials carry none.
- `order-writers`: small per-Justice numbers consistent with the above.
- `big_case_score` 0.62: nationally significant for energy/climate policy and the building and gas industries, statutory rather than constitutional.

## Retrieval and caveats

One corpus query (generic recent granted SCOTUS rows; not informative about this question) and the committed statpack. No CourtListener MCP or web retrieval; I did not look at the live docket beyond the snapshot. I have background familiarity with the Berkeley litigation from training; I know nothing about this petition's disposition, which does not yet exist. The petition text was truncated and I rely on the petitioners' own description of the pending circuit cases and of the government's briefs, which I did not verify independently.
