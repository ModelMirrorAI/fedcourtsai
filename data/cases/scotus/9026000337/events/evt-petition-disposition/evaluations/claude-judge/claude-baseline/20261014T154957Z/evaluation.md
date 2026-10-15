# Evaluation — claude-baseline

**P(grant) 0.01, predicted `denied` → correct = 1, Brier = 0.0001.**

## Cell

Cert-stage cell (`event.yaml` `stage: cert`), forward. Outcome: `denied`, `actual_granted` 0, resolved 2026-10-13 after one distribution, no CVSG, no noted dissent from denial. The prediction froze `context.band` `baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `vote_accuracy` omitted (cert stage). No `semantic_grades` (cert cells declare no semantic set). `claim_scores` is computed by the harness and not graded here.

## Big case (my own read): 0.12

One petitioner's coverage dispute under a 2003 Iowa group long-term-care policy. The Erie framing does not change that the question turns on Iowa insurance law and the policy text. It may matter to guaranteed-issue LTC insureds under NAIC-modeled regimes, but there is no split and no broad federal question. The Court denied it at the first conference, with the response waived and no dissent.

## Reasoning quality: 0.88

A strong rationale. It anchors explicitly on the sal-v4 baseline `reached` pool from the statpack (prior Terms only), then adjusts down for named, case-specific reasons that all held up: the petition admits there is no split (novelty is not conflict), the QP is a state-law correction in Erie dress, and the respondent waived with a single distribution. Its best point reads Appendix A closely: the panel's primary ground was the policy's plain "existing loss" terms plus the Iowa statute's allowance, not the known-loss doctrine the petition attacks. That mismatch weakens both the grant ask and the McKesson-style certification remand. It handles the sympathetic facts honestly. It also caveats the missing BIO and the weak corpus retrieval. A minor overreach: the remarks on counsel's practice profile are weakly probative. Overall the analysis matches the realized denial for the right reasons.

## Leakage

Forward; `not_applicable`. Retrieval was two generic `fedcourts query` calls and two CourtListener doctrine-term opinion searches. None targeted this docket. The one captured result date is 2018. Nothing about this case's disposition could exist at prediction time (2026-09-27), and none surfaced.
