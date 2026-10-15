# gemini-baseline: P(grant) 0.95, predicted granted; actual denied

## Cell

Interim stage (stay application 26A477, NRCC/NRSC v. Sherrod Brown, stay of a Fourth Circuit mandamus order directing the FCC to act). The Court resolved it on 2026-10-14 as **denied** (`actual_granted` 0). The cell is interim, so `segment_base_rate` and `brier_skill_score` are not mine to write. The harness stamps both from the pool of substantive grants in the statpack's interim section over application-Terms before 2026, and clears both if the pool falls below its registered floor. If they come back null, the reason is a thin or missing pool, not a choice I made. `base_rate_basis` is null by structure. No votes were predicted, and they would not be scored at this stage. No semantic set is declared, so there is no `semantic_grades` block. The claim scores are the harness's.

## Scores

- correct: 0 (granted vs denied)
- brier_score: (0.95 − 0)² = 0.9025

## Reasoning quality: 0.25

It quoted the correct 9.65% pool, then moved to 0.95 on a single argument: the Court stayed the first Fourth Circuit ruling, so it is "extremely likely" to stay this one, which it frames as an attempt to bypass that stay. It does not engage the respondents' opposition at all, and that opposition was in the provisioned record. In particular it never addresses the central distinction that a writ ordering the agency to decide does not vacate the Public Notice. Without that, it could not see why the September 4 rationale might not carry over. Its use of Purcell assumes the writ changes the election rules, which the writ does not do directly. Most of the factual content came from web news rather than the provisioned filings. The procedural account is accurate, but the legal analysis is thin and the confidence is far beyond what the argument supports.

## Leakage

Forward mode. The candidate ran at about 18:15 UTC on 2026-10-14, the same date the application was resolved. Its CourtListener docket query for 26A477 and its two web searches on the case caption are recorded as `unobserved`, so the log cannot show what they returned. Its own disclosure says the news it found ran up to the October 8 administrative stay. It forecast a grant at 0.95, the opposite of the actual denial, and nothing in its reasoning presupposes the result. I find no sign that this case's disposition surfaced, so I graded it not_applicable with the same-day timing noted.

## Big case

My own read is 0.5. See `big_case.notes`.
