# codex-baseline: P(grant) 0.78, predicted granted; actual denied

## Cell

Interim stage (stay application 26A477, NRCC/NRSC v. Sherrod Brown, stay of a Fourth Circuit mandamus order directing the FCC to act). The Court resolved it on 2026-10-14 as **denied** (`actual_granted` 0). The cell is interim, so `segment_base_rate` and `brier_skill_score` are not mine to write. The harness stamps both from the pool of substantive grants in the statpack's interim section over application-Terms before 2026, and clears both if the pool falls below its registered floor. If they come back null, the reason is a thin or missing pool, not a choice I made. `base_rate_basis` is null by structure. No votes were predicted, and they would not be scored at this stage. No semantic set is declared, so there is no `semantic_grades` block. The claim scores are the harness's.

## Scores

- correct: 0 (granted vs denied)
- brier_score: (0.78 − 0)² = 0.6084

## Reasoning quality: 0.55

This is the most careful analysis of the three. It anchored on the same strictly-prior pool (53/549 = 9.65%) and said explicitly that its case-specific signals are correlated and not independent multipliers. It also set out the respondents' position accurately and in detail: mandamus compels a decision, not a result; the FCC could deny review and leave the notice in force; so the harm found on September 4 does not carry over automatically. It even said that the Court "could deny a stay without repudiating September 4", which is close to the reasoning the outcome bears out. It also checked the governing Hollingsworth stay standard against the opinion text itself.

Where it falls short: having stated that distinction, it still landed at 78%, and nothing in the rationale explains why the stay-precedent signal should outweigh it by that margin. Its account of the applicants' "strongest argument" (equity and respect for the earlier stay) is reasonable, but it is presented more confidently than the record warrants. Calibration is the main miss; the legal analysis itself is sound.

## Leakage

Forward mode. The only external lookups were for general law (Hollingsworth v. Perry, 47 U.S.C. 155). The web rows were unobserved, so I graded them on their queries, and none of those queries names this application. The qp-topics path was excluded in its find command. Graded not_applicable.

## Big case

My own read is 0.5. See `big_case.notes`.
