# Rationale for the prediction

## Record and information boundary

This is a forward cert-stage prediction of Parker C. Myslow v. United States, Supreme Court No. 25-1148. The petition-kind event has no explicit stage or moment; I use the prompt's cert default and the named petition-disposition event, supplying all five cert claims. I read the case-level snapshot `record/snapshots/2026-09-15.json`, the event definition, `record/context.json`, and all three provisioned document texts. The context freezes `baseline`, salience version `sal-v4`, Term 2025, one distribution, and no CVSG. It has no cutoff. The snapshot records the June 17 distribution for September 28, 2026, not multiple conferences or a post-conference hold. Its source creation date is September 14, 2026; I make no claim that it includes later docket activity.

`record/documents/documents.json` reports a 29-page petition and 16-page opposition, both fetched July 17, 2026, neither truncated nor empty. The petition was filed March 31 and the opposition June 3. The QP extract is usable. The snapshot records a June 15 reply, but no reply text is provisioned; I do not claim to know its rebuttal. The appendix is linked but not separately provisioned, so my account of its documents rests on the parties' descriptions, not an independent examination of the appendix.

## Anchor

The committed `metrics/statpack.md` publishes a matching `sal-v4` table. For this private petitioner I use the **bracketed baseline reached** rates, not the federal-petitioner column merely because the United States is the respondent, and not the terminal-baseline rates. Pooling every displayed Term strictly before the context's Term 2025 gives:

| Term | Baseline reached rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The executed weighted calculation yields approximately **5.12% over a weighted denominator of 11,580**. This is an approximation calculated from rounded displayed rates, not reconstructed exact grant counts. I exclude 2025 and 2026 despite the future conference occurring near the next Term. These are the committed pack's estimates, not a fresh corpus query; no corpus-wide pull vintage was obtained, and I do not represent the pack as a current census.

I also read the modern-cert disposition and originating-court sections and the paid-segment relist/CVSG cuts. The terminal relist buckets show much higher grant-family rates after repeated distributions; the CVSG bucket also differs substantially from the no-CVSG bucket. Those are terminal-state associations, not forward increment probabilities from this snapshot. I do not multiply them into the anchor or treat the summer delay as additional attention. The court-of-origin table is descriptive context, not a replacement for the required prior-Term risk-set anchor.

## Why 1.5%, below the anchor

**Strongest negative: closely analogous petitions were already declined.** The petition itself acknowledges prior denials in Schneider and Dominguez-Garcia (petition p. 6 n.1). The opposition describes the January 12, 2026 denials in Johnson and Schneider, including the consolidated Schneider cases (opposition pp. 3, 6). Those are pre-snapshot outcomes of other petitions, not Myslow's own disposition. They materially lower the probability that this petition persuades four Justices to revisit the military appellate gateway. They are predictive evidence, not precedential holdings that the military courts were correct. I disclose their use in `flags.json`.

**The best affirmative case is textual and structural.** Petitioner distinguishes the military judge's signed judgment from the later staff-judge-advocate indorsement, invokes Article 66(d)(2)'s authority over subsequent processing errors, and argues that treating the two acts as simultaneous disrupts uniform deadlines and judicial control of the judgment. His reliance on the Johnson concurrence identifies a real concern about the majority's timing rationale (petition pp. 8–15). A nonviolent drug-use conviction and continuing firearms disability give the question more significance than a clerical dispute alone.

**The opposition supplies substantial vehicle and importance objections.** It distinguishes signing from entry into the record, says the indorsement and judgment entered together and bore the same date, and characterizes the restriction as a collateral consequence rather than an appellate-reviewable finding or sentence. It also notes that the Johnson concurrence agreed with the disposition despite disagreeing with the timing reasoning (opposition pp. 7–9). These are contested arguments, not facts I independently adjudicated. The AFCCA decision here is nonprecedential and disposed of the firearms claim without substantive discussion; CAAF denied review. That leaves little case-specific analysis for the Supreme Court to examine (opposition pp. 1, 4–6).

**The broad Second Amendment dispute is not a clean match to the question presented.** Petition pp. 18–20 discuss disagreement among civilian circuits, but p. 19 n.6 expressly distinguishes that disagreement from the immediate military-review issue. The QP asks who may review an allegedly unconstitutional annotation; it does not directly present the merits of a developed civilian Section 922 challenge. The petition also says the annotation did not identify a particular subsection of Section 922(g), and assumes subsection (g)(1) (p. 16 n.3). I therefore do not equate this vehicle with a clean grant to settle the underlying constitutional disagreement or adopt its constitutional premises as established law.

**Prospective importance has narrowed, without eliminating the claimed injury.** Both sides acknowledge the February 4, 2026 guidance memorandum removing first indorsements from court-martial documents. Petitioner emphasizes continuing disability and the memorandum's limited duration; the government emphasizes reduced recurrence and possible permanence (petition p. 10 n.2; opposition pp. 3–4 n.1, 10). I treat this as an importance reduction, not mootness. The opposition also identifies administrative correction, restoration, and separate civil-litigation avenues (pp. 9–10); their practical availability to Myslow was not independently verified, so I give them less weight than the analogous denials.

Together these considerations move the approximately 5.12% anchor to **1.5%**, not zero. The residual probability reflects the textual disagreement, continuing injury, and the chance that the Court sees broader military-review consequences. This adjustment is judgmental, not a fitted likelihood-ratio model.

## Other probabilities and limitations

An 8% redistribution probability allows for examination or a hold but reflects the absence of a new vehicle feature distinguishing the prior rejected petitions. A 0.1% CVSG probability reflects the government's already-filed opposition. The 25% summary-route probability is conditional on a grant, not an unconditional 25% forecast; the record identifies no intervening decision requiring a remand of this military statutory question. A 2.5% separate-writing probability is conditional on denial and reflects the constitutional stakes without predicting a specific Justice. These are subjective forecasts, not published incremental base rates.

The significance score of 0.30 reflects meaningful rights and military appellate access, tempered by the narrow procedural question and changed administrative practice. It is not a proxy for grant likelihood.

I neither knew nor retrieved Myslow's Supreme Court disposition. General-law web requests returned no usable content, so no external result informed the prediction. I did not query CourtListener or the corpus and did not seek this case's current docket or outcome. The missing reply and independently unread appendix limit confidence in my assessment of the government's objections. The forecast nevertheless rests on substantial pre-decision advocacy from both sides rather than the caption alone.
