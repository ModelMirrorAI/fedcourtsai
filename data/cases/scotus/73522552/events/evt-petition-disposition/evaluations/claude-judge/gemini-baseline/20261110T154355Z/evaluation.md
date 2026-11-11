# Evaluation — gemini-baseline, scotus/73522552 (Isaacson v. Moses, No. 25-1411), evt-petition-disposition

**Stage:** cert (forward, `distribution` moment, snapshot 2026-10-06). **Outcome:** denied on November 9, 2026, after one post-briefing distribution (Oct 7, for the Nov 6 conference). There was no CVSG and no noted dissent.

## Score
- Predicted `denied` at P(grant) = 0.20. `correct` = 1. Brier = (0.20 − 0)² = **0.04**.
- The segment base rate and skill are the harness's stamp; see the stamped segment base rate.

## Reasoning (reasoning_quality 0.4)
I checked the candidate's base-rate figure against the build it was placed against (`statpack-at`, commit 1c4f550b7b75, the same sal-v4 table). Its 5.7% is the correct OT2024 `baseline` reached figure. It is a single Term rather than a pool over prior Terms, which is a minor weakness but not an error. The signals it cites are accurate: the 5-1 split, the response requested after waivers, and the Chamber amicus. But the rationale is a single paragraph. The vehicle discussion is limited to "there may be vehicle issues", with no engagement with the briefs in opposition (summary order, uncontested amount, finality). It also gives no reason for 0.20 specifically rather than some other figure. The direction was right, but the analysis is thin.

## Predicted reasoning (0.35)
The document never states the disposition outright; it only says "should the Court deny". Its most specific central claim is that the petition would be "distributed and then relisted once or twice". That did not happen: the petition was distributed once after briefing and denied at that conference. "No CVSG" was borne out. The suggestion of a possible dissent from denial by conservative Justices did not happen either, though the claim was hedged. The grant-conditional content is unresolved. With a central path forecast that failed and the rest generic, the document sits between the 0.25 and 0.5 anchors.

## Leakage
Forward cell, and the case was pending. The log, where every result is unobserved, shows only local listings and file writes; the reasoning cites only provisioned entries through Oct 2. `not_applicable`.

## Big case
The evaluator's read is 0.4 (see reasoning in the JSON).
