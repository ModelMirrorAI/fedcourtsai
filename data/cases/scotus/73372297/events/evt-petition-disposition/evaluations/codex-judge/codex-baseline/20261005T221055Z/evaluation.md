# Evaluation: codex-baseline

## Outcome and numerical scores

The authoritative cert-stage outcome is `denied` on October 5, 2026, with `actual_granted = 0`. codex-baseline's September 16 prediction also names `denied`, with any-grant probability 0.004. Thus `correct = 1` and Brier loss is `(0.004 - 0)^2 = 0.000016`.

The prediction freezes Term 2025, band `baseline`, and version `sal-v4`. The statpack heading matches the frozen version, so `base_rate_basis = risk_set`. Use the bracketed reached rates in the rendered prior-Term rows: 2024: 5.7%, n=1,271; 2023: 5.9%, n=1,312; 2022: 5.8%, n=1,192; 2021: 5.6%, n=1,500; 2020: 4.5%, n=1,739; 2019: 4.6%, n=1,399; 2018: 4.6%, n=1,524; 2017: 4.7%, n=1,643. Their weighted mean is 592.925 / 11,580 = 0.05120250431778929; the weighted numerator is based on rounded percentages, not a literal grant count. Skill is `1 - 0.000016 / 0.05120250431778929^2 = 0.9938970814070851`.

codex-baseline's 593 / 11,580 = approximately 0.051208981 uses the companion statpack JSON's unrounded fields for those same Terms, as its retrieval log states and the committed JSON confirms. That is a precision difference, not an incorrect band, version, or time window. This evaluation uses the prompt's displayed Markdown rates consistently for all candidates. The caption renders 10 of 10 Terms, with 2025 and 2026 excluded from the pool, so there is no hidden-window discrepancy.

The pool describes the committed denial-reweighted live/historical slice. No fresh corpus query was made, and the inspected pack supplies no corpus-wide newest-pull timestamp or per-case last-pulled stamp. The provisioned evaluation snapshot is October 5, 2026; it does not attest the freshness of the remote corpus. Neither a correct denial nor this single positive skill score establishes population-level performance.

## Reasoning quality: 0.93

The rationale carefully distinguishes documented posture from the petitioner's allegations. It identifies the individualized damages and records-access disputes, the petition's own account of the review-deadline obstacle, the absent appendix, and the lack of a developed conflict. Its discussion of the missing lower-court materials does not turn an alleged deadline problem into a conclusively established jurisdictional bar. The petition's “The Appeal” and “Reasons for Granting” sections support that account.

The analysis also explains why the government's waiver is not agreement with the petitioner, why a summer wait after one distribution is not evidence of relisting, and why broader criticism of the compensation program does not establish government support for this case. The generic Rule 10 discussion is tied to a recorded official-rules retrieval rather than an unsupported assertion about this petition's merits. Quantitatively, the rationale uses the correct frozen-band risk set and prior-Term window, avoids multiplying overlapping descriptive slices, and identifies the move to 0.4% as judgmental rather than empirically fitted. It retains uncertainty about material not supplied.

The remaining limitation is the magnitude of that adjustment: the record supports a low probability more directly than it establishes 0.4% in particular. No comparable-case calibration or sensitivity range demonstrates that exact value. This modest deduction is independent of whether the final label happened to be right. The unexplained denial is compatible with the analysis, but does not reveal the Court's actual reasons or prove the underlying allegations false.

The score grades the headline-probability reasoning in `reasoning.md` only. The forecast document, structured procedural claims, significance score, and any implied vote predictions receive no reward or penalty in it. No inference about authorship is used.

## Leakage and scoring boundaries

The log identifies a forward prediction made September 16, before the October 5 resolution. Of 32 calls, 27 have captured results and five are unobserved. The external query strings and URLs concern generic Court rules; they do not name this case or request its disposition. The subsequent official-rules download has captured status. Local calls concern the provisioned snapshot, petition, aggregate statpack, schemas, and output production. A find command excludes the forbidden labeling subtree; it does not read labeling artifacts and is not outcome retrieval merely because the excluded path appears in its text.

The candidate reports no outcome knowledge, and its reasoning describes the conference as still future. The log and prose contain no evidence of this petition's disposition surfacing before prediction. Outcome material is therefore assessed false, influence `not_applicable`, and suspected leakage false. Unobserved web results are assessed from their generic queries, not assumed empty because the candidate saw no visible response. Collapsed `other` tool classes are assessed by their query content and carry no adverse inference.

No cert votes or semantic propositions are graded. Mechanical claim scoring remains with the harness. No independent big-case assessment is supplied because the candidate's significance judgment was encountered before an independent read was fixed.
