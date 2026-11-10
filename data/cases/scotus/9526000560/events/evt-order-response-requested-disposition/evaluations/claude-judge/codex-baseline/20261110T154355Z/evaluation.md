# Evaluation — codex-baseline

**Correct: 1** (predicted `granted`; actual `granted`). **Brier: 0.0169** (p = 0.87).

## Cell

Interim stage (stay application 26A560), forward mode. The outcome is an unqualified grant on Nov 9, 2026 (`interim_reading` granted, `interim_granted` 1), disposed of by a short per curiam with Justice Jackson noting she would deny. `correct` and `brier_score` are scored against `interim_granted`. The interim baseline and skill (`segment_base_rate`, `brier_skill_score`) are the harness's to stamp, so I left them null. I quote no rate of my own: refer to the stamped segment base rate. On an interim cell no votes are scored and no semantic set is declared.

## Leakage

Forward cell. The prediction was made 2026-10-23, before the 2026-11-09 resolution. The log shows no document dated on or after resolution and no query for this application's outcome. Graded `not_applicable`.

## Reasoning (reasoning_quality 0.85)

The rationale picks out the route the Court actually took. Its jurisdiction argument is the strongest one: a major-questions objection is a claim of excess statutory authority, and Dalton v. Specter (472–474) means such a claim is not a constitutional one under §102(c)(2)(A). The per curiam rests on that same distinction and cites the same pages of Dalton. The rationale also leans correctly on the applicant's ~$460,000-a-day suspension costs; the Court relied on "nearly half a million dollars" a day that "cannot be recouped". It keeps the unqualified-grant target separate from favorable-but-mixed relief and lists honest countervailing factors (the one-sided record, the delay before applying, a refusal to treat Sierra Club as controlling). Its large move up from the base rate is openly labelled judgment rather than an estimated conditional rate, which is honest but unquantified. Small deductions: the secondary statutory-merits argument, which the Court did not need, gets nearly as much weight as jurisdiction.

## Predicted reasoning (0.90)

Central claims: an unqualified stay pending cert rather than summary reversal (borne out); the jurisdiction ground framed exactly as a major-questions claim attacking statutory authority (borne out, and specific); concrete construction costs as support (borne out); procedural rungs (referral and one amicus, both borne out). The one miss is the timing window, Oct 30–Nov 6; the order came Nov 9. The document is specific on the disposition and the ground and commits to no vote lineup. It sits just below the top anchor because of the timing miss.
