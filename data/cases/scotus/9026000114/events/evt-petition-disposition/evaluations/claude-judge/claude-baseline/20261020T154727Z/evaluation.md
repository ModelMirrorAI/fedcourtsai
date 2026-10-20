# Evaluation — claude-baseline

## Cell

Cert-stage, forward cell: *Allen v. Stein* (scotus/9026000114), `evt-petition-disposition`. Outcome: **denied** on 2026-10-19 (`actual_granted` 0), two distributions, no CVSG, no noted dissent from denial. The prediction froze `context.band` = `elevated` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's risk-set stamp; I left them null and quote no rate of my own. Where comparison matters, read it against the stamped segment base rate. `correct` and `brier_score` below are my elicited reads, which the stamp recomputes and compares.

No semantic block applies (cert stage); votes are not scored at cert.

## Scores

- Predicted `denied`, P(grant) = 0.13 → **correct = 1**, **Brier = 0.0169** (best of the three).

## Reasoning quality: 0.85

A strong, well-structured analysis that the denial bears out. It anchors on the elevated band's pooled rate. It then moves **down** for reasons it checked against the lower-court opinion itself: the Fourth Circuit expressly invoked "either prong" of *Swint*, which supports the BIO's account that the court applied the majority rule rather than adopting a new "but-for" test. That turns QP 1 into an error-correction ask. It also weighs the contestable split, the lack of amicus support, the unattractive second-trip posture, and the weak summary-reversal case on QP 2 (party presentation). It explicitly avoids double-counting the response request ("mostly priced into the anchor") and correctly declines to treat two distributions as two relists. It gives a plausible range and states its own limits (reply brief unread, relist estimate not corpus-conditioned). Minor deductions: the summary-route and relist figures rest on general knowledge, as it acknowledges.

## Leakage

Forward; `not_applicable`. The log is fully captured. Corpus queries (prior trip No. 18-877, Swint cite, 2020s grants) and CourtListener reads of the January 2026 Fourth Circuit opinion all predate the event. None targeted this petition's disposition. The reasoning treats the petition as pending for the October 16 conference.
