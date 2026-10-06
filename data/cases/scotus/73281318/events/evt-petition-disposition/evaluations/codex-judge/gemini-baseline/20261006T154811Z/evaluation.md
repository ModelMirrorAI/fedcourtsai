# Evaluation of gemini-baseline

## Outcome and numerical scores

This cert-stage evaluation concerns the staged prediction from run 20260916T170237Z. The recorded outcome is denied on October 5, 2026, with actual_granted = 0. The candidate predicted denied, so correct = 1. Its 2% probability yields Brier score (0.02 - 0)^2 = 0.0004. The denial does not establish the merits of the search or disclose the Court's rationale.

The candidate froze elevated, sal-v4, Term 2025. The matching committed metrics/statpack.md table supplies the bracketed reached risk set, pooled over displayed Terms 2017–2024 only. The chronological (rate %, weighted n) pairs are (17.5, 400), (15.9, 347), (13.8, 334), (16.1, 397), (20.5, 342), (19.0, 300), (17.5, 354), and (17.9, 336). Their rendered-rate weighted numerator is 484.386 and denominator 2,810. Segment base rate is therefore 0.17237935943060498, base_rate_basis risk_set, and skill = 1 - 0.0004 / rate^2 = 0.9865386236512242.

These are denial-reweighted live/historical-slice estimates based on rounded displayed rates, not raw grant counts. The table renders 10 of 10 Terms, so no rendering-window divergence applies. No later Term or evaluator terminal band is used. The approximately 17.2% anchor in the rationale is consistent with this estimate. No live corpus was consulted or claimed current.

## Reasoning quality: 0.76

The concise rationale identifies three important features corroborated by the supplied briefs: the interlocutory reversal of suppression, a fact-specific challenge to the emergency-aid standard's application, and the opposition's explanation that the lower court's probable-cause language favored the defendant rather than creating a strong GVR route. It correctly avoids interpreting two distributions as repeated substantive conference struggles. These are pertinent reasons to reduce the elevated-band anchor substantially.

The weakness is incomplete handling of uncertainty, not brevity by itself. The conclusion that the vehicle is fatal is stronger than the document's analysis of finality exceptions supports. Describing a GVR as futile treats the opposition's argument as decisive without exploring residual uncertainty. The response request's positive informational value receives little weight or explanation; favorable home-entry facts and the unavailable reply are not meaningfully weighed. The document gives little account of why the final number should be 2% rather than another low probability. Its claim that the merits are weak is less developed than its vehicle analysis.

The favorable realized loss does not remove these weaknesses, and the bare denial does not prove that the vehicle was jurisdictionally fatal. The grade concerns only reasoning.md, not the separate forecast or the truth of mechanical claim predictions. No claim_scores, semantic grades, or vote accuracy are supplied on this cert-stage cell.

## Leakage

The staged log records forward mode, and the September 16 prediction precedes the October 5 disposition. Every one of its 35 rows is unobserved. I therefore do not treat null result dates or digests as proof that no material was returned. The query targets themselves show provisioned record reads, brief searches, aggregate baseline reads, schema checks, and output work; none seeks this case's later history or disposing order. The reasoning describes predecision arguments rather than reading the recorded denial back into a prediction. On that evidence, retrieved_outcome_material is false, influence not_applicable, and leakage_suspected false. This finding retains the result-level visibility limitation; missing capture is neither a defect nor proof of leakage.
