# Evaluation — gemini-baseline, scotus/9026000241, evt-petition-arrival-disposition

Cert-stage, arrival-moment, forward cell. Outcome: petition **denied** 2026-11-09 after a single distribution (respondents waived; distributed for the 11/6/2026 conference). No CVSG, no noted dissent. The segment base rate and skill are stamped by the harness from the frozen `baseline` band's risk set; I quote no rate of my own. I left `vote_accuracy` out because this is a cert cell.

**Correct** (denied vs denied). Brier (0.065 − 0)² = 0.004225.

**Reasoning (0.50).** Selects the right anchor (the frozen baseline band's strictly-prior arrival rate) but then stops there. The rationale itself identifies reasons this is a weaker-than-average paid petition (the Fifth Circuit applied a recent controlling precedent, there is no mature split, private petitioners against a municipality) yet concludes there is "no strong reason to adjust" and leaves the number at the band average. That is internally inconsistent: if the vehicle is poor relative to the segment, the forecast should sit below the segment rate. The analysis rests on the QP alone. It does not engage the petition (an unpublished decision below, the claimed Eighth Circuit conflict, the QP's misframing of the *Nieves* exception), even though `documents.json` listed the petition as available. Directionally sound and correct, but it is the weakest-supported of the three numbers and roughly 2.6× the next-highest.

**Leakage.** Forward mode, predicted 2026-08-25 while the petition was undecided. The retrieval log shows only pre-decision precedent lookups and searches for the unpublished decision below. Nothing in the log or the prose touches this petition's disposition. Graded `not_applicable`, not suspected.

**Big case.** My own read is 0.15: a fact-bound application of *Gonzalez* from an unpublished decision.

## Predicted reasoning

Grade 0.55. I treated these as the central claims:

- *Denial at the first conference with no further relist.* — **borne-out**. Single distribution Oct 07 for the 11/6/2026 conference; denied Nov 9; distribution_count 1.
- *No CVSG.* — **borne-out**. Outcome cvsg_date null.
- *No separate writing or dissent from denial.* — **borne-out**. noted_dissent_from_denial false.

Every central claim held, but each is close to the modal path of a paid baseline-band petition (one distribution, denial, no CVSG, no writing). That limits how much discriminating content the forecast carries, so the grade sits between the 0.5 and 0.75 anchors. The conditional content (a reformulated QP or the GVR-versus-plenary split if the Court granted) earns neither credit nor penalty, because the Court denied.
