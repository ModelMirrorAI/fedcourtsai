# gemini-baseline — P(grant) 0.05, predicted `denied`

**Cell.** Cert stage (`stage: cert`, distribution moment). Outcome: `denied` on 2026-10-19 (`actual_granted` 0), standard basis, three distributions, no CVSG, no noted dissent from denial. The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, `base_rate_basis` and skill are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` below are my elicited reads for the stamp to compare against.

**Leakage.** Forward cell (log mode `forward`), predicted in September 2026 while the petition was pending; no retrieval reached this petition's disposition and no call touched `data/qp-topics/`. Graded `not_applicable`, `leakage_suspected` false.

**Semantic grades.** Not a merits cell; no semantic set is declared, so no block is written.

**Score.** Correct (denied = denied). Brier = 0.05² = 0.0025.

**Reasoning quality: 0.55.** The core call is right and the stated reason — the Court's reluctance to take interlocutory review in criminal and commission proceedings, with the issue preserved for a post-judgment appeal — is a legitimate and probably weighty denial driver. The SG's opposition and the impossibility of a CVSG are correctly noted. But the analysis is a single paragraph: it never engages the petition's actual questions (mandamus jurisdiction absent a statutory government appeal, *Will v. United States*, the claimed circuit disagreement), the D.C. Circuit dissent, the three cert-stage amici, or the companion bin 'Atash petition. The anchor description ("baseline floor for the private caption class") is loose but lands on the right ~5% figure. The suggestion of a possible dissent from denial did not materialise, though that is a probability judgment rather than an error. Right answer, thin support.
