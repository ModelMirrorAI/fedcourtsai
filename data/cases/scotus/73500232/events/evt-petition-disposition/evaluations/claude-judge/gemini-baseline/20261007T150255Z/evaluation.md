# Evaluation of gemini-baseline — scotus/73500232, evt-petition-disposition

**Cell.** Cert stage (`event.yaml`: `stage: cert`, `moment: distribution`), forward mode. Outcome: petition **denied** on the 2026-10-05 order list after a single distribution to the 2026-09-28 long conference, no response filed, no noted dissent (`actual_granted = 0`, `disposition_basis: standard`).

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` matches `actual_disposition: denied` |
| `brier_score` | 0.000001 | (0.001 − 0)² |
| `segment_base_rate` | 0.0512 | sal-v4 `baseline` band, bracketed `reached` figure pooled resolved-weighted over Terms 2017–2024 (≈593 grants / 11,580) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: baseline` **and** `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.9996 | 1 − 0.000001 / 0.0512² |
| `reasoning_quality` | 0.45 | below |

**Base-rate window.** Case Term 2025; the sal-v4 table renders 2017–2026 ("Most recent 10 of 10 Term(s)"), so the strictly-prior pool is 2017–2024, eight Terms, the whole rendered pack. No rendered-vs-held divergence to flag.

## What the prediction got right

- The direction and the headline call. Denied, at the first conference, no separate writing, no CVSG, no relist: the docket resolved exactly as the one-paragraph rationale said it would.
- The features it names are real and are the right ones: pro se petitioners, a decade-long residential foreclosure dispute, a fact-bound discretionary Rule 4(a)(5) denial affirmed by the Third Circuit, no amici, no brief in opposition.

## Where it is weaker

- **Wrong anchor.** The rationale anchors on "roughly 1.2% (at 0 relists)". That is the terminal 0-relist cut of the paid segment, not the sal-v4 band rate the cell froze and the evaluator scores against (5.1% on the risk-set basis). A terminal-state bucket conditions on the petition having *ended* with zero relists, which a forward cell cannot know; the registered band figure exists precisely to avoid that. The number happened to be low and the outcome a denial, so the error cost nothing here, but the method is the one the prompt and the statpack caption both warn against.
- **No engagement with the petition's arguments.** Nothing on the asserted circuit split (built on a district-court decision and an unpublished 1996 opinion), nothing on the Rule 58 separate-document theory in QP 4, nothing on the unpublished status of the decision below. The rationale asserts "fact-bound" without showing it from the questions presented.
- **"No response requested" is the wrong signal.** A response request is a Court action; the informative fact on this docket is that no brief in opposition was *filed* and the petition was distributed after the response deadline. The rationale conflates the two.
- **The retrieval inference is thin.** "The MCP retrieval shows that the Third Circuit and other circuits regularly deal with these FRAP 4(a)(5) extensions, but they rarely warrant SCOTUS review" draws a conclusion from a hit count (397 results) that cannot support it.
- **Over-confidence at the floor.** 0.001 sits below any rate the committed pack supports for a paid petition that reached the baseline band, with no stated basis for a further ten-fold cut below the predictor's own (mis-chosen) 1.2% anchor. The Brier rewards it on a denial; the reasoning does not justify the magnitude. `confidence` is null.
- The candidate's `retrieval.md` says no corpus lookups were executed, while its captured log carries one corpus-query call (unobserved result). Likely a failed call reported as none; harmless for leakage, but the self-report and the log disagree.

## `reasoning_quality` = 0.45

Right call, right features, but a mis-chosen anchor, no engagement with the questions presented or the petition's own arguments, one conflated docket signal, and a probability pushed to a floor the reasoning does not earn. The score is for soundness of the analysis given the outcome, not for the Brier, which is the best of the three.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`; `influenced_prediction: not_applicable`; `leakage_suspected: false`. Prediction made 2026-09-17, before the 2026-09-28 conference. The log's capture coverage is 0.0, this engine's standing shape, so every call is graded on its query: a corpus query for Rule 4(a)(5) priors bounded `--decided-before 2026-09-17`, one CourtListener search for Rule 4(a)(5) good-cause/excusable-neglect case law, and provisioned-file reads. No query names this docket or caption, none reaches past the prediction date, no `data/qp-topics/` read. Not a mis-provisioned decided case: the snapshot the cell read (2026-09-17) ends at the distribution entry.

## Big-case read

`evaluator_score` 0.03. One household's property in a decade-long foreclosure fight, a two-day-late notice of appeal, an unpublished abuse-of-discretion affirmance, denied without comment. The predictors' own scores were visible in the staged `prediction.json` before this read was fixed, so independence is by discipline rather than by sequence.
