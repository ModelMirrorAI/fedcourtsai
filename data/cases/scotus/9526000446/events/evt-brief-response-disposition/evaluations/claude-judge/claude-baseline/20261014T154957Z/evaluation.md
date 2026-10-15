# Evaluation — claude-baseline

## Cell and outcome

This is an **interim** cell: the Kyle Wagner v. United States stay application (26A446), at the `response-filed` moment. The outcome is `denied` (`actual_granted` 0), resolved 2026-10-13, after the application was referred to the Court. There were zero amicus briefs and no recorded votes. Because the cell is interim, the segment base rate and the Brier skill score are the harness's: `stamp-cell` pools the substantive interim slice over application-Terms strictly before 2026. I wrote neither and left `base_rate_basis` null. If the stamped rate comes back null, the pool fell below its registered floor. The prediction's `context.band` is null, which is the ordinary interim shape, so no flag is needed. `vote_accuracy` is omitted because votes are never scored off a merits cell. `semantic_grades` is omitted because no semantic set is declared on an interim cell. `claim_scores` is the harness's.

## Leakage

The prediction ran **forward** (`mode: forward`, cutoff 2026-10-09, created 2026-10-09), before the 2026-10-13 resolution. I confirmed that nothing in the log or the reasoning shows this application's disposition as already decided, so I graded it `not_applicable`.

## Scores

- `predicted_disposition` `denied` against `denied`, so `correct` = 1.
- P(grant) 0.04, so `brier_score` = 0.0016.

## Reasoning quality: 0.85

This is the strongest rationale of the cell. It anchors on the stage-correct statpack pool (31/301 = 10.3%, Terms 2024–2025) and names that pool's coverage weakness. It then moves down for reasons that track how the emergency docket actually works:

- A private criminal defendant seeking release almost never gets a stay, while the pool is dominated by government applicants.
- The SG's opposition is real, including the earlier denial in Gray v. United States and the narrowed split.
- There is a mootness and self-inflicted-delay vehicle problem with trial set for January 2027.
- The equities on the record recited from the Sixth Circuit opinion cut against release.

It weighs the counter-signals honestly: the response call (correctly treated as routine on a counseled application), the October 6 letter, and the dissent below. It also states the scenario under which its number would be badly wrong. It read the primary filings (application, opposition, letter, circuit opinion) rather than relying on the application alone.

The minor deductions are two. The "dominated by government applicants" premise about the pool is asserted, not shown from the pack. The 0.04 sits below the anchor by a large judgmental factor without much attempt to quantify it.
