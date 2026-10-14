# Evaluation — claude-baseline

**Cell.** Cert stage, forward mode. Johnson v. Montana, No. 25-1273 (Confrontation Clause: whether *Maryland v. Craig* or *Crawford* governs two-way video testimony by an adult prosecution witness). Outcome: `denied` on 2026-10-13 after two distributions, no CVSG, no noted dissent from denial. The prediction froze band `baseline` under `sal-v4`, so the segment base rate, `brier_skill_score` and `base_rate_basis` are stamped by the harness from the risk-set pool; I wrote none of them and compare against "the stamped segment base rate" only. `vote_accuracy` is omitted (cert cell). No `semantic_grades` (cert cell; no semantic set declared). Claims are scored in code and not graded here.

**Scores.** Predicted `denied`, P(grant) = 0.15 → `correct` = 1, Brier = 0.0225.

**Reasoning quality: 0.85.** The strongest analysis of the three. It anchored on the correct table (sal-v4 bracketed `reached` for `baseline`, pooled OT2017–OT2024 strictly before the case's Term, ≈5.1%), then made explicit, separately justified adjustments: up for the Court's call for a response (honestly flagged as held from general knowledge, with a stated sensitivity), counsel and the clean single QP; down for preservation (the theory-switch shown in the BIO's appendix), harmlessness (petitioner's own admission and arrest inside the house), unsympathetic facts, and the Court's prior denials (Wrotten, Weigand) on a lopsided split. Those down-weights are exactly the vehicle problems most consistent with the eventual denial. It fetched the BIO and reply from the snapshot's own docket URLs and disclosed that clearly. Deductions: the call-for-response uplift to 12–15% is somewhat generous for a paid petition with a weak vehicle, and it did not read the decision below itself (disclosed).

**Leakage.** Forward; `not_applicable`. All retrieval predates the resolution (BIO 2026-09-04, reply 2026-09-15, Montana opinion 2026-02-24); nothing about this petition's disposition surfaced.

**Big case (my read, 0.45).** A recurring and doctrinally live question, but this docket was a poor vehicle and drew no noted dissent.
