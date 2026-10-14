# claude-baseline — evaluation

## Cell

Cert stage (`event.yaml` `stage: cert`). Outcome: `actual_disposition` **granted**, `actual_granted` 1, `disposition_route` plenary, resolved 2026-10-13 after two distributions, no CVSG. The prediction froze a band (`baseline`, sal-v4, Term 2025), so the segment base rate, `base_rate_basis` and `brier_skill_score` are the harness's stamp and left null here; read the comparison against "the stamped segment base rate". `correct` is the exact-label match on the disposition axis: `gvr` and `summary-reversal` both count as grants on the binary axis but are distinct labels from `granted`, so a summary-disposition call scores 0 against a plenary grant. Claims and the forecast document are scored in code and are not graded here. Cert cell: no vote accuracy, no semantic grades.

## Score

- Predicted `gvr`, P(grant) 0.60 → `correct` 0 (label), Brier (0.60 − 1)² = **0.16**.
- Right side of 0.5 on the binary axis, the most conservative of the three. Within its grant mass it put 0.27 on a plenary grant versus 0.33 summary disposition — the most weight on the actual route of any candidate — but chose `gvr` as the label.

## Reasoning quality — 0.72

The most balanced analysis of the three. It read the full record, identified the federal-petitioner mismatch with the frozen band and quantified both anchors, and gave the right weight to the June 2025 order (stay pending a future petition as a Hollingsworth-style signal of a reasonable probability of a grant) and to the thinness of the D.C. Circuit's remand order. Its "why not higher" section engages the respondents' strongest points concretely (withdrawal of exactly the category the order flagged, en banc denial without a vote request, staleness, forfeiture, vehicle). It also explicitly recognised that QP 2 is "a real statutory question the Court might prefer to decide with argument" — the reasoning that turned out to govern — though it still ranked a summary disposition first.

Deductions: it shaded downward on general knowledge outside the provisioned record (DOGE's reported wind-down), which it disclosed clearly and held loosely; and its discount of the probability, in particular its weight on denial (0.40), proved too heavy given the Court's demonstrated interest. A well-calibrated read, slightly under-confident.

## Leakage

Forward cell, prediction 2026-09-16, outcome 2026-10-13, log fully captured. CourtListener lookup of this docket returned its pre-decision state (date_modified 2026-07-08, not terminated); district-court RECAP queries returned nothing after December 2025; corpus citation queries returned no rows. No post-resolution document date, nothing aimed at the disposition, no `data/qp-topics/` read. `not_applicable`, not suspected.

## Big case

My own read: 0.74 (see evaluation.json).
