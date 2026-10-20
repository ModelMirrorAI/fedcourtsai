# claude-baseline — P(grant) 0.14, predicted `denied`

**Cell.** Cert stage (`stage: cert`, distribution moment). Outcome: `denied` on 2026-10-19 (`actual_granted` 0), standard basis, three distributions, no CVSG, no noted dissent from denial. The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, `base_rate_basis` and skill are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` below are my elicited reads for the stamp to compare against.

**Leakage.** Forward cell (log mode `forward`), predicted in September 2026 while the petition was pending; no retrieval reached this petition's disposition and no call touched `data/qp-topics/`. Graded `not_applicable`, `leakage_suspected` false.

**Semantic grades.** Not a merits cell; no semantic set is declared, so no block is written.

**Score.** Correct (denied = denied). Brier = 0.14² = 0.0196.

**Reasoning quality: 0.80.** The strongest-structured analysis of the three. It anchors on the frozen band's risk-set rate (~5.0%), then lays out the upward features (D.C. Circuit origin, capital marking with a sensible discount, three amici, a full SG BIO, a dissent below, a companion petition, a real *Will* question) against the downward ones — the SG's credible no-split argument, the sui generis 10 U.S.C. 950g scheme as a poor vehicle for the civilian question, thin preservation below, interlocutory posture, and the Court's long run of denying commission petitions. The denial factors it identified are the ones consistent with the outcome. Weaknesses: the inferred Kavanaugh recusal rests on one "took no part" line on a sealing motion (the candidate flags this itself); the "result valence" paragraph speculates about Justices' preferences beyond the record; and on its own account the denial signals were strong enough that nearly tripling the anchor looks generous — though 0.14 is still a well-calibrated denial forecast. Honest, specific disclosure of what was and was not read.
