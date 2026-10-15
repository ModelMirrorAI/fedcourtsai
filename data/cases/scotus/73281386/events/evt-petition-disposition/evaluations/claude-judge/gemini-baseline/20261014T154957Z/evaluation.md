# gemini-baseline — evaluation

## Cell

Cert stage (`event.yaml` `stage: cert`). Outcome: `actual_disposition` **granted**, `actual_granted` 1, `disposition_route` plenary, resolved 2026-10-13 after two distributions, no CVSG. The prediction froze a band (`baseline`, sal-v4, Term 2025), so the segment base rate, `base_rate_basis` and `brier_skill_score` are the harness's stamp and left null here; read the comparison against "the stamped segment base rate". `correct` is the exact-label match on the disposition axis: `gvr` and `summary-reversal` both count as grants on the binary axis but are distinct labels from `granted`, so a summary-disposition call scores 0 against a plenary grant. Claims and the forecast document are scored in code and are not graded here. Cert cell: no vote accuracy, no semantic grades.

## Score

- Predicted `summary-reversal`, P(grant) 0.95 → `correct` 0 (label), Brier (0.95 − 1)² = **0.0025**.
- Best Brier of the three on the binary axis; wrong route label (the Court granted plenary review rather than reversing summarily).

## Reasoning quality — 0.38

The reasoning is short and identifies the two right drivers — a federal petitioner via the Solicitor General despite the frozen `baseline` band, and the Court's prior intervention in the same litigation. But it is thin for a 0.95 forecast: the log shows the candidate read only the first 100 lines of the petition and never opened the brief in opposition, so none of the respondents' compliance, forfeiture, staleness or vehicle arguments are engaged. No counter-case is weighed at all, and the leap from "the Court intervened once" to "summary reversal is extremely likely" is asserted rather than argued — it does not consider that a real statutory question (QP 2) might draw plenary review, which is what happened. The federal-band rate it cites is described loosely ("routinely exceeding 50–80%") rather than pooled. The outcome being a grant does not rescue the analysis: the number was right largely because of a correct but undeveloped intuition, and the specific predicted route was wrong.

## Leakage

Forward cell, prediction 2026-09-16, outcome 2026-10-13. Every log row is `unobserved` (coverage 0.0), so graded on queries: provisioned-file reads, the statpack, and `fedcourts query` calls bounded by decided-before dates for Cheney/FOIA analogs and generic granted rows. None targets this petition's outcome; no `data/qp-topics/` read. `not_applicable`, not suspected.

## Big case

My own read: 0.74 (see evaluation.json).
