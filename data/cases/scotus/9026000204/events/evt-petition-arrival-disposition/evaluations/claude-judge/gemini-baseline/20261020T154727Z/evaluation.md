# gemini-baseline — evaluation

**Score.** P(grant) 0.95, predicted `granted`. That is correct. Brier = 0.0025.

**Cell.** Cert stage, `arrival` moment, forward mode. Outcome: `granted` (plenary route), resolved 2026-10-19 after two distributions. The prediction froze `band: federal` (`sal-v3`), so the segment base rate, the Brier skill score and the basis are stamped by the harness from the risk-set anchor. I left them null and quote no rate of my own here; see "the stamped segment base rate". `correct` and `brier_score` are written as my independent read. The harness recomputes and stamps both.

**Votes / semantic.** This is a cert cell, so votes are not scored and no `semantic_grades` block applies.

**Leakage.** The cell is forward: docketed 2026-08-18, predicted 2026-08-20, two months before the grant. I checked the captured log for this case's own disposition surfacing as already decided and found none. Graded `not_applicable`, with `retrieved_outcome_material: false`.

**Big case (my read, 0.6).** The SG is defending a 160-year-old tax-administration statute that the Fifth Circuit invalidated on Necessary and Proper grounds, against a square Sixth Circuit conflict. The Court granted plenary review. The doctrine matters, but the statute is narrow.

**Reasoning quality: 0.6.** The direction and factors are right: the SG is the petitioner, the Fifth Circuit struck down a federal statute, the CA6 split is direct, and no CVSG is possible. The anchor is cited only as "approximately 71%", with no Terms or counts shown. The jump from 71% to 95% rests on an assertion ("granted almost universally") rather than an argued adjustment. There is no engagement with vehicle specifics, the companion *Ream* petition, mootness, or the unseen BIO beyond one generic sentence. One internal inconsistency: retrieval.md says `fedcourts query` was "not successfully invoked", yet the captured log shows a query call. Its result was not captured, so this is a candor/precision nit rather than a leakage signal. The result is sound but thinly argued.

**Retrieval.** One CourtListener search ("Scott McNutt"), result unobserved. It is graded on its query: a forward check that the case was undecided. That is legitimate in a forward cell, and the case was in fact open.
