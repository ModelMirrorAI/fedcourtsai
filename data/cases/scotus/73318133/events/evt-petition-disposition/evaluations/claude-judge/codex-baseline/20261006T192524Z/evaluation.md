# Evaluation: codex-baseline — Veto v. The Boeing Company, No. 25-1270 (evt-petition-disposition)

## Outcome and scoring

Cert-stage cell. The petition was **denied** on October 5, 2026 after a single
distribution (conference of September 28, 2026), with no noted dissent.
`actual_granted` = 0.

- `predicted_disposition` `denied` matches → **correct = 1**.
- `probability` 0.003 → **brier_score = 9e-06**.
- **segment_base_rate = 0.0512**, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`; the statpack band
  table's heading is sal-v4, so the bracketed `reached` figure applies.
  Pooled resolved-weighted over the rendered Terms strictly before Term 2025
  (OT2017 through OT2024; the caption renders 10 of 10 Terms, so the rendered
  window and the configured lookback coincide): 592.9 / 11,580 = 5.12%.
- **brier_skill_score = 0.9966**.
- No votes scored (cert stage); no `semantic_grades` (none declared on a cert
  event).

## Reasoning quality: 0.85

The anchor is right and is derived the same way I derived it, down to the
denominator; the candidate is careful to say it is a weighted mean of
displayed rounded rates rather than a recovered count, and it refuses the
terminal-baseline substitution. The central adverse consideration is well
chosen: the gap between the petition's sweeping questions and the narrow
evidentiary ruling actually under review, framed through Rule 10's
distinction between compelling grounds and factual-error correction. The
rationale keeps the petitioner's allegations as allegations, reads the relist
and CVSG cuts as terminal population shapes rather than transition
probabilities, and states the conditional structure of each claim correctly.
Its observation that pro se status is not itself a reason to deny is a fair
corrective to a common shortcut.

What held the score back. The write-up spends a good deal of its length on
provenance disclaimers (the pack's vintage, the manifest's fetch date, the
cache-path workaround) that do not bear on the forecast, and the actual
case-specific analysis is correspondingly thinner than it could be: it never
engages with the absence of a response or waiver as a signal about the
Court's path to a grant, which is the one docket mechanism that would have
had to fire first. The stakes paragraph assigns 0.18 to a case whose
adjudicative reach it correctly describes as an individual wrongful-
termination dispute; the paragraph's own logic supports a lower number, and
the gap between the reasoning and the figure is a soundness point against the
document, though a small one. The outcome was consistent with the forecast.

## Leakage: forward, not applicable

`mode` is `forward` and the case was open when predicted (prediction
2026-09-16; denial 2026-10-05). The external calls are three `web-search`
rows for Supreme Court Rule 10 material, all `unobserved`, so graded on their
queries, which name no case; and one captured shell `curl` of Rule 10 from
Cornell LII. None is about this docket. One shell call runs a `find` whose
`-not -path` clause names `data/qp-topics/` to exclude it; that is a path
exclusion in a search for a filename, not a read of the directory's
membership, and I do not grade it as a qp-topics read. No `retrieved_doc_date`
on or after the resolution, and the reasoning says in terms that it did not
retrieve the disposition. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case (my independent read): 0.02

Formed before reading the candidate's own score. A pro se individual
retaliation suit with incoherent questions presented and an unpublished
affirmance below; the respondent's name adds nothing doctrinal.
