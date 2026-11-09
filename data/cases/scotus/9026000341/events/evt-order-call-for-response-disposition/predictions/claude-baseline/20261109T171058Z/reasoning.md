# Reasoning — Spartan Securities Group v. SEC, No. 26-341 (response-requested moment)

**P(any grant, GVR included) = 0.16. Call: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-10-23.json`: paid petition filed Aug 28, 2026 by NCLA from CA11 No. 22-13129 (published opinion Jan 16, 2026; rehearing denied Apr 30, 2026). The SG waived a response Oct 9. The petition was distributed for the 11/6/2026 conference on Oct 14. One amicus brief (Investor Choice Advocates Network) was filed Oct 15. The Court requested a response on Oct 23, due Nov 23, 2026. The record shows one distribution and no CVSG. A CVSG cannot happen here because the United States is the respondent.
- `context.json`: mode `forward`, band `baseline` (sal-v8), `cert_anchor.rate` = 0.0516.
- `questions-presented.txt` and `petition.txt` (reasons section): QP1 asks whether nonpublic Forms 211 to FINRA and emails to DTC that no investor saw are "in connection with" a securities purchase under 10(b). The petition claims an "unacknowledged" split with the Texas Gulf Sulphur dissemination line (2d, 3d, 4th, 9th, 10th, D.C. Cir.). QP2 asks whether, after Liu and Sripetch, disgorgement may go to the Treasury with no identified harmed investors. It claims a split among the 5th Cir. (Hallam: (d)(7) disgorgement is legal), the 2d Cir. (Ahmed/Govil: equitable limits apply) and the 9th Cir.
- `decision-below.txt` (CourtListener cluster 10775540; it matches the petition's description): the CA11 panel squarely held that under §§ 21(d)(3)(A)(ii) and (d)(7) the SEC may obtain disgorgement paid to the Treasury even where that would not be "for the benefit of investors" under (d)(5). It addressed Ahmed/Govil in a footnote and distinguished them. The opinion is long and published, so it is a clean vehicle on QP2.
- `same-question.json`: no similar pending petitions above the threshold.
- `lower-court-docket.txt`: an en banc petition was filed; the disposition was not read, and no dissent was recorded.

## Anchor and adjustments
- Anchor: baseline band reached rate of 5.2% (`cert_anchor`). This is a paid petition and, per the statpack, CA11 grant-family rates are typical.
- **Up: the call for a response.** The SG waived, and a Justice still asked for a response. That is a real but low-bar signal, and most such petitions are still denied. From general knowledge, the grant rate after a call for a response is roughly 2–3x the paid baseline. No committed table conditions on this signal, so this step is my own judgement.
- **Up: subject matter.** SEC disgorgement has produced three cert grants in nine years (Kokesh, Liu, Sripetch). Sripetch (June 4, 2026, unanimous, Gorsuch, J.) expressly left open the Treasury/no-victim question and the nature of (d)(7). Justice Thomas wrote separately on (d)(7). The CA11 holding answers that open question directly, and the petition shows a real tension with Ahmed/Govil's reading of (d)(7). One amicus brief (statpack 1-amicus bucket: about 15% grant family, n≈1159) is consistent with this.
- **Up (small): GVR route.** Sripetch postdates both the judgment below and the rehearing denial. A GVR in light of Sripetch is possible, although Sripetch ruled for the SEC, which cuts against a remand changing the result.
- **Down:** QP1 is fact-bound, and the claimed split is "silent", which the Court discounts. The QP2 disgorgement here is small (about $150k). There is a stipulation that distribution to investors was infeasible, which may make the case a messy vehicle. The SG will likely argue that Sripetch's reasoning (disgorgement is tied to interference with investors' protected interests) leaves no square split worth resolving now, or that the 5th Cir.'s Hallam reading is narrow.

Net: about 0.16. The main uncertainty is whether the Court wants a near-term follow-on to Sripetch on (d)(7)/Treasury. If so, this published, squarely decided opinion is a plausible vehicle, and the odds could be considerably higher.

## Claims
- relist-increment 0.97: masked on this moment; the petition will be redistributed once the response arrives.
- cvsg-increment 0.01: the United States is the respondent, so a CVSG is essentially impossible.
- summary-disposition-route 0.35: given a grant, a GVR in light of Sripetch is a real alternative to plenary review.
- dissent-from-denial 0.07: Thomas (Sripetch concurrence on (d)(7) as legal disgorgement) or Gorsuch could write. Still, this is unlikely on a denial.

## Retrieval / degradations
One corpus query (shape only) and one web search confirming Sripetch's date and holding. That decision predates the snapshot, so it is legitimate forward context. Nothing about this case's own disposition surfaced.
