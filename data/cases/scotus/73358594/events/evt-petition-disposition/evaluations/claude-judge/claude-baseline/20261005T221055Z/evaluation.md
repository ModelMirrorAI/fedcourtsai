# Evaluation of claude-baseline — scotus/73358594, evt-petition-disposition

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
  10 Terms, so the rendered window is the whole pack and no earlier Term
  exists for the 10-Term lookback to reach; no divergence to flag.
- `brier_skill_score = 1 − 0.0001 / 0.051203² = 0.962`.
- No `vote_accuracy` (cert cell); no `semantic_grades` (no semantic set on a
  cert event; `semantic_claims` is null); `claim_scores` left to the harness.

## Reasoning quality: 0.88

The strongest of the three documents.

- **Anchor.** It reads the sal-v4 table correctly: bracketed reached rate for
  `baseline`, pooled over the eight strictly-prior Terms the table renders,
  weighted by risk-set n, "roughly 5.1% (about 593 grants over about 11,580
  petitions)" — exactly the figure I compute — and names it as the yardstick
  the cell is scored against. It quotes the paid-segment relist-0 and `cafc`
  cuts for orientation without substituting them.
- **Adjustments are specific, correctly ordered, and each tied to the
  record.** (1) SG waiver with no call for a response, correctly identified as
  the strongest routine-denial signal on the paid docket because the Court
  essentially never grants without a response; (2) the decision below is a
  one-line Rule 36 affirmance, read directly off Appendix A; (3) no conflict
  alleged — it correctly characterizes *Flynn v. SEC* as an analogous remand
  the petition does not claim the Federal Circuit rejected as law; (4)
  error-correction posture under a substantial-evidence standard; (5) petition
  quality, with concrete record reads (the (i)/(ii) slip, the pro se
  misstatement against argued counsel in App. A). Each of these is a
  recognised Rule 10 consideration or a documented Court practice, not a
  generic assertion.
- **Calibration reasoning.** It explains why it did not go below 1%: the
  reached population already includes many weak petitions, GVR residual, and
  honest uncertainty about reading a 194-page record from text. That is the
  right way to think about the floor.
- **Retrieval was purposeful.** Two CourtListener searches aimed at a
  concrete question (is there a pending companion or an intervening decision
  that would make this a hold or GVR vehicle), with the result's limits stated
  (did not open *Margolin*; discount the GVR conditional accordingly).
- **Where to discount me** names the one fact that would most change the
  number (whether the Board's initial decision in fact analyzed gross
  mismanagement), and in which direction.

Minor reservations: "the Court almost never grants without at least a
response" is stated as absolute where "calls for a response before granting"
would be exact, and the relist-increment paragraph leans on a rough
"roughly a quarter" figure whose source in the pack is not named. Neither
affects the disposition analysis.

## Leakage

Mode `forward`; `retrieved_outcome_material: false`;
`influenced_prediction: not_applicable`; `leakage_suspected: false`. Created
2026-09-16 against a 2026-09-16 snapshot ending at the June 17 distribution;
denial 2026-10-05. Captured log (17 calls, coverage 1.0): record, prompt, and
statpack reads plus two captured CourtListener searches on WPA / § 2302(b)(8)
terms. The single `retrieved_doc_date`, 2026-05-26, is *Margolin v. NAIJ*,
an unrelated opinion that predates this event's resolution and is legitimate
forward signal. No query names this petition or docket 25-1289; no
`data/qp-topics/` read. Not a mis-provisioned decided case.

## Big case

My independent read is 0.10 (see `big_case.notes`). The candidate's 0.10 and
its rationale (single-employee reprisal appeal from a Rule 36 affirmance, no
split, narrow remand even on a grant) match the stakes as they resolved.
