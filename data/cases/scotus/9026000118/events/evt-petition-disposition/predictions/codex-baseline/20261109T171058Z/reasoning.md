# Rationale

## Call and information set

I assign **0.88 to any grant-family disposition** and select **summary reversal**, not a new plenary argument, as the modal disposition. This includes the contract's grant-family treatment of a vacatur and remand for mootness; it is not an 88% forecast that Alabama wins a final merits judgment.

The baseline is `record/snapshots/2026-11-09.json`, with the distribution-moment event and forward-mode `record/context.json`. There are **three distributions**, entered September 30, November 2, and November 9 for conferences on October 16, November 6, and November 13, 2026. Thus two redistributions have already occurred; my increment forecast starts after the third distribution. There is no CVSG and no amicus-brief entry in the supplied docket. An absent amicus entry is not proof that no support exists elsewhere.

Although the event uses the cert-stage contract, the filing is a **jurisdictional statement appealing a three-judge district court's injunction under 28 U.S.C. §1253**, not an ordinary discretionary certiorari petition. I retain the declared stage, binary, and disposition vocabulary, but do not equate its selection standard with ordinary cert selection. Noting probable jurisdiction, summary reversal, and vacatur are relevant routes; the merits judgment after plenary review is not this event's target.

## Calibration

The frozen `sal-v8`, `high` anchor in context is **0.3484455958549223**, pooled over strictly earlier Terms with a ten-Term lookback. I use that anchor rather than the terminal-band rate or the current Term's tiny sample. `metrics/statpack.md`, under the matching salience-version table, supplies the appropriate risk-set interpretation. The broader modern docket's grant-plus-GVR share is approximately 2.8%, but that unselected population is not this repeatedly distributed state appeal.

The paid-segment relist-2 bucket has **n=495 resolved**, with 28.3% grants and 12.9% GVRs; relist-3+ has **n=483 resolved**, with 23.2% grants and 14.1% GVRs. These terminal-count cuts cross-check the scale of the anchor, not the probability of another relist. The CVSG bucket has **n=164 resolved**, with 29.3% grants and 5.5% GVRs; the no-CVSG bucket has **n=13,550 resolved**, with 4.1% grants and 2.3% GVRs. Neither is an independent multiplier. The observed-zero-amicus bucket has **n=11,109 resolved**, with 2.0% grants and 1.8% GVRs, but this marginal terminal-count comparison deserves little weight against direct judicial evidence in this appeal. These aggregate cuts describe population shape; they do not replace the frozen prior-Term anchor.

The bounded corpus lookup returned three earlier GVRs: Monsanto v. Salas, No. 24-1097; Monsanto v. Johnson, No. 24-1098; and Petersen v. Doe, No. 24-449. Their three or four distributions show that repeated consideration can end in an order-stage remand rather than argument. They are not voting-law merits analogues, and the two Monsanto cases are not independent substantive evidence.

## Why this appeal departs sharply from the anchor

The jurisdictional statement's questions concern alternative-map requirements, separating race from partisan voting, the totality inquiry, and intentional discrimination. Its body, particularly printed pages 1–3, 7–10, and 23–35, argues that the district court reinstated substantially the same injunction after Callais. I checked the opposing account in the bound district-court order, especially App.1a–12a and 27a–44a, and the older findings excerpt in the separate appendix. The district court treated the legislative conduct and its record of intentional discrimination as independently significant; Alabama's description is advocacy, not an uncontested factual finding.

The strongest incremental evidence is the **June 2, 2026 stay opinion**, Allen v. Milligan, 608 U.S. 511, covering applications 25A1314–25A1316, including Singleton. This is an earlier interim event, not the disposition now being predicted. CourtListener opinion 11336479, per curiam pages 2–4, independently confirms that the Court already found Alabama likely to succeed on both the statutory and constitutional claims and identified specific errors involving legislative good faith, alternative maps, and partisan voting. That directly adverse assessment of this very injunction is much stronger than party identity, stakes, or relists alone. It is provisional, not a binding prediction of the appellate disposition, but makes ordinary no-review treatment unlikely.

I also checked Callais itself, CourtListener opinion 11320154, majority pages 29–30. Its requirements for alternative maps and partisan controls substantiate the legal framework rather than merely repeating Alabama's characterization. Because a controlling decision and a case-specific stay opinion already address the issues, another full briefing-and-argument cycle adds less than it would in a fresh doctrinal dispute.

## Counterweights and route uncertainty

The retrieved September 18 motion to dismiss, printed pages i, 8–11, and 16–20, argues that relief concerns only the 2026 election and challenges Alabama's account of available alternative maps. November 3, 2026 is already past at prediction time. This creates a serious mootness issue, not a reason to assume what the Court has done.

The retrieved September 29 response, printed pages 1–3 and 12–13, answers that post-election administration remains, the injunction has continuing effects, and its expiration language extends beyond election day; alternatively, it asks for Munsingwear vacatur. I have not independently resolved the parties' competing constructions. Mootness therefore shifts appreciable probability from substantive reversal to vacatur/remand rather than moving all of it to an ungranted dismissal. The response also disputes the adequacy of appellees' proposed alternative maps. These contested facts and procedural issues keep the forecast below certainty.

`record/same-question.json` identifies Nos. 26-116 and 26-117 as exact textual matches, but these are similarity candidates, not Court `Vide` links. The jurisdictional statement independently explains the common Milligan/Singleton/Caster proceedings. No related docket was provisioned or retrieved, and I infer neither a companion grant nor a formal hold. I do not rely on the similarity file's next-day cutoff or pending-status labels.

## Auxiliary probabilities and limitations

At **0.68**, another distribution is more likely than immediate disposition, chiefly because preparing or coordinating a reasoned summary order and dissent can take additional conferences. My modal path is one or two more redistributions. A new CVSG is only **0.01**: the Court has already addressed the operative legal dispute itself. Conditional on grant, **0.95** goes to disposition in the order itself, with summary reversal ahead of vacatur/remand and only a small plenary-review tail. Conditional on an ungranted denial, I put a dissent or statement at **0.18**. That is distinct from the substantially greater chance of a liberal dissent from a summary reversal.

The order-writing forecast favors Sotomayor as actual author, because she authored the earlier stay dissent joined by Kagan and Jackson. Joining that dissent does not make the other two its authors. Their probabilities are correspondingly smaller, and no per-Justice cert vote forecast is supplied. The stakes score **0.94** concerns representation and voting-rights enforcement, not the grant probability.

`documents.json` marks both the jurisdictional statement PDF and separate appendix as truncated, with extractable text. The statement's main argument is available; bound lower-court material is cut partway through the May 26 order, and the separate appendix supplies only part of the much longer earlier findings. Neither complete appendix nor a fresh lower-court docket was reconstructed. The initially unstaged dismissal motion and response were retrieved directly from their dated snapshot links. Browser calls returned no usable content; direct filing retrieval and CourtListener supplied the needed primary materials. A reporter-citation search for the stay was empty, but a narrowly date-bounded lookup located its text.

I did not know or retrieve the target appeal's eventual disposition, subsequent history, other predictors' outputs, or outcome labels. The earlier stay and Callais ruling are expressly pre-decision context. No current merits-docket outcome search was used.
