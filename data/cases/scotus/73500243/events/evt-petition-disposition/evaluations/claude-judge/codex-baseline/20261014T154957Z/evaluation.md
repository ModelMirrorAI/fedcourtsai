# Evaluation: codex-baseline

**Cell:** scotus/73500243 (No. 25-1341, *Birks v. Aguirre-Jarquin*). Event `evt-petition-disposition`. Stage **cert**, mode **forward**. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), with no noted dissent and two distributions. The Court called for a response on July 31, and it never added a distribution beyond the two already on the docket when the predictions ran.

**Base rate:** the prediction froze `context.band` = `elevated` (sal-v4, Term 2025), so the harness stamps the segment base rate and skill from the risk-set anchor. I left `segment_base_rate`, `brier_skill_score` and `base_rate_basis` null, and any comparison here refers to "the stamped segment base rate". No votes are scored at the cert stage, `claim_scores` is the harness's, and no semantic set is declared for this cell, so I wrote no `semantic_grades`.

**Scores:** predicted `denied`, so `correct` = 1. P(grant) = 0.10, so Brier = 0.0100.

**Reasoning quality: 0.80.** This was a careful, well-sourced analysis. It recomputed the elevated band's reached anchor from the statpack's unrounded figures and kept the frozen conditioning rather than re-banding the case. It correctly discounts the repeated-consideration signal, since the second distribution followed the call for a response and not an actual conference. It identifies the same vehicle problems that the denial bears out, citing specific pages: the petition concedes its differing causation tests do not change the result, and the pendent-jurisdiction posture leaves materiality undecided below. It also read the pre-decision brief in opposition and fairly weighs its reframing as deliberate evasion of verification. It keeps a nontrivial chance of summary intervention, and it is candid about what it did not read (the reply, and the truncated petition appendix). It is slightly less complete than the strongest analysis because it skipped the reply. Some of the space it spends on the provenance of its sources adds little to the legal reasoning.

**Leakage:** forward, `not_applicable`. It fetched the pre-decision brief in opposition from the URL in its own snapshot. One web search was not captured; I graded it on its query (`site.supremecourt.gov "Zorn" "Lalli" 2026`), which does not ask about this petition's disposition. It made no reads under data/qp-topics and disclosed everything in retrieval.md.

**Big case:** my own read is 0.30.
