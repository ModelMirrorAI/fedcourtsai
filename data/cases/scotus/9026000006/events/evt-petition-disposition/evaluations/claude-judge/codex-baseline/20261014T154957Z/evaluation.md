# Evaluation — codex-baseline

**Cell.** scotus/9026000006 (Merritt v. Texas Farm Bureau), `evt-petition-disposition`, stage `cert`. Outcome: `denied` on 2026-10-13, after a single distribution for the October 9, 2026 conference, with no noted dissent (`actual_granted` 0).

**Base rate.** The scored prediction froze a band (`baseline`, `sal-v4`), so the segment base rate, its basis and the Brier skill score are the harness's risk-set anchor, filled in by `stamp-cell`. I leave them null here and quote no rate of my own. Compare against the stamped segment base rate.

**Leakage.** Forward cell: the prediction is dated 2026-10-04, before the conference and the denial. I checked the log for this case's own disposition showing up as already decided and found none (details below).

**Score.** Predicted `denied`, P(grant) = 0.02. Correct (1). Brier = 0.02² = 0.0004.

**Reasoning quality: 0.85.** This is a careful, well-sourced rationale. It does these things well:

- It pools the baseline reached rate from the displayed pre-2026 Terms (~5.0%) and shows its work.
- It correctly declines to multiply the terminal relist and CVSG cuts into the prospective rate.
- It treats the QP fairly as an intelligible statutory distinction, the strongest reason the grant chance is not zero.
- It identifies the missing circuit conflict as the main downward driver.
- It weighs the vehicle problems with citations to the record: Fifth Circuit footnote 2 leaving waiver unreached, the jury verdict, the deferential review, and the unresolved cross-appeal issues.
- It treats the BIO's survey of the circuits as an adversary's argument, not as verified fact.

Its one weak spot is that it stays a little above what the record warranted. It gives some weight to the petitioner's "recurring question" framing even though no circuit disagreement was shown, so 2% is mildly generous. That is a defensible calibration choice, not an error.

**Leakage.** There were two generic web lookups on Supreme Court Rule 10 and the Court's rules PDF. Both are `unobserved`. Graded on their queries, neither is case-specific, and the candidate says both returned nothing usable. One shell call ran `find data -name AGENTS.md -not -path 'data/qp-topics/*'`. That is a path-exclusion filter, which the contract classes as not a read. Grade: `not_applicable`, not suspected.
