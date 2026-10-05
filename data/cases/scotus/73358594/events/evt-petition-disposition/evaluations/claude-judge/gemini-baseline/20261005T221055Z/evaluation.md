# Evaluation of gemini-baseline — scotus/73358594, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition
(No. 25-1289, Bolanos-Reynoso v. Department of Agriculture, Federal Circuit)
was **denied** on 2026-10-05 after its first conference of 2026-09-28, with no
noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`,
`distribution_count: 1`, `noted_dissent_from_denial: false`).

- `predicted_disposition: denied` → `correct = 1`.
- `probability = 0.01` → `brier_score = (0.01 − 0)² = 0.0001`.
- `segment_base_rate = 0.051203`, basis `risk_set`: the prediction's frozen
  context carries `band: baseline` and `salience_version: sal-v4`, matching
  the statpack table's heading. Pooled bracketed `reached` baseline rate,
  resolved-weighted, over OT2017–OT2024 (every rendered Term strictly before
  Term 2025): ≈592.9 grants over n = 11,580 → 5.12%. The table renders 10 of
  10 Terms, so the rendered window is the whole pack; no divergence to flag.
- `brier_skill_score = 1 − 0.0001 / 0.051203² = 0.962`.
- No `vote_accuracy` (cert cell); no `semantic_grades` (no semantic set on a
  cert event; `semantic_claims` is null); `claim_scores` left to the harness.

## Reasoning quality: 0.55

The number is as good as the best candidate's and the core signal is right,
but the document earns the number with far less analysis than its
competitors and than the record supports.

What is sound:

- **Anchor.** "~5.1% for cases that reach this band (pooled OT2017–OT2024)" is
  the correct band, the correct reached figure, and the correct window.
- **Primary signal.** The SG's waiver on behalf of the federal respondent,
  read as signalling no split, poor vehicle, or fact-bound error correction,
  with the correct observation that the Court rarely grants without a
  response and usually does not call for one on a routine WPA petition from
  the Federal Circuit. That is the single most informative fact on this docket
  and the candidate identified it.
- **Structural points.** CVSG categorically inapplicable because the SG
  already represents the respondent; a first-conference denial without relist
  as the modal path for a waived petition.

What is missing or weak:

- **No engagement with the decision below or the petition's argument.** The
  record shows a one-line Federal Circuit Rule 36 affirmance (Appendix A) and
  a petition that alleges no circuit conflict and cites *Flynn v. SEC* only as
  an analogous remand. Neither the Rule 36 posture nor the absence of a split
  is mentioned, though both are first-order Rule 10 considerations and both
  were in the provisioned documents. The document would read the same for
  almost any SG-waiver petition; the adjustment is asserted from the waiver
  alone rather than built from the case.
- **It adopts the petitioner's framing as fact.** The dissent paragraph
  refers to "the MSPB and Federal Circuit's failure to consider the second
  statutory category" — the petition's contested premise, which the candidate
  did not test against the Board decision (App. 3a–119a) or the Rule 36
  judgment. The better documents flagged this as advocacy.
- **No calibration reasoning.** Why 1% rather than 2% or 0.5% — what the
  reached population contains, what residual a GVR or late call-for-response
  carries — is not addressed.
- **Thin retrieval, candidly reported.** Two CourtListener searches returning
  nothing and an aborted free-text corpus query; the retrieval note is honest
  about this, which is to its credit, but nothing retrieved informed the
  analysis.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`;
`influenced_prediction: not_applicable`; `leakage_suspected: false`. Created
2026-09-16 against a 2026-09-16 snapshot ending at the June 17 distribution;
denial 2026-10-05. The log (24 calls) has capture coverage 0.0, which is this
engine's standing shape rather than a defect, so every call is graded on its
query: record and statpack reads, two `fedcourts query` attempts, and two
CourtListener searches — one on MSPB / WPA terms, one on petitioner's
counsel's name. A counsel-name search could in principle surface this docket,
but on 2026-09-16 the petition was undecided, so nothing outcome-revealing
existed to retrieve; the candidate reports 0 results, which the unobserved
marker cannot confirm or deny. No `data/qp-topics/` read. Not a
mis-provisioned decided case.

## Big case

My independent read is 0.10 (see `big_case.notes`). The candidate's 0.10 and
its one-line rationale (routine whistleblower dispute over MSPB procedures, no
broad national impact) match the stakes as they resolved.
