# Evaluation — claude-baseline, evt-order-response-requested-disposition

**The cell is interim** (a stay application, `response-requested` moment), so
the baseline and skill are the harness's: `segment_base_rate` and
`brier_skill_score` are stamped by `stamp-cell` from the committed statpack's
interim section, and `base_rate_basis` stays null structurally — the interim
pool is no salience-band product. The pool the stamp should find: for a
Term-2026 application, Terms 2025 (16/178) and 2024 (14/47) pool to 30/225 ≈
13.3%, clearing the 50-resolved floor — a stamped rate is expected rather than
a refusal. No votes were predicted and none is scored on this stage.

**Outcome.** Denied on 2026-08-24 — denied as moot, in the same order that
granted the parallel presidential application (26A124) and stayed the
District of Massachusetts injunction pending appeal (`actual_disposition` =
`denied`, `actual_granted` = 0, read as recorded).

**Scores.** `predicted_disposition` = `denied` matches: `correct` = 1.
`brier_score` = (0.15 − 0)² = 0.0225 — the best of the three candidates.

**Reasoning quality: 0.9.** The strongest analysis in the cohort, and the one
the realized order most closely vindicates. The predictor found the companion
federal application in the same matter and priced this cell *conditionally on
it* — explicitly holding that a denial of the states' application "for want of
standing or as duplicative is live even in the scenario where the federal
application succeeds." That is nearly verbatim what happened: the federal
application was granted and this one was denied as moot. Beyond that
structure, the cell anchored on the correct strictly-prior pooled baseline
(30/225 ≈ 13.3%) with the right caveats (right-censored escalation counts,
scored-population selection), identified the intervenor-standing weakness,
read Purcell in the correct direction (denial preserves the status quo — the
inverse of gemini-baseline's reading), applied the denial-first convention to
partial relief, showed its arithmetic, and stated where to discount it. The
deductions are small: the decomposition's tandem-grant term (P ≈ 0.6 that a
federal grant carries this application to an unqualified grant) sat well above
what its own duplicative-denial insight supports — followed through, that
insight points below 0.15, and the outcome bore it out — and part of the
underlying-litigation account leans on training-data knowledge rather than
retrieved text, which the predictor itself disclosed.

**Leakage.** Forward and confirmed: resolution postdates the prediction by
four days; the candidate additionally self-bounded its docket-entry retrieval
to pre-cutoff dates. One thing worth naming, though it is not leakage: the
candidate read another predictor's committed `prediction.json` for the
companion case (scotus/9526000124) — disclosed in its retrieval note, stated
as read "for field conventions" while also yielding forward signal about the
companion application's state. Forward retrieval is unrestricted and the
disclosure is a point for the cell's integrity, but it is a cross-predictor
anchoring channel a maintainer may want to know exists; flagged at info
severity in this run's `flags.json`. `not_applicable`.

**Big case.** My independent read is 0.9 — see the JSON notes.
