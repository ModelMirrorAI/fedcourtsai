# claude-baseline: P(grant) 0.82, predicted granted; actual denied

## Cell

Interim stage (stay application 26A477, NRCC/NRSC v. Sherrod Brown, stay of a Fourth Circuit mandamus order directing the FCC to act). The Court resolved it on 2026-10-14 as **denied** (`actual_granted` 0). The cell is interim, so `segment_base_rate` and `brier_skill_score` are not mine to write. The harness stamps both from the pool of substantive grants in the statpack's interim section over application-Terms before 2026, and clears both if the pool falls below its registered floor. If they come back null, the reason is a thin or missing pool, not a choice I made. `base_rate_basis` is null by structure. No votes were predicted, and they would not be scored at this stage. No semantic set is declared, so there is no `semantic_grades` block. The claim scores are the harness's.

## Scores

- correct: 0 (granted vs denied)
- brier_score: (0.82 − 0)² = 0.6724

## Reasoning quality: 0.50

Strengths: it anchored correctly on the strictly-prior interim pool (53/549 ≈ 9.7%). It also read both the application and the response, and named the response's strongest point, which is exactly where the denial turned out to rest. Brown I said the Commission must resolve every application, and the writ only compels the FCC to decide (it may even decide without reasons), so it intrudes far less than the vacatur the Court stayed on September 4. It also flagged mootness risk if the FCC rules.

Weaknesses: it identified that distinction and then priced it at only about 18% combined with every other downside. The upward adjustments are largely correlated (the prior stay, the administrative stay, the election proximity) yet were stacked as separate pushes. The prior stay rested on harm from actual vacatur of the Public Notice, a harm that a decision-forcing writ does not obviously reproduce, and the reasoning did not test that transfer. It says plainly that it read only parts of both briefs. The disclosure is honest, but the analysis is thinner for it.

## Leakage

Forward mode. No retrieval beyond provisioned inputs and the statpack; graded not_applicable.

## Big case

My own read is 0.5: real election-season stakes, but a narrow procedural question. See `big_case.notes`.
