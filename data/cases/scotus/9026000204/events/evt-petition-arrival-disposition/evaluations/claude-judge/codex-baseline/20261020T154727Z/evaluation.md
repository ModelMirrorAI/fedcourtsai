# codex-baseline — evaluation

**Score.** P(grant) 0.95, predicted `granted`. That is correct. Brier = (0.95−1)² = 0.0025.

**Cell.** Cert stage, `arrival` moment, forward mode. Outcome: `granted` (plenary route), resolved 2026-10-19 after two distributions. The prediction froze `band: federal` (`sal-v3`), so the segment base rate, the Brier skill score and the basis are stamped by the harness from the risk-set anchor. I left them null and quote no rate of my own here; see "the stamped segment base rate". `correct` and `brier_score` are written as my independent read. The harness recomputes and stamps both.

**Votes / semantic.** This is a cert cell, so votes are not scored and no `semantic_grades` block applies.

**Leakage.** The cell is forward: docketed 2026-08-18, predicted 2026-08-20, two months before the grant. I checked the captured log for this case's own disposition surfacing as already decided and found none. Graded `not_applicable`, with `retrieved_outcome_material: false`.

**Big case (my read, 0.6).** The SG is defending a 160-year-old tax-administration statute that the Fifth Circuit invalidated on Necessary and Proper grounds, against a square Sixth Circuit conflict. The Court granted plenary review. The doctrine matters, but the statute is narrow.

**Reasoning quality: 0.85.** The anchor is explicit and pooled correctly: the sal-v3 federal band over the strictly-prior Terms OT2017–OT2025, 143/201 ≈ 71%. It declines the terminal relist cut because that cut conditions on a future trajectory, which is the right instinct for an arrival moment. The upward adjustment rests on the right factors: the SG is the petitioner, a federal statute was invalidated below, there is a square CA5/CA6 conflict, and the vehicle advantages (standing undisputed, associational standing, no extra Commerce Clause question) are drawn from the petition. The 5% tail is tied to concrete risks: the BIO is unseen, the case could become moot, and the Court could prefer the companion vehicle. It also discloses that the petition was provisioned truncated. Minor deduction: 0.95 is aggressive for a docketing-time forecast before any response, though it is well defended.

**Retrieval.** Two CourtListener opinion searches, both bounded to filed before 2026-08-20. Their results were unobserved in the log. The candidate's own retrieval.md says they surfaced the April 2026 lower-court opinions. Legitimate forward context.
