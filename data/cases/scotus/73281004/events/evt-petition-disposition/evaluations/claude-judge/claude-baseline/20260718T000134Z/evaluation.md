# Evaluation — claude-baseline / scotus/73281004 / evt-petition-disposition

**Outcome:** `dismissed` (Petition Dismissed — Rule 46, entered 2026-07-17).
**Prediction:** `dismissed`, P(granted) = 0.01 → correct = 1, Brier = 0.0001.

## What the prediction got right

- **The dispositive signal, correctly weighted.** The reasoning centers the
  June 30, 2026 joint motion to dismiss and names the controlling mechanism —
  Supreme Court Rule 46.1, under which the Clerk enters an agreed dismissal
  without referring it to the Court. That is exactly what happened seventeen
  days later ("Petition Dismissed - Rule 46"). Identifying jointness from the
  filed document's caption (`MANEY-JOINT MODM`) when the docket entry text
  alone didn't say "joint" was careful reading of the provisioned record.
- **Calibrated residuals.** The explicit branch weighting (~0.93 dismissed /
  ~0.06 denied / ~0.01 granted) reserves probability for the motion failing,
  and correctly reasons that even in that branch the petition's grant odds
  were modest: fact-bound, vehicle-specific QPs, interlocutory QI posture, no
  split claimed. The residual grant probability of 0.01 is defensible rather
  than performatively zero.
- **Honest treatment of the pre-dismissal cert posture.** It credits the
  April 2 call for a response as a genuine chamber-interest signal while
  correctly noting a bare CFR is weaker than a CVSG, flagging its own
  extrapolation from the statpack's CVSG rate (~27%) rather than presenting
  it as a measured CFR rate.
- **Base rates used properly.** Statpack disposition splits and five corpus
  dismissed-petition priors corroborate, not drive, the case-specific signal.

## Quibbles

- The CFR "triples-to-quadruples" multiplier is an admitted extrapolation
  from CVSG numbers; harmless here since it only priced a residual branch.
- `input_snapshot` points at `record/snapshots/2026-07-16.json`, which has
  since been superseded in the repo by the 2026-07-17 refresh — a provenance
  note, not a fault of the prediction.

## Reasoning quality: 0.95

Correct mechanism, correct rule number, calibrated decomposition, transparent
sourcing, and explicit mode/leakage self-awareness. Deducted slightly for the
extrapolated CFR multiplier presented with more precision than the data
supports.

## Leakage

Forward mode, confirmed genuine: the prediction ran 2026-07-16 and the
dismissal was entered 2026-07-17, so no disposition existed to leak. The
harness log shows provisioned reads, statpack greps, and one corpus query for
*other* dismissed-petition priors (retrieved doc date 2026-06-29 — before this
event's resolution, and not this case). No CourtListener or web lookups.
`not_applicable`, nothing suspected.
