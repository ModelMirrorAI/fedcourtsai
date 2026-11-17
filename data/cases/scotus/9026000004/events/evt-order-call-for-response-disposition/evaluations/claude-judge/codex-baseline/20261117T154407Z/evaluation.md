# Evaluation: codex-baseline

Cert-stage cell (moment `response-requested`). Outcome: **denied** on 2026-11-16, no noted dissent, two distributions, no CVSG.

## Scores

- Predicted `denied` at P(grant) = 0.14: `correct` = 1, Brier = (0.14 - 0)^2 = 0.0196.
- Base rate, skill and claim scores are the harness's; left unset.

## Reasoning quality: 0.78

Careful and accurate. Record facts check out against the staged petition: 1985 registration, a collateral default-judgment dispute with two appeals, the Court of Appeals not deciding the consent-notice question, one amicus. It separates the petition's advocacy from established fact (the "wrong defendant" story; the cited out-of-state decisions being the petition's account), and it declines to assert forfeiture or an adequate state ground it could not establish from the record while still weighting the risk. The brief in opposition later pressed exactly that risk.

The anchor is right: 660 / 12,913 pooled over OT2017-OT2025 reproduces from the statpack build in force at its run (`statpack-at`, build 7bcde3b105cb). It is explicit that the relist, CVSG and amicus cuts are terminal, overlapping populations and that no response-request-conditioned rate exists, so the upward move is judgment.

The most valuable step is doctrinal: it read *Mallory* itself and found that footnote 5 rejects a magic-words requirement and mentions Georgia, which undercuts the petition's express-statutory-notice framing. That is a real reason to doubt the split, not a generic vehicle complaint.

Where it falls short: having built a strong case against the vehicle and against the split, it still lands at 0.14, nearly three times its anchor and the highest of the cell. The reasoning lists more and weightier downward factors than upward ones, so the number sits above what its own analysis supports. The outcome (a quiet denial at the first post-response conference) is consistent with that. The prose is also heavy on process caveats relative to analysis.

## Predicted reasoning: 0.7

Central claims: (1) denial without a separate writing; (2) at least one more distribution, with exactly one the modal path; (3) no CVSG.

All three are borne out (one further distribution on Oct 28 for the Nov 13 conference, denial Nov 16, no CVSG, no writing). The document commits to the modal path and is right, but it is hedged throughout ("most likely", "possible but not my central prediction") and does not commit to when the petition would be decided, so it carries less discriminating content than a forecast naming the conference. The question-presented, route and likely-author passages are conditional on a grant or a writing that did not occur and earn neither credit nor penalty.

## Leakage

Forward cell, predicted 2026-10-29 while the petition was pending. The five web calls are unobserved in the log; their queries all target the 2023 *Mallory* slip opinion, which predates the event and is general precedent. `not_applicable`.
