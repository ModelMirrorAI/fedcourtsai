# Evaluation — codex-baseline

**Cell:** scotus/9026000062, `evt-petition-disposition` (cert stage, *Custodia Bank, Inc. v. Federal Reserve Board of Governors*, No. 26-62). Outcome: **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

## Scores
- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 − 0)² = 0.0144.
- Base rate, skill and claim scores are the harness's; I wrote none. No votes are scored on a cert cell.

## Reasoning quality — 0.80
A careful and accurate rationale. It reads the docket correctly (one distribution, three amicus briefs, extensions that are not response requests, the reply's "Distributed" tag not a second distribution), uses the frozen risk-set anchor rather than the terminal rate, and is explicit that the statpack's relist, CVSG and amicus buckets are terminal-state cross-checks and not conditional probabilities for this petition. It identifies the controlling weaknesses — the conceded absence of a split, the waived Appointments Clause argument, the proposed payment-account rule as a reason to wait — and is disciplined about not treating the briefs' accounts as verified fact. The one soft spot is the size of the upward move: lifting a 5.2% anchor to 12% on importance, a dissent and three amicus briefs, against SG opposition and no split, was somewhat generous, and the rationale gives the Solicitor General's opposition less weight as a denial signal than it deserved. The denial at first conference is consistent with the analysis but sits on the side of it the number under-weighted.

## Predicted reasoning — 0.80
Central claims: denial; zero additional distributions with the denial on the order list after the 11/13 conference, "likely November 16"; no CVSG; no noted dissent or statement. All borne out, and the second is the most specific procedural call in the cell — a committed path and date that the docket matched exactly. The stated reasons for denial cannot be checked against an unexplained order. It stays below the top anchor because denial without relist was the favoured outcome on the record. Conditional content on the question taken and the plenary route never came into play.

## Leakage
Forward, `not_applicable`. The prediction predates the disposition by two weeks. Three web calls are unobserved in the log; their queries target the statute's text and the Court's rules page, not this case, and the candidate discloses them as returning nothing. No outcome-revealing material appears.

## Big case — 0.50
Sector-important statutory question about master-account access, with no split and a quiet denial.
