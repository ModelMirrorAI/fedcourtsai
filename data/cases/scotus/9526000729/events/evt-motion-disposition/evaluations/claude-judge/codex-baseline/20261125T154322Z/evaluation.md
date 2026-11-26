# Evaluation - codex-baseline, scotus/9526000729, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: a stay application (26A729), filed with a motion for leave to file under seal, from the Supreme Judicial Court of Maine. Justice Jackson denied both on 2026-11-23, six days after submission, with no response requested, no referral to the Court and no amicus filings. The outcome records the finer reading (`interim_reading: denied`, `interim_granted: 0`).

- Predicted `denied` at probability 0.02: `correct` = 1, `brier_score` = 0.0004.
- `vote_accuracy` is omitted, as on every interim cell.
- The segment base rate, the skill score and `claim_scores` are the harness's to stamp and are left unset here. The prediction froze no band, so no flag is needed.
- No semantic set is declared on an interim cell, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.7)

A careful rationale that is honest about how little the record shows. It pools the interim counts correctly, picks the private/unmarked cell and says why it prefers it to the two margins, and discounts further because the applicant is an individual in a dispute with another individual, using a named institutional application as a contrast. It states the stay standard accurately and identifies what it could not see and what would move the estimate.

It scores lowest of the three on analysis because the downward adjustment is the least developed: a five-point move is asserted from the individual-versus-individual caption alone, and its searches came back empty, so nothing case-specific supports it. Its referral figure (24%) is justified only by the remark that referral can accompany a summary denial, which does not engage with how a first application to the Circuit Justice is usually handled.

## Predicted reasoning (`predicted_reasoning_quality` = 0.8)

I treated as central: denial by Justice Jackson herself within about two weeks; no response and no referral; no amicus and no signed explanation; and the stated basis. The first three are borne out by the Nov 23 entry and the outcome's interim signals; the basis is unresolved because the order gives no reasons, and it is in any case a restatement of the stay standard rather than a discriminating call. The document commits to the single-Justice route, which is the part a reader could have got wrong, but it is silent on the sealing motion, which the order also disposed of. Right and reasonably specific, with less committed than the other two.

## Leakage

Forward cell (cutoff 2026-11-18, arrival-position; prediction written 2026-11-21, event resolved 2026-11-23). Captured coverage is partial (about 0.45), so the unobserved rows are graded on their queries: CourtListener searches for the Maine docket and caption were date-bounded before 2026-11-18, plus Hollingsworth and a 2022 application as a comparator. The latest legible document date is 2022-09-14. No query reaches this application's disposition and the reasoning does not presuppose it. Graded `not_applicable`; `leakage_suspected` is false.

## Big case

My own read is 0.02: a private family-type dispute between two individuals, resolved by a one-line chambers denial.
