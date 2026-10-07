# Evaluation: gemini-baseline — Veto v. The Boeing Company, No. 25-1270 (evt-petition-disposition)

## Outcome and scoring

Cert-stage cell. The petition was **denied** on October 5, 2026 after a single
distribution (conference of September 28, 2026), with no noted dissent.
`actual_granted` = 0.

- `predicted_disposition` `denied` matches → **correct = 1**.
- `probability` 0.001 → **brier_score = 1e-06**.
- **segment_base_rate = 0.0512**, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`; the statpack band
  table's heading is sal-v4, so the bracketed `reached` figure applies.
  Pooled resolved-weighted over the rendered Terms strictly before Term 2025
  (OT2017 through OT2024; the caption renders 10 of 10 Terms, so the rendered
  window and the configured lookback coincide): 592.9 / 11,580 = 5.12%.
- **brier_skill_score = 0.9996**.
- No votes scored (cert stage); no `semantic_grades` (none declared on a cert
  event).

## Reasoning quality: 0.60

The direction and the main reason are right: the candidate names the
prior-Term band anchor at about 5%, identifies the petition as pro se with
nine incoherent questions spanning drug use, patents, the Export-Import Bank,
and whistleblower retaliation, and correctly notes there is no circuit split
and no vehicle. It also correctly reads the relist-0 bucket's 1.2% as a
figure that overstates this petition's chances rather than treating it as the
anchor.

But the document is a single paragraph and the analysis stops at the label
"incoherent." It does not say what the court below actually decided (a
summary-judgment affirmance on California Labor Code retaliation claims in an
unpublished memorandum), does not mention that no response or waiver was on
the docket, and does not explain why a 0.1% figure, fifty-fold below the band
anchor, is the right magnitude rather than 0.3% or 1%; "virtually no chance"
is a conclusion, not a calibration. The claims block is left unexplained in
the rationale beyond a sentence on administrative relists. The outcome was
consistent with the forecast, and nothing here was wrong, but little of it
could be checked against anything, which is what this score measures.

## Leakage: forward, not applicable

`mode` is `forward` and the case was open when predicted (prediction
2026-09-16; denial 2026-10-05). The log holds 23 calls, all file-read,
file-search, file-write, or shell against the provisioned record, the
prompt, the schemas, and the committed statpack; no web, corpus, or
CourtListener call. Every row is `unobserved` (`result_capture_coverage`
0.0, the engine's standing shape), so each is graded on its query, and no
query names anything outside the checkout. No read of `data/qp-topics/`. The
reasoning presupposes nothing about the disposition.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false.

## Big case (my independent read): 0.02

Formed before reading the candidate's own score. A pro se individual
retaliation suit with incoherent questions presented and an unpublished
affirmance below; the respondent's name adds nothing doctrinal.
