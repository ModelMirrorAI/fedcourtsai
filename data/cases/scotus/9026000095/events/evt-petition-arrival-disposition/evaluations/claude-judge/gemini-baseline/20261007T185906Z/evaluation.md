# Evaluation — gemini-baseline — scotus/9026000095 — evt-petition-arrival-disposition

## Outcome and scores

Cert-stage arrival cell. The petition (Zhong v. Superior Court of California,
No. 26-95, pro se) was distributed once, for the September 28, 2026 conference,
and **denied on October 5, 2026** with no noted dissent (`actual_disposition:
denied`, `actual_granted: 0`).

- `correct` = 1: gemini-baseline predicted `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate`, `brier_skill_score` **omitted**, `base_rate_basis` null.
  The prediction froze `band: baseline` under `salience_version: sal-v3`; the
  committed `metrics/statpack.md` renders its "Segment base rate by salience
  band" table under **sal-v4**. The prompt's rule for a heading/version
  mismatch is to omit the rate and the skill together and flag it, which this
  cell does (see the cell's `flags.json`). I did not relabel the cell
  `terminal`. For the reader only, and not as a scored baseline: the pack's
  JSON carries sal-v3 `alt_segments` for every Term, and the baseline band's
  risk-set figures there are identical to the sal-v4 ones (pooled OT2017–OT2025
  reached rate 5.02%, n=12,720), so the candidate's 0.005 would sit far below
  any baseline-band anchor on either version.
- `vote_accuracy` omitted (cert stage; never scored).
- `claim_scores` not written (harness-computed). The forecast document and the
  claims block were read for context only and are not scored here.

## Leakage

`mode: forward`; the prediction was created 2026-08-16, seven weeks before the
denial. The retrieval log has 23 calls with `result_capture_coverage` 0.0 —
every call `unobserved`, which is an engine's standing shape, not a defect — so
each call is graded on its query. Every query is a local read of the provisioned
record, the prompts, the schema, or `metrics/statpack.md`, or one of the cell's
own writes. No `retrieved_doc_date`, no query touching this docket's
disposition, no `data/qp-topics/` read, no MCP or web call. The reasoning's one
docket-acquired fact — Justice Kagan's August 3 denial of the stay application
and its refiling to the Chief Justice — is on the provisioned snapshot and
predates resolution; legitimate forward signal, not leakage.
`retrieved_outcome_material: false`, `influenced_prediction: not_applicable`,
`leakage_suspected: false`.

## Reasoning quality — 0.55

What the rationale gets right:

- It anchors correctly on the weakest band's bracketed `reached` figure (~6.5%
  as the table then read) and adjusts sharply downward, which is the right
  shape for a pro se petition attacking a state court's summary denial of a
  disqualification motion.
- The three substantive reasons — fact-bound, no clean split on a pure federal
  question, state summary denials rarely reviewed — are all correct and were
  each borne out by the brief in opposition, which pressed the absence of any
  Rule 10 conflict and the fact-specific nature of the bias allegations.
- Reading the single-Justice stay denial and refiling as a negative signal is a
  reasonable use of the provisioned docket.

What holds the score down:

- The rationale is thin. It is a paragraph of correct generalities, not an
  analysis of this petition. The retrieval log shows the questions-presented
  file and documents index were read but **not** the nine-page petition text
  itself, and the rationale reflects that: nothing on the §1257 finality
  problem (the enforcement action is still pending below), nothing on the
  posture (a summarily denied writ of mandate with the court and judge as named
  respondents), nothing on whether Murchison/Caperton/Williams actually support
  a reasoned-ruling requirement. Those were the dispositive vehicle defects and
  the brief in opposition led with them.
- "Appears to be a solo practitioner or pro se filer" hedges a fact the
  petition's cover states outright (Pro Se Petitioners).
- No calibration discussion — why 0.005 rather than 0.02 or 0.001 — and no
  acknowledgement that the snapshot post-dates the arrival moment.

Right outcome, right direction, and a defensible number, reached by a correct
but shallow route. The score reflects soundness of analysis, not the hit.

## Big case

My independent read is 0.03 (formed from the record before consulting the
candidate's score): a local code-enforcement dispute, pro se, no split, no
institutional party, no amicus, no separate writing, stay denied twice. The
candidate's own 0.05 rationale points the same way; I record no agreement
number.
