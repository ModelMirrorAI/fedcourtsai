# Evaluation: claude-baseline

## Outcome and scores

This is a cert-stage evaluation. The outcome records denied on October 5, 2026 and actual_granted = 0. The candidate predicted denied, so correct = 1. Its probability 0.004 gives Brier = 0.000016. The numerical result does not establish the correctness of every proposed reason for denial.

## Baseline

The prediction freezes baseline under sal-v4 in docket Term 2025. The matching committed metrics/statpack.md table supplies the risk-set bracketed reached figures. Pool all shown Terms strictly before 2025: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643. Neither the same-Term row nor 2026 enters the pool.

The executed calculation is 592.925 / 11580 = 0.05120250431778929. Both numerator and rate are approximate reconstructions from printed rounded percentages and denial-reweighted denominators, not exact observed counts. The caption says 10 of 10 Terms are rendered; no truncated-table window discrepancy arises. Thus base_rate_basis = risk_set and skill = 1 - 0.000016 / baseline^2 = 0.9938970814070851. These figures describe the committed pack, not freshly queried remote state.

## Reasoning quality: 0.83

The rationale provides a transparent prior and detailed case-specific reasons for a substantial downward adjustment. It focuses on the actual notice theory, the petition's concessions about retroactivity and a reasonable transition period, and the distinction between an asserted conflict about Ohio law and a developed conflict about the federal question. Its reported lower-opinion retrieval gives the preservation concern a stated evidentiary basis, and its concluding caveat fairly admits that the state supreme court jurisdictional memorandum was not retrieved.

The principal weakness is overconfidence relative to that evidence. Silence in the lower opinion does not, on this supplied record alone, establish that the federal claim was unpreserved, yet the rationale treats this as the single largest discount. Its assertion that serial pro se litigants grant at rates well below the paid population has no displayed comparative estimate; unrelated litigation and discipline are not substitutes for a case-specific vehicle analysis. The 0.4% endpoint remains a subjective adjustment, not an empirically fitted estimate. Those limitations reduce the grade despite the correct outcome.

Only reasoning.md is qualitatively graded. The forecast and quantitative claims were read but are not independently scored, and the denial is not treated as a merits endorsement of the candidate's doctrinal account.

## Integrity and scope

The harness log records forward mode, 23 captured calls, and September 17 timestamps. Target-case retrieval includes the older Ohio opinion, the SCOTUS docket row and docket-entry query; the candidate describes an unterminated docket and no returned entries. The latest extracted document date is September 17, still before the October 5 resolution. No query, dated result metadata or prose shows this petition's disposing order. Searching the open case itself is permissible in forward mode; older denials involving the same litigant are not this event's outcome. Leakage is assessed as no retrieved outcome material and not_applicable influence, with leakage_suspected = false.

Vote accuracy and semantic grading are inapplicable to cert. Claim scores and provenance stamps remain harness-owned. The optional big-case assessment is omitted because an independent read was not formed before seeing the candidate's score. No flag-worthy anomaly was identified.
