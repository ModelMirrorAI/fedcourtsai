# Evaluation — claude-baseline
## Cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`). Outcome: petition **granted**, plenary route, resolved 2026-10-13 after two distributions (9/28/2026 long conference, relisted for 10/9/2026). `actual_granted` = 1. All three candidates are forward predictions made 2026-10-03 on a one-distribution snapshot, each with a frozen `context.band` of `federal` (sal-v4), so the segment base rate, its basis and the Brier skill score are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are my elicited values for the stamp to compare. No votes scored (cert stage); no semantic set declared (cert stage), so no `semantic_grades`. Claims are scored in code, not here.

## Score

P(grant) 0.38, predicted `denied` → `correct` 0, Brier (0.38−1)² = 0.3844.

## Reasoning quality: 0.60

The most thorough legal analysis of the three: it read the full Fourth Circuit opinion, identified the panel and dissent, the conflict with `Matter of A-C-M-`, the Second/Third vs. Sixth Circuit alignment, the Loper Bright angle, and real vehicle concerns (respondent removed to Nigeria, "on this record" framing, alternative remand grounds). It anchored correctly on the strictly-prior federal reached rate (~73%) and stated it would have sat at 0.72–0.75 on the merits of the petition.

The miss comes from one inference it then weighted decisively: that absence from the post-long-conference grant tranche (inferred from a neighbouring docket granted 10/1 and this docket showing no entry on 10/3) "removes the single largest grant path." The signal was legitimate forward information and the candidate disclosed it openly, but the realized path — relist to the next conference, then grant — is the ordinary route for a contested SG petition, and the candidate's own path model assigned P(grant | relist) ≈ 0.6 with P(relist) 0.55. Moving from ~0.73 to 0.38 on an unvalidated assumption that "about two thirds" of eventual federal grants come in the first tranche was an over-adjustment; the "where to discount me" section names the risk but underweights it. Good process, transparent, but the decisive step was poorly calibrated.

## Leakage

Forward; `not_applicable`. Fetching this case's own live docket on 2026-10-03 is allowed for an open case, and it showed nothing beyond the 8/19 distribution; the relist and the 10/13 grant postdate it. No outcome material.
