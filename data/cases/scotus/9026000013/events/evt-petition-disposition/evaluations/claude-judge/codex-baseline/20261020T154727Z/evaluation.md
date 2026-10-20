# codex-baseline — P(grant) 0.16, predicted `denied`

**Cell.** Cert stage (`stage: cert`, distribution moment). Outcome: `denied` on 2026-10-19 (`actual_granted` 0), standard basis, three distributions, no CVSG, no noted dissent from denial. The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, `base_rate_basis` and skill are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` below are my elicited reads for the stamp to compare against.

**Leakage.** Forward cell (log mode `forward`), predicted in September 2026 while the petition was pending; no retrieval reached this petition's disposition and no call touched `data/qp-topics/`. Graded `not_applicable`, `leakage_suspected` false.

**Semantic grades.** Not a merits cell; no semantic set is declared, so no block is written.

**Score.** Correct (denied = denied). Brier = 0.16² = 0.0256.

**Reasoning quality: 0.78.** Careful and well-sourced: it reconstructs the risk-set anchor exactly (638/12,720 ≈ 5.02%), keeps the descriptive cuts as background rather than multipliers, and checks *Will v. United States* directly, reading its reservation as cutting both ways — a sound reading. The denial factors (contested and imperfect split, vehicle problems from the commission statutes, question two as case-specific error correction, SG opposition with no escalation) are well reasoned and match the outcome. It also correctly declines to treat the sealing-motion nonparticipation as a case-wide recusal, and surfaces a capital-marking metadata discrepancy. Weaknesses: the upward adjustment to 0.16 is admittedly judgmental and leans on stakes the candidate itself says do not make four votes likely; it did not read the reply; and the prose is dense, with some stated figures cut off mid-sentence. A slightly higher probability than claude-baseline on comparable reasoning, both good.
