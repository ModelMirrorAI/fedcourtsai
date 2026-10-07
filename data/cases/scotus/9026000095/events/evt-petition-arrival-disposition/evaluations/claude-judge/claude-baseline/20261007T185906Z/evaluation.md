# Evaluation — claude-baseline — scotus/9026000095 — evt-petition-arrival-disposition

## Outcome and scores

Cert-stage arrival cell. The petition (Zhong v. Superior Court of California,
No. 26-95, pro se) drew a brief in opposition from the City of Diamond Bar on
August 20, 2026 (not a waiver), was distributed once for the September 28
conference, and was **denied on October 5, 2026** with no noted dissent
(`actual_disposition: denied`, `actual_granted: 0`).

- `correct` = 1: claude-baseline predicted `denied`.
- `brier_score` = (0.003 − 0)² = 0.000009.
- `segment_base_rate`, `brier_skill_score` **omitted**, `base_rate_basis` null.
  The prediction froze `band: baseline` under `salience_version: sal-v3`; the
  committed `metrics/statpack.md` renders its band table under **sal-v4**. Under
  the prompt's version-mismatch rule the rate and skill are omitted together
  and the mismatch is flagged (see the cell's `flags.json`); the cell is not
  relabelled `terminal`. For the reader only, not as a scored baseline: the
  pack's JSON `alt_segments` carry sal-v3 for every Term with baseline-band
  risk-set figures identical to sal-v4's (pooled OT2017–OT2025 reached rate
  5.02%, n=12,720). The candidate's 6.55% (n≈13,163) was pooled from the per-
  Term rows as rendered on August 16 — its logged arithmetic lists those rows —
  so the difference is pack vintage, not an error in the candidate's pooling.
- `vote_accuracy` omitted (cert stage; never scored).
- `claim_scores` not written (harness-computed). The forecast document and the
  claims block were read for context only and are not scored here.

## Leakage

`mode: forward`; prediction created 2026-08-16, denial 2026-10-05. The log has
22 calls, all `captured` (coverage 1.0): file reads of the prompt, the schema,
the provisioned record, snapshot, questions presented and the full petition
text, two `sed` slices of `metrics/statpack.md`, one `fedcourts query` with a
free-text argument that errored (no rows, no transfer line), `--help`, a Python
pooling computation, and the cell's own writes. No MCP or web calls, no
`retrieved_doc_date`, no query touching this docket's disposition, no
`data/qp-topics/` read. The rationale uses Justice Kagan's August 3 stay denial
from the provisioned snapshot as a weak negative signal and says, correctly,
that it predates the open disposition and is not leakage.
`retrieved_outcome_material: false`, `influenced_prediction: not_applicable`,
`leakage_suspected: false`.

## Reasoning quality — 0.86

Strengths:

- **Correct anchor, correctly reasoned.** It pools the baseline band's
  bracketed `reached` figures over the nine prior Term rows, notes that at the
  arrival moment the frozen-band rule and the whole-paid-segment rule coincide
  for the weakest band, and rules out the `federal` class on the caption. The
  logged computation matches the stated 6.55%.
- **It read the petition and said what was missing from it.** The central
  observation — the petition asserts an "objectively intolerable risk of bias"
  without ever stating the facts said to create it — is exactly what the City's
  brief in opposition later pressed ("The petition omits the allegations
  necessary to evaluate bias"; the allegations were adverse rulings and a
  tentative ruling, which Liteky says almost never suffice).
- **Vehicle and jurisdiction.** §1257 finality against a pending enforcement
  action, the one-sentence finality argument that does not engage the ongoing
  proceedings, the Superior Court and judge as named respondents, no reasoned
  decision below — all borne out by the BIO's finality, state-grounds, and
  Rule 10 sections. The "state procedures vary widely with no cited conflict"
  point was the BIO's Rule 10 argument almost verbatim.
- Good calibration prose: it explains why it stops at 0.3% (GVR residual) and
  which of its own numbers a reader should discount most.
- Candid about retrieval: it tried the corpus CLI, found no discriminating
  filter, and anchored on the pack rather than inventing a prior.

Weaknesses:

- It expected the respondents to waive and the petition to go to conference on
  the waiver; the City filed a 25-page BIO on the response date. The rationale
  reads a missing BIO as "neutral-to-negative (a waiver is likely)", a minor
  misjudgment with no effect on the direction of the number.
- Like codex-baseline, it did not flag the preservation problem — the petition's
  bare "expressly raised and preserved" with no record cite — which became the
  BIO's strongest ground.
- The "paid pro se petitions with no developed split … grant well under 1%"
  rate is asserted from general knowledge rather than a pack figure; it is
  plausible but unsourced.

A thorough, well-anchored rationale whose specific diagnoses of the petition's
weaknesses were confirmed by the opposition brief and the denial.

## Big case

My independent read is 0.03 (formed from the record before consulting the
candidate's score): local pro se code-enforcement dispute, no split, no
institutional petitioner, stay denied twice, denied without comment. The
candidate's own 0.03 rationale points the same way; I record no agreement
number.
