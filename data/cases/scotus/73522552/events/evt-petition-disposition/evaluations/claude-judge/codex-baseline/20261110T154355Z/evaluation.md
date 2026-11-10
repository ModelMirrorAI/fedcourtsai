# Evaluation — codex-baseline, scotus/73522552 (Isaacson v. Moses, No. 25-1411), evt-petition-disposition

**Stage:** cert (forward, `distribution` moment, snapshot 2026-10-06). **Outcome:** denied on November 9, 2026, after a single post-briefing distribution (Oct 7, for the Nov 6 conference). There was no CVSG and no noted dissent.

## Score
- Predicted `denied` at P(grant) = 0.28. `correct` = 1. Brier = (0.28 − 0)² = **0.0784**.
- The segment base rate and skill are stamped by the harness from the frozen `baseline` band (sal-v4) risk set; see the stamped segment base rate. I did not compute my own.

## Reasoning (reasoning_quality 0.6)
The anchor is done carefully: the candidate pooled the sal-v4 `baseline` bracketed reached rate over OT2017–OT2024 (593/11,580 ≈ 5.1%), which matches the pack it was placed against. It also correctly treats the relist and CVSG tables as describing terminal states, not as a forward hazard. The upward signals it names are real: the conceded circuit split, the response the Court requested after both respondents waived, and the Chamber amicus. It reads the vehicle problems fairly: unpublished summary order, uncontested $5,000 amount, and the Times' plea for finality.

Two things hold the grade down. First, the jump from roughly 5% to 28% is large and only loosely argued. The candidate itself calls it "judgmental", and it leans heavily on the response request. That signal is weaker for a question the Court had recently and repeatedly passed over, but the candidate did not look into that history. Second, the result was a routine denial at the first conference after briefing, so 28% was well above what the record supported. The direction was right, but the size of the adjustment was not well calibrated.

## Predicted reasoning (0.75)
I treated as central the denial, the relist path (at least one more distribution, most likely one or two, with the first one just putting completed briefing before a conference), the timing (late Oct–Dec), no CVSG, and no separate writing on denial. All of these were borne out, and the relist forecast was notably specific: it correctly framed the next distribution as procedural rather than a substantive relist. The conditional grant content (which QP, 8% summary route) is unresolved and counts for nothing either way. The grade stops at 0.75 because most of these claims are what a routine-denial forecast would say anyway, and the document never committed to anything contrarian.

## Leakage
Forward cell, and the case was pending at the snapshot. The log shows reads of provisioned inputs and the statpack, plus one general Rules-of-the-Court search/fetch that returned nothing usable. There was no case-outcome material. `influenced_prediction` = `not_applicable`.

## Big case
The evaluator's read is 0.4: a real split on an issue that touches most class settlements, but a weak vehicle, a question the Court has repeatedly declined, and low public salience.
