# Evaluation — codex-baseline / scotus/73281004 / evt-petition-disposition

**Outcome:** `dismissed` (Petition Dismissed — Rule 46, entered 2026-07-17).
**Prediction:** `dismissed`, P(granted) = 0.002 → correct = 1, Brier = 0.000004.

## What the prediction got right

- **The dispositive signal.** It correctly read the June 30 dismissal motion
  as controlling, noted the linked filing's filename identifies it as joint,
  and reasoned that a consensual request to terminate makes any grant
  extraordinarily unlikely. The realized Rule 46 dismissal on July 17 bears
  this out.
- **Disciplined inference.** It explicitly declined to speculate about *why*
  the parties sought dismissal (the motion text was not provisioned) — a
  nice epistemic boundary its peers mostly crossed by assuming settlement.
- **The counterfactual cert merits are well argued.** The conditional
  analysis (CFR as grant-side signal vs. no split, unpublished memorandum,
  aggregated multi-facility record, interlocutory QI posture) is accurate
  and appropriately hedged, and it correctly identified the statpack's
  ordinary-petition anchors (3.0% ca9 grant rate, 0.8% no-relist rate, ~2%
  dismissal rates) as not capturing an already-filed dismissal motion.
- **Honest tooling disclosure.** The failed corpus query (unresolvable
  remote host) and the empty CourtListener searches for the lower-court
  opinion are disclosed in the reasoning and retrieval log; the legal
  analysis is expressly grounded on the petition's own account. That is the
  right way to handle a degraded tool.

## Quibbles

- P(granted) = 0.002 is aggressive; with a live (if small) branch where the
  motion is withdrawn and the CFR-flagged petition returns to conference,
  something nearer 0.005–0.01 is easier to defend. The Brier outcome rewards
  the aggression here, but the calibration argument is thinner than
  claude-baseline's explicit branch decomposition.
- It does not name Rule 46.1's clerk-entry mechanics, though the functional
  reasoning is equivalent.

## Reasoning quality: 0.93

Sound mechanism, careful conditional analysis, exemplary disclosure of
retrieval failures. Slightly below claude-baseline only for the thinner
residual-branch accounting behind the very low tail probability.

## Leakage

Forward mode, confirmed genuine: predicted 2026-07-16, dismissal entered
2026-07-17. The log shows provisioned reads, statpack greps, one failed
corpus query, and three CourtListener opinion searches aimed solely at the
2025 Ninth Circuit decision below (the one legible retrieved doc date,
2025-09-15, is an unrelated result pre-dating the event). Its retrieval note
"No search sought this Supreme Court petition's disposition or subsequent
history" matches the harness log. `not_applicable`, nothing suspected.
