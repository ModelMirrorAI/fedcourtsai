# Evaluation — codex-baseline

## Cell
Interim cell (stay of execution pending cert, 26A634, linked with 26-6051), forward mode. Outcome: `denied`. `interim_reading` is `denied` and `interim_granted` is 0. The Nov 5, 2026 order reads "presented to Justice Thomas and by him referred to the Court is denied", and cert was denied in the same order. Signals: referred to the Court, no response requested (the State filed on its own Nov 4), no amicus, no noted dissent or writing.

The baseline and skill are the harness's (`stamp-cell` pools the substantive slice's finer-reading grant rate over application Terms before OT2026). I write neither. All three predictors reported that the statpack they read at prediction time had no finer-reading counts (`finer_unread` non-zero in every pooled Term), so they anchored without a published baseline. The pack now committed carries finer counts with `finer_unread` 0 for OT2016–OT2025. The stamped rate should therefore be computable, but whether it is null is the stamp's call. I quote no figure. The claims block (`interim-v3`) is computed in code and not graded here. No semantic set is declared on an interim cell. Votes are not scored on this stage.

## Big case
My read is 0.15: fact-bound capital maladministration claim, one-line denial, no writing.

## Scores
- `correct` = 1 (predicted `denied`). `brier_score` = (0.08 − 0)² = 0.0064.

## Reasoning (`reasoning_quality` 0.7)
Careful and honest about its information set. It verified Hill v. McDonough and Baze passages on CourtListener, separated the cognizability of the claim from entitlement to a stay, and correctly located the main obstacle in merits likelihood against adverse findings. Its baseline audit is scrupulous. Weaknesses: it treats the timing/discovery argument as a material route to relief, and that is why the probability is 8%. That is high for a referred last-minute capital stay against unanimous lower-court findings, and the outcome gave no sign of traction (no noted dissent). It also misses the CA11's alternative-method ground. Its 80% response-request estimate rests on a misreading of practice in Florida warrant cases, where the State files without a call. The rationale for that claim is part of reasoning.md, but it is graded only for soundness here, not scored.

## Predicted reasoning (0.7)
Central claims: (1) a formal call for Florida's response (80%): not borne out, since the State filed Nov 4 with no request entry; (2) referral to the full Court: borne out; (3) denial by a brief unsigned order: borne out; (4) disposition on Nov 5: borne out; (5) no separate writing as the modal outcome: borne out. The disposition and route held. The one specific procedural call it led with failed, and its remaining claims are fairly generic. That puts it at the 0.75 anchor, slightly lower.

## Leakage
Forward, `not_applicable`. The prediction was created 2026-11-04T23:13Z. Two unobserved web searches are graded on their queries: general precedent, never this case. The corpus query was restricted to before 2026. No outcome material.
