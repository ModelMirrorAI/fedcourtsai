# Evaluation of `codex-baseline` — `scotus/9026000433` (`evt-petition-disposition`)

## Outcome and Quantitative Summary

This is a forward certiorari-stage cell (`moment: distribution`). On November 16, 2026, the Supreme Court denied certiorari off the initial November 13, 2026 conference distribution (`actual_disposition = "denied"`, `actual_granted = 0`, `signals.distribution_count = 1`, `signals.cvsg_date = null`, `noted_dissent_from_denial = false`).

- **Predicted disposition:** `denied` (`correct = 1`)
- **Predicted grant probability:** `0.12` (`brier_score = 0.0144`)
- **Baseline and skill:** Left null for harness stamping; skill is evaluated on the board against the stamped segment base rate.

## Assessment of `reasoning.md` (`reasoning_quality = 0.72`)

`codex-baseline` conducted the strongest primary-source verification among the three candidates, but paired that thorough doctrinal legwork with a miscalibrated upward probability adjustment:

1. **Exemplary primary-source verification:** `codex-baseline` read both `petition.txt` and `appendix.txt` directly and used CourtListener MCP tools (`search`, `search_document`, `read_document`) to inspect the Eleventh Circuit's opinion in *DeMarcus v. University of South Alabama*, 133 F.4th 1305 (11th Cir. 2025). That check uncovered a key weakness in the petition's circuit-split narrative: *DeMarcus* expressly treated the framing dispute as non-dispositive and resolved the claims on qualified immunity rather than holding that a plaintiff prevails on conscience-shocking conduct alone without a protected interest.
2. **Accurate statpack reading:** Rebuilding the candidate-time statpack (`7bcde3b105cb` via `fedcourts statpack-at`, under `sal-v4`) confirms that `codex-baseline` verified the exact pre-2026 `baseline` risk-set counts in `statpack.json` and accurately quoted the candidate-time marginal tables (`relist_bucket`, `cvsg`, `cert_amicus`, and `ca3`).
3. **Significant calibration error in probability synthesis:** Despite documenting every major vehicle and posture headwind—respondents' October 16 and October 20 waivers with no response call, an unpublished Third Circuit qualified-immunity affirmance, Judge Roth's agreement on the absence of clearly established precedent, and *DeMarcus* itself turning on qualified immunity—`codex-baseline` adjusted **upward** to `probability = 0.12` (`0.09` plenary grant + `0.03` GVR) and `relist-increment = 0.24`. Moving well above the unconditional risk-set anchor (which already includes petitions with filed or requested oppositions) on a BIO-waived petition was directionally unsound: `codex-baseline` gave excessive weight to the marginal `cert_amicus = 1` cut despite acknowledging its confounding with CVSGs and relists, and its numbers implied an implausible `50%` conditional grant rate (`0.12 / 0.24`) if a response call and second distribution occurred. Its `cvsg-increment = 0.01` on a municipal police-misconduct tort suit with no federal statutory or institutional interest was likewise overstated.

## Predicted reasoning (`predicted_reasoning_quality = 0.82`)

Evaluated strictly on its own commitments rather than on `prediction.json`'s probabilities, `codex-baseline`'s `predicted_reasoning.md` held up well against the staged record:

- **Disposition and separate writings (`borne-out`):** Led with a clear forecast that the Court would deny the petition without a separate writing (`actual_disposition = "denied"`, `noted_dissent_from_denial = false`).
- **Procedural trajectory (`borne-out`):** Identified the modal path as an order-list denial directly from the November 13, 2026 conference with no additional distribution, no relist (`distribution_count = 1`), and no CVSG (`cvsg_date = null`).
- **Conference rationale and conditional scenarios (`unresolved`):** Its explanation of why denial was favored and its discussion of conditional response-call, merits/GVR/summary-reversal, and separate-writing scenarios (naming Justice Sotomayor and secondarily Justice Thomas) are left untested by the Court's bare `Petition DENIED.` order.

All testable central claims were borne out with no failed calls; the grade sits slightly below `claude-baseline` only because `codex-baseline` devoted substantially more space to hedged conditional grant/GVR/summary-reversal scenarios and did not pin the November 16 orders-list date.

## Leakage Audit

`retrieval_log.json` records `mode = "forward"` (`run_id = 20261030T011325Z`), 17 days prior to the November 16, 2026 denial. Thirty-four of 35 logged calls are `captured` (`result_capture_coverage = 0.9714`), covering local file/statpack reads, two `fedcourts query` calls on granted priors (latest `retrieved_doc_date = 2026-10-22`), and four CourtListener MCP calls examining *DeMarcus* (`133 F.4th 1305`); the single `unobserved` `web-search` call queried *County of Sacramento v. Lewis* (`523 U.S. 833`), not this docket. No `data/qp-topics/` reads or outcome-revealing material appear (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
