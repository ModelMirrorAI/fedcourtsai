# Evaluation — codex-baseline

**Cell:** scotus/9026000100, `evt-petition-disposition` (stage `cert`). Outcome: petition **denied** on 2026-11-16, after a second distribution (Oct 28, for the 11/13/2026 conference), no CVSG, no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.10 − 0)² = 0.01.
- `vote_accuracy` omitted (cert stage). The base rate, basis and skill fields are left to the harness stamp; `claim_scores` is the harness's.

## Reasoning quality — 0.70

The rationale is careful and honest about its information set: it states what was provisioned, what was not (no reply, no amicus text, no video), and that its factual statements are the parties' advocacy rather than findings. It anchors on the pooled risk-set rate for its frozen band over strictly prior Terms, declines to promote the petition into stronger terminal relist/CVSG buckets, and reads the Ninth Circuit memorandum independently of the opposition's description of it. Its legal framing is sound: Rule 10's error-correction distinction, Ames as a narrow holding with a separate concurrence rather than a majority invitation, Hittle as context rather than precedent.

What costs it: the net adjustment went the wrong way for the reasons it itself laid out. Having catalogued an unpublished memorandum, no asserted conflict on a rule, a fact-tangled question and a preservation problem, it still roughly doubled the anchor on the strength of the response request and four amicus entries, and it did not weigh the Court's recent refusals of the same question as heavily as the record invited. The Court denied at the first post-opposition conference without a writing. One denial does not show 0.10 was miscalibrated, but the upward move was the least well-supported step in an otherwise disciplined analysis, and it is acknowledged as a judgmental doubling rather than a conditioned rate.

## Predicted reasoning — 0.75

Central claims: denial without separate writing; one further (post-opposition) distribution followed by denial in November or December 2026; no CVSG; vehicle quality as the reason. The first three were borne out on the docket and outcome record. The stated ground is unresolved — the denial is unexplained. The document is specific on the procedural path (one redistribution, not a true relist) but hedges the timing across two months and does not commit to denial at the first post-opposition conference, which is what happened. The conditional-on-grant content (narrowed question, 0.35 summary route) earned neither credit nor penalty.

## Leakage

Forward cell, predicted 2026-10-25 against a case resolved 2026-11-16. The log's web calls are result-unobserved; their queries are general (Ames, Rule 10, the Court's rules PDF) and none reaches this petition's docket. No outcome material; `influenced_prediction` = `not_applicable`.

## Big case

My own read: 0.30 — an important abstract question in a weak, fact-bound vehicle that the Court declined without comment.
