# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of the prediction from run `20260918T174135Z`. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label was `denied`, so correctness is **1**. With P(grant) = 0.26, the Brier score is `(0.26 - 0)^2 = 0.0676`.

The scored prediction froze elevated under sal-v4 and docket Term 2025. The committed `metrics/statpack.md` heading matches that version. Its caption renders 10 of 10 Terms; every rendered Term strictly before 2025 is pooled, using bracketed reached rates rather than terminal-band rates. OT2024 through OT2017 contribute respectively (17.9%, n=336), (17.5%, n=354), (19.0%, n=300), (20.5%, n=342), (16.1%, n=397), (13.8%, n=334), (15.9%, n=347), and (17.5%, n=400).

The displayed-rate weighted pool is `484.386 / 2810 = 0.17237935943060498`, basis `risk_set`. The numerator is derived from rounded percentages over weighted denominators, not an integer grant count. Brier skill is `1 - 0.0676 / 0.17237935943060498^2 = -1.2749726029430946`. The forecast underperformed this naive baseline on this event despite naming the correct modal label; that does not establish long-run miscalibration. The predictor's stated 484/2810 baseline came from its more precise JSON-pack calculation; the small difference is not treated as a reasoning error because this evaluation follows the printed-table contract. No live corpus freshness is asserted or was obtained.

## Reasoning quality: 0.90

The rationale distinguishes a broadly important legal question from whether this record actually presents the alleged conflict. It identifies both the petition's claimed split and the opposition's counterargument that objective medical evidence, not subjective employer belief, supported the judgment. Its attention to cross-citations, medical versus nonmedical comparators, and independent evidentiary obstacles is grounded in the parties' provisioned texts. It appropriately attributes contested positions to the parties instead of treating them as independently established holdings.

The procedural analysis is also careful: two distribution entries are not automatically two substantive conference examinations, particularly when the first coincides with the response request and the later entry follows completed briefing. The rationale preserves the frozen band rather than substituting a stronger terminal signal. It explicitly identifies the unavailable reply and disclaims treating denial as merits endorsement.

The principal remaining limitation is quantitative: moving from about 17.2% to 26% is an acknowledged judgment rather than an empirically supported adjustment. Response-request and amicus signals may overlap with the attention already represented in the band, and the rationale does not quantify their incremental contribution. This prevents a near-perfect assessment, but the balanced handling of the record remains strong despite the negative realized Brier skill.

The recorded denial provides no explanation establishing which vehicle objection mattered. This grade is confined to the soundness of `reasoning.md`, not the accuracy of prose forecasts or individual mechanical claims.

## Leakage and scoring boundaries

The log records 28 calls on September 18, before the October 5 resolution, with 26 captured results and two unobserved web calls (coverage 26/28). Those two queries concern the older Groff precedent and its official opinion URL; they do not target this petition's later history. Although the retrieval note describes them as yielding no usable content, uncaptured results cannot independently corroborate that description. Their scope and chronology, rather than an assumed empty response, support the clean assessment.

The remaining queries concern provisioned case inputs, the committed statpack, and contract/output operations. The instruction-file search explicitly excludes the forbidden labeling subtree rather than reading it. There is no concrete indication of this petition's outcome being known at prediction time. Mode is `forward`, retrieved outcome material is false, influence is `not_applicable`, and leakage is not suspected.

Cert votes are not scored. Semantic grades do not apply. Mechanical claim scores and harness-owned stamps are left absent.
