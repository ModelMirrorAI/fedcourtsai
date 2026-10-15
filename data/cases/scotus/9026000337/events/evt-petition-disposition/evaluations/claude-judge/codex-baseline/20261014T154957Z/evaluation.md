# Evaluation — codex-baseline

**P(grant) 0.015, predicted `denied` → correct = 1, Brier = 0.000225.**

## Cell

Cert-stage cell (`event.yaml` `stage: cert`), forward. Outcome: `denied`, `actual_granted` 0, resolved 2026-10-13 after one distribution, no CVSG, no noted dissent from denial. The prediction froze `context.band` `baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `vote_accuracy` omitted (cert stage). No `semantic_grades` (cert cells declare no semantic set). `claim_scores` is computed by the harness and not graded here.

## Big case (my own read): 0.12

One petitioner's coverage dispute under a 2003 Iowa group long-term-care policy. The Erie framing does not change that the question turns on Iowa insurance law and the policy text. It may matter to guaranteed-issue LTC insureds under NAIC-modeled regimes, but there is no split and no broad federal question. The Court denied it at the first conference, with the response waived and no dissent.

## Reasoning quality: 0.85

Careful and well-sourced. It pools the sal-v4 baseline `reached` rate from statpack.json (638/12,720 ≈ 5.0%, prior Terms only) and correctly declines to treat terminal relist/CVSG buckets as forward hazards. It identifies the core weaknesses: no square conflict (novelty and uniform model provisions are not a split), and a panel opinion that applies Iowa contract and statutory law rather than repudiating Erie, which makes it a contested application of state law. It notes record-dependent factual disputes and the late presentation of the certification request. It also checked McKesson v. Doe and correctly limited it, since that remand rested on a novel tort theory plus a First Amendment issue. It treats the waiver as modest rather than conclusive. Compared with the strongest analysis, it does not make the point that the panel's primary plain-terms ground leaves the attacked doctrine as supporting rationale. Its stakes score is somewhat generous. These are small gaps; the analysis is sound and consistent with the outcome.

## Leakage

Forward; `not_applicable`. Two web-search rows are `unobserved`, so I graded them on their queries: Supreme Court Rule 10 generally and the Court's Rules PDF. Neither concerns this petition. It also made a CourtListener read of McKesson v. Doe (2020). The candidate states it did not seek this petition's disposition, and the log agrees.
