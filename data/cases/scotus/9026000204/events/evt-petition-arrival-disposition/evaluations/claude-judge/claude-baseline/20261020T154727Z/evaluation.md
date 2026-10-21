# claude-baseline — evaluation

**Score.** P(grant) 0.90, predicted `granted`. That is correct. Brier = (0.90−1)² = 0.01.

**Cell.** Cert stage, `arrival` moment, forward mode. Outcome: `granted` (plenary route), resolved 2026-10-19 after two distributions. The prediction froze `band: federal` (`sal-v3`), so the segment base rate, the Brier skill score and the basis are stamped by the harness from the risk-set anchor. I left them null and quote no rate of my own here; see "the stamped segment base rate". `correct` and `brier_score` are written as my independent read. The harness recomputes and stamps both.

**Votes / semantic.** This is a cert cell, so votes are not scored and no `semantic_grades` block applies.

**Leakage.** The cell is forward: docketed 2026-08-18, predicted 2026-08-20, two months before the grant. I checked the captured log for this case's own disposition surfacing as already decided and found none. Graded `not_applicable`, with `retrieved_outcome_material: false`.

**Big case (my read, 0.6).** The SG is defending a 160-year-old tax-administration statute that the Fifth Circuit invalidated on Necessary and Proper grounds, against a square Sixth Circuit conflict. The Court granted plenary review. The doctrine matters, but the statute is narrow.

**Reasoning quality: 0.85.** This is the most transparent anchor: the federal-band counts are pooled term by term over OT2017–OT2025 (n = 201, ≈143 grants ≈ 71%) and cross-checked against the pooled salience cut. The adjustments are enumerated and well grounded: the "usual" practice of granting when a federal statute is invalidated, with the petition's recent examples; a square, acknowledged split; and a clean vehicle. The downward holds are specific, and most of them are real risks: the unseen BIO, legislative mooting, and the vehicle choice between this case and *Ream*. It correctly notes that a hold-then-GVR stays in the grant family. Its limits are candidly disclosed: the petition was truncated, the CA5 opinion was read only through the SG, and the companion-docket lookups failed. Leaving 10% on denial was more conservative than the posture warranted, and that cost it slightly on Brier. The analysis itself is the most complete of the three.

**Retrieval.** `fedcourts query` calls for generic granted priors and two CourtListener docket searches for the companion *Ream* petition (0 results). All of these are legitimate forward context. One shell call piped `git status --porcelain` through `grep -v '^ D data/qp-topics'`. That lists path status from git's index and opens no file under `data/qp-topics/`, so it is not a qp-topics read.
