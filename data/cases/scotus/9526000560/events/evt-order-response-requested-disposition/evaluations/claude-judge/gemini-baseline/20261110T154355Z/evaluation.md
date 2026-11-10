# Evaluation — gemini-baseline

**Correct: 1** (predicted `granted`; actual `granted`). **Brier: 0.0625** (p = 0.75).

## Cell

Interim stage (stay application 26A560), forward mode. The outcome is an unqualified grant on Nov 9, 2026 (`interim_reading` granted, `interim_granted` 1), disposed of by a short per curiam with Justice Jackson noting she would deny. `correct` and `brier_score` are scored against `interim_granted`. The interim baseline and skill (`segment_base_rate`, `brier_skill_score`) are the harness's to stamp, so I left them null. I quote no rate of my own: refer to the stamped segment base rate. On an interim cell no votes are scored and no semantic set is declared.

## Leakage

Forward cell. The prediction was made 2026-10-23, before the 2026-11-09 resolution. The log shows no document dated on or after resolution and no query for this application's outcome. Graded `not_applicable`.

## Reasoning (reasoning_quality 0.72)

This is the most heavily researched rationale. It read the district court's opinion and stay denial and built a reference class of recent SG stay grants. It correctly puts §102(c)(2)(A) and Dalton first, and it treats the absence of any court of appeals as the reason the Supreme Court alone can check the injunction, a point the per curiam also notes. Deductions:
- It says the injunction rested "solely" on a nonconstitutional ultra vires §102(a)/(b) claim. The record (per curiam) shows the district court took jurisdiction by treating a *major-questions* claim as constitutional. The rationale's own Learning Resources discussion half-captures this, but the jurisdictional framing is off.
- It cites $173,000 a day in standby costs. The figure the Court relied on is nearly half a million dollars a day.
- It spends real weight on CASA overbreadth and a partial carve-out for the church (about 0.13). Neither appeared in the outcome, and they pulled its probability down further than its own reference class supported.

Its downside scenarios were stated clearly and reasonably, and the forfeiture point was a genuine risk factor to weigh.

## Predicted reasoning (0.68)

Central claims: an unqualified full stay pending cert (borne out); a primary §102(c)(2)(A)/Dalton jurisdiction ground (borne out in direction, though framed around §102(a)/(b) predicates rather than the relabelled major-questions claim); secondary grounds of Learning Resources on the merits and CASA overbreadth (not borne out, since the Court did not reach either); a 6–3 lineup with a written dissent (not borne out: only Jackson noted, and no one wrote); timing Nov 2–9, referral and amicus (borne out). The disposition and the primary ground held. The specific secondary grounds and the lineup did not, which places the document in the 0.5–0.75 band.
