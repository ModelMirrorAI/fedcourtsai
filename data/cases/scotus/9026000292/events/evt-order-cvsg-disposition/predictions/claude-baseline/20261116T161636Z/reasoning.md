# Reasoning — Havlish v. Taliban, No. 26-292 (CVSG moment)

**P(any grant) = 0.42; label: denied (a lean, not a confident call).**

## What I read
- Snapshot `2026-11-16.json`: petition filed Aug 31 2026; two cert-stage amicus briefs on Oct 5 (Iowa and 30 other States for petitioners; the Chargé d'Affaires of Afghanistan's UN mission, vided across the companion dockets); distributed for the Nov 6 and Nov 13 conferences (2 distributions); on Nov 16 the Court granted leave to file a supplemental brief and invited the Solicitor General's views. Justice Kagan is recused (prior government employment). No brief in opposition and no waiver appears on the docket; the Taliban is a defaulted judgment debtor, so there is no ordinary adversarial respondent.
- `questions-presented.txt` and the body of `petition.txt` (truncated row; I read the introduction, the split argument and parts of the appendix). `lower-court-docket.txt` (en banc petition filed and denied; it reports "dissent noted: not found", but the petition describes two dissents from denial joined by five judges — I follow the petition, as the prompt directs).
- `record/related/26-293.json` (relation `Vide`, Ashton) and `26-294.json` (relation `vided-amicus`, Owens): both are companion petitions from the same Second Circuit judgment, on the identical distribution schedule, and both drew the same CVSG on the same day. They will be disposed of together; they add no independent signal beyond confirming the Court is treating the three as a set.
- `same-question.json` lists no matching petitions.

## Anchors
- `context.json` band `high` (sal-v8), `cert_anchor.rate` = 0.350; `cert_amicus_line` (arm `some`, n=543) = 0.352.
- Statpack CVSG cut (paid scored segment): 166 resolved, granted 29.5% + GVR 6.0% = about 35.5% grant family; denied 62.0%.
So the committed baselines all sit at roughly 0.35.

## Adjustments
Upward:
- Five Second Circuit judges dissented from denial of rehearing en banc (Sullivan, joined by Livingston, Bianco and Park; Menashi separately), plus a panel dissent. That is a strong cert signal by itself.
- Stakes: about $3.5 billion in blocked Da Afghanistan Bank funds at the FRBNY and judgments held by 9/11 families; 31 States filed in support at the cert stage.
- A pure question of statutory text (whether TRIA § 201(a) fixes agency-or-instrumentality status at the blocking date), with a claimed conflict with the Ninth (Kirschenbaum) and Eleventh (Stansell) Circuits.
- The Court called for the SG without any respondent having opposed, which suggests real interest rather than routine caution.

Downward:
- The split is soft. As the petition itself describes them, the other circuits' cases concern when instrumentality status is measured relative to execution, not a square holding rejecting a blocking-date rule; the "blocking date" rule is new, so there is little percolation.
- The United States' position is the hinge and I cannot predict it confidently. The Executive has historically resisted TRIA attachments that constrain its control over blocked sovereign assets, and earlier US statements in this litigation emphasised keeping the reserves for the Afghan people and not recognising the Taliban as Afghanistan's government. A recommendation to deny would be followed more often than not. On the other hand, the current administration may be more receptive to 9/11 families and the States' position. I treat the recommendation as close to a coin flip, slightly tilted to "deny".
- Vehicle wrinkles: no adversary defending the judgment (an appointed amicus might be needed), recognition/FSIA issues lurking as alternative grounds for affirmance, and an eight-Justice Court with Kagan out.

Net: a modest move above the ~0.35 anchor to 0.42. Rough decomposition: P(SG says grant) ≈ 0.45 with P(grant | that) ≈ 0.75; P(SG says deny) ≈ 0.55 with P(grant | that) ≈ 0.15, giving ≈ 0.42.

## Other claims
- `relist-increment` 0.97: after the invited brief arrives the petition is redistributed for conference; only a withdrawal or dismissal before then would prevent it.
- `cvsg-increment` 0.02: a CVSG is already on the docket (vacuous here); a second call is essentially unheard of.
- `summary-disposition-route` 0.05 (given a grant): no intervening decision is in view; a grant would be plenary.
- `dissent-from-denial` 0.12 (given a denial): the subject (9/11 victims, terrorism judgments) could draw a statement, but denials after a CVSG rarely carry one.
- `order-writers`: small numbers, highest for Alito, Gorsuch and Thomas; Kagan near zero because she is recused.

## Uncertainty and discounts
The forecast is dominated by a brief that does not exist yet. I did not retrieve the Second Circuit opinions outside the provisioned petition appendix, and I made no web search; my account of the earlier US position rests on the petition appendix and general background, not on a filing I verified. The CVSG base rate has n=166, so the anchor itself is noisy. Retrieval beyond provisioned inputs was one corpus query (unhelpful for this question) and the statpack.
