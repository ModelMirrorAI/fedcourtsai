# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage cell. The outcome records a plenary grant on November 6, 2026, confirmed by the staged docket. codex-baseline predicted denial with P(any grant) = 0.38, giving **correct = 0** and **Brier = 0.3844**, from (0.38 - 1)^2. Cert votes are not scored, no semantic set is graded, and the harness computes the structured quantitative claims.

The scored prediction's frozen context is `elevated`, `sal-v4`, Term 2025, with two distributions. It is not replaced by the evaluator's later `high`, `sal-v8`, four-distribution context. The harness owns the baseline, its basis, and skill; this evaluation supplies no competing numerical anchor.

## Reasoning quality: 0.90

This is a well-supported analysis of why a serious petition could nevertheless be denied. It gives specific upward weight to the focused Hill conflict, the reasoned dissent, the FAA framework, and industry interest, while distinguishing the existence of an amicus from knowledge of its contents. It fairly presents Brown's ongoing Chapter 13 case, Maze's discharged Chapter 7 posture, the Section 105(a) overlap, and the disputed concession and preservation issues. It does not turn respondents' characterizations into findings.

The September dismissal is handled particularly well: the rationale recognizes leave to amend, credits the argument that arbitration could remain a live controversy, and does not assert established mootness. Its modestly denial-favoring balance proved wrong, but the grant alone does not falsify those legal concerns or reveal which consideration persuaded the Court. The unresolved pleading is a possible obstacle, not a doctrinal rule that the Court must refuse review; the candidate mostly preserves that distinction.

Its empirical anchoring is transparent and avoids treating terminal relist buckets as next-step hazards or adding the same relist signal twice. The historical statistics were checked against candidate-era statpack build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, recovered separately for this alias by `statpack-at`. The listed prior-Term risk-set inputs agree with that build. This checks the candidate's reasoning, not the current harness's eventual baseline.

The remaining weakness is the necessarily judgmental size of the vehicle discount relative to a documented conflict and dissent. The rationale offers no validated mapping from those features to its final probability, and active relist interest proved more persistent than its modal expectation. Those are limitations of the analysis, not a reason to equate the wrong binary call with poor legal reasoning. This score excludes the forecast document and structured claims.

## Predicted reasoning

**Grade: 0.25.** The leading commitment was denial, with the pleading and conflict objections furnishing the proposed explanation. That central disposition failed. The modal no-further-distribution forecast also failed: the docket adds October 13 and November 2 distributions before the November 6 grant. Its stated October-or-November resolution window was nevertheless correct, and its minority branch explicitly allowed further distributions.

No CVSG and a plenary rather than summary route were borne out. They provide partial procedural credit, but do not outweigh the principal failed call. The forecasted FAA merits ground and precise carve-out for standalone Section 105(a) proceedings remain unresolved: cert was granted, not decided on the merits. The conditional denial-writing forecast was never tested and is not a miss. The grade concerns the forecast prose only, without rescoring its numerical claims.

## Leakage and stakes

The log reports forward mode. Its 32 calls include 31 captured results and one unobserved hosted call whose query is the September 14 supplemental PDF. I do not infer that this unobserved call returned nothing. Its target, the captured follow-up retrievals, and the reasoning instead identify pre-decision filings about a lower-court pleading dismissal. Prediction activity on October 6 preceded the Supreme Court's November 6 disposition; no logged query or prose presents that disposition as already known. The appropriate assessment is `not_applicable`, with `leakage_suspected: false`.

My stakes read is **0.50**, independently based on nationwide implications for consumer-bankruptcy enforcement and arbitration, tempered by the specialized forum question and the absence of a merits holding at this stage.
