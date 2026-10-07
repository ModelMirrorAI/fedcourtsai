# Evaluation: gemini-baseline

## Disposition and quantitative scores

The actual cert disposition is `denied`, `actual_granted: 0`, dated October 5, 2026. gemini-baseline's September 18 prediction names `denied` with P(any grant) = 0.005. Exact-label correctness is 1 and Brier is `(0.005 - 0)^2 = 0.000025`.

The frozen context, not the candidate's speculative explanation of it, determines the baseline: band `elevated`, version `sal-v4`, Term 2026. The committed `metrics/statpack.md` table matches that version. Using the bracketed reached figures for every displayed prior Term gives these `(rate, weighted n)` pairs for 2025–2017: `(0.135,275)`, `(0.179,336)`, `(0.175,354)`, `(0.190,300)`, `(0.205,342)`, `(0.161,397)`, `(0.138,334)`, `(0.159,347)`, `(0.175,400)`. Thus the pool is `521.511 / 3085 = 0.16904732576985413`, on the `risk_set` basis. The weighted numerator is reconstructed from rounded displayed percentages, not an observed grant count. Skill is `1 - 0.000025 / baseline^2 = 0.9991251705412212`.

All 10 of the pack's 10 available Terms are rendered; 2026 is excluded and the nine strictly prior Terms are included, so there is no rendered-window divergence. No live corpus lookup or corpus freshness check was made by this evaluator: the rate is a committed-pack estimate, not a current remote-corpus measurement. A good score on this single denial does not establish general calibration. The motion-related distribution concern is preserved in flags rather than used to change the frozen band.

## Reasoning quality: 0.55

The rationale identifies relevant procedural features: a response waiver, an earlier distribution concerning the veteran-status motion, and a fact-specific installation-debarment dispute. It reasonably separates an eventual grant from the intermediate possibility of a requested response and gives a clear low-probability disposition forecast.

Its analysis of the asserted APA conflict and vehicle is largely conclusory. It labels the case an exceedingly poor vehicle without analyzing the allegedly inconsistent appellate rules, the record additions, or preservation issues. It supplies no measured conditional rate or explicit calculation to justify moving from roughly 16–17% to 0.5%. Most importantly, it speculates that the elevated band arises because the federal government is the respondent. The committed band description distinguishes petitioner classes from trajectory bands; a federal respondent is not a federal petitioner, and the record instead contains a two-distribution signal. That unsupported account undermines its understanding of the conditioning baseline even though the JSON retains the correct frozen band.

The correct denial forecast therefore earns full label credit and the mechanically calculated Brier, but not a high analytical score. The unexplained denial does not establish that the Court accepted any of the candidate's proposed reasons. The reasoning score concerns the content and support of `reasoning.md`, not its brevity, the tool capture rate, or the forecast document. The claim probabilities themselves are not graded here.

## Leakage and retrieval limitations

The harness log says forward and timestamps all calls September 18, before the October 5 resolution. Every one of its 26 result markers is `unobserved`; this is a visibility limit, not a failed-call finding. In particular, it records `fedcourts query --court scotus --era 2020s`, while the retrieval note says no retrieval beyond provisioned inputs. The record establishes an attempted query but not whether it succeeded, which rows it returned, or any transfer amount. The discrepancy is flagged informationally; neither success nor failure is inferred.

The visible queries do not seek this petition's disposition, and the reasoning presents the petition as awaiting the September 28 conference. There is no affirmative evidence that a decided case was provisioned forward. Because the broad query's result is wholly unobserved, `retrieved_outcome_material` is null rather than a verified false. On the demonstrated predecision forward timing, influence is `not_applicable` and `leakage_suspected` is false. Missing capture alone is not a basis for leakage exclusion.

I read the pointed-to forecast but do not grade it. No semantic grades or vote accuracy are written for this cert event. The harness owns claim scores and provenance stamps. No optional significance assessment is supplied.
