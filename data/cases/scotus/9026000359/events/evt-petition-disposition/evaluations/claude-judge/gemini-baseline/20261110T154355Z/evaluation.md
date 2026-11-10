# Evaluation: gemini-baseline, scotus/9026000359, evt-petition-disposition

**Cell:** cert stage, forward, distribution moment. **Outcome:** `denied` (2026-11-09), one distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` with P(grant) = 0.005, so `correct` = 1 and Brier = 0.000025. The segment base rate, basis and skill are stamped by the harness (frozen band `baseline`, sal-v4). Compare against the stamped segment base rate. Vote accuracy does not apply on a cert cell.

**Reasoning quality: 0.55.** The direction and the main drivers are right: the waiver with no call for a response, error-correction framing, no pleaded split, and a local dispute. Three weaknesses lower the grade:
- **A factual error used as a reason.** The rationale twice calls the Sixth Circuit decision "unpublished". The staged appendix opinion is headed "RECOMMENDED FOR PUBLICATION" (File Name 26a0176p.06). The candidate appears to have keyed on the phrase in a grep rather than the heading.
- **An oversimplified holding.** It says the court found no protected property interest. That is the procedural due process holding only. For takings the panel assumed an interest, and the retaliation claim failed on municipal policymaker grounds.
- **The terminal anchor.** It anchors on a figure of about 0.9%, which matches the band's terminal grant rate. The frozen-band rule points to the risk-set (reached) rate. The final number is still reasonable.

The rationale is brief and engages little with the appendix.

## Predicted reasoning

**Grade: 0.5.** The central claims are:
- outright denial at the first conference;
- no relists;
- no CVSG;
- no separate writing.

All four were borne out, but they are generic for this posture. The contextual premise that the opinion is unpublished is wrong, a minor cost because the disposition does not turn on it. The conditional-grant content (the procedural due process or takings question) is unresolved.

## Leakage

The cell is forward, with `cutoff` null and a 2026-10-15 snapshot. Every logged call is `unobserved`, so the calls are graded on their queries. All of them were reads of the provisioned record, the statpack, the prompt and schemas, plus writes to its own output directory. There were no web or CourtListener calls and nothing under data/qp-topics. `not_applicable`, not suspected.

## Big case

0.07. The case is a local, fact-bound permitting dispute, denied at its first conference.
