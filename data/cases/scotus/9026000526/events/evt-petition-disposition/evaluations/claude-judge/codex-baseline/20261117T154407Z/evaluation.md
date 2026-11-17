# Evaluation — codex-baseline, scotus/9026000526, evt-petition-disposition

Cert-stage cell. The Court denied the petition on 2026-11-16, on the first order list after the single November 13 conference, with no relist, no CVSG and no noted dissent or statement.

## Scores

- Predicted `denied` at P(grant) = 0.025; actual `denied`. `correct` = 1, `brier_score` = 0.000625.
- `vote_accuracy` omitted (cert stage). The segment base rate, basis and skill score are the harness's to stamp and are left null; the claims block is scored in code.
- `reasoning_quality` = 0.85; `predicted_reasoning_quality` = 0.8.

## Reasoning

The strongest rationale of the three. It starts from the frozen cert anchor, says explicitly why the terminal relist/CVSG/amicus cuts are overlapping descriptions rather than independent likelihood ratios, and then adjusts down for the waiver, the absence of a response request and a weak conflict. Its distinctive contribution is doctrinal and checked against a source: it went to *United States v. Scott* itself and confirmed that the dismissal there also came at the close of all the evidence, which undercuts the petition's central distinction between a completed evidentiary presentation and an earlier procedural dismissal. It also read the appendix rather than the petition's characterisation (earlier directed-verdict motions denied, the final renewed motion not ruled on, dismissal on compulsory-process grounds followed by entry of an acquittal) — which the staged petition text bears out. It handles the state-law/finality point with care, declining to assert a jurisdictional bar. Uncertainty is stated honestly (appendix portions rather than the whole trial record; no opposition to test the reading). The 2.5% figure is a defensible halving of the anchor. Small deductions: some of the prose is procedural boilerplate, and the residual probability is argued qualitatively rather than derived.

## Predicted reasoning

Central claims: denial on the ordinary order list after the November 13 conference with no opinion; no further distribution as the modal path; no CVSG; no noted writing. All four are borne out by the outcome and docket. The document commits clearly ("will deny", "will not call", "No Justice will note") and names the timing. The conditional-on-grant content (narrowed question, plenary over summary) earns neither credit nor penalty. The grade stops short of the top anchor because every borne-out claim was the modal expectation for a waived, amicus-less first-conference petition: specific and right, but not calls a competent reader would plausibly have made otherwise.

## Leakage

Forward cell, prediction created 2026-11-05, eleven days before the 2026-11-16 denial. The log shows provisioned-input reads, statpack reads, corpus queries for unrelated 2020s denials (one legible doc date 2026-04-29, before resolution), two unobserved web calls whose queries target McElrath v. Georgia, and CourtListener lookups for United States v. Scott (1978). No query targets this petition's disposition and nothing dated on or after resolution appears. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My own read is 0.2: a fact-bound double-jeopardy classification dispute in one state prosecution, waived by the State, unsupported by amici, and denied without comment.
