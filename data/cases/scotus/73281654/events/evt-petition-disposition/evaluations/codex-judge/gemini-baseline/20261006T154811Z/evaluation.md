# Evaluation: gemini-baseline

## Outcome and scores

The supplied cert-stage outcome is denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline's September 18 forecast names denial and assigns P(any grant) = 0.01. Exact-label correctness is 1; Brier loss is `(0.01 - 0)^2 = 0.0001`. The small realized loss does not independently validate its factual premises or establish calibration.

gemini-baseline froze elevated band, sal-v4, and docket Term 2025. The matching committed sal-v4 table supplies the risk-set baseline, using only bracketed reached values from Terms 2017–2024: `(17.5%,400), (15.9%,347), (13.8%,334), (16.1%,397), (20.5%,342), (19.0%,300), (17.5%,354), (17.9%,336)`. Resolved-weighting gives 484.386 / 2,810 = 0.17237935943060498. This is approximate reconstruction from rounded, denial-reweighted rates, not an integer grant count. The table displays all ten of ten Terms; 2025 and 2026 do not enter. Brier skill is `1 - 0.0001 / baseline^2 = 0.9966346559128061`. The band comes from the prediction, never from the evaluator's decided-docket context. These are committed-artifact calculations; no refreshed corpus or population-wide inference is claimed.

## Reasoning quality: 0.48

The rationale identifies genuinely relevant considerations: the money-mandating-source problem, possible independent jurisdictional obstacles, lack of a demonstrated circuit conflict, and an opposition already filed for the United States. Those considerations support a downward adjustment from the elevated-band anchor without relying on hindsight.

However, its first major reason is factually contradicted by the provisioned record. It calls the Federal Circuit decision unpublished and nonprecedential, while the opposition's Opinions Below section, printed page 1, reports it at 156 F.4th 1339. The candidate's own retrieval note describes an unpublished opinion with ID 11171627, but the uncaptured result does not let me determine what that opinion was. I therefore flag the demonstrated publication-status error without speculating about the retrieved document's identity.

The discussion also blurs the relevant court and claim when presenting the procedural dismissals. The opposition, printed pages 9–11, attributes three grounds for the water claim to the CFC and expressly says the Federal Circuit did not reach section 1500 for that claim after affirming on the substantive-source ground. Those alternative grounds create serious vehicle risk, but the rationale does not preserve that distinction or explain why they inevitably foreclose review. It labels the precedent's application straightforward without engaging the petition's existing-water versus additional-water distinction. Finally, it gives no reproducible pooling calculation and little explanation for choosing 1% rather than a less extreme downward adjustment.

The score concerns these analytical strengths and defects in `reasoning.md`, not its correct label or its unscored forecast. A bare cert denial supplies no Court rationale with which to vindicate the doctrinal assertions.

## Leakage and scope

The harness records forward mode. Every one of 31 logged calls is unobserved; this is a capture limitation, not a defect or evidence of leakage. I inspected the query slices rather than treating missing dates or digests as failed retrieval. The log includes provisioned-input reads, a case-caption search, an opinion read and passage search, and two corpus commands carrying a pre-prediction date restriction. The corpus commands are not listed in the candidate's retrieval note, but their results and success cannot be inferred. No call or reasoning affirmatively exposes the October 5 petition outcome. In the genuine forward chronology, a case search on September 18 is not itself leakage. Retrieved outcome material is assessed false on the available evidence, influence not applicable, and leakage suspected false, with limited assurance because no results were captured.

The factual error is recorded durably in the cell's `flags.json`; it is not a leakage finding. The forecast document was read but not scored. Cert votes and semantic claims are unscored, and mechanical claim scores remain the harness's. Optional stakes grading is omitted because the candidate's score had already been seen.
