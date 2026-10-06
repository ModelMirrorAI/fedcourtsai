# Evaluation — gemini-baseline — scotus/73392441 evt-petition-disposition

## Cell

Cert-stage petition event (`stage: cert`, `moment: distribution`), forward mode. Outcome: certiorari **denied** on 2026-10-05 after a single distribution (for the September 28, 2026 conference), no CVSG, no noted dissent. `actual_granted = 0`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` == `actual_disposition: denied` |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 (593 / 11,580) |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.990467 | 1 − 0.000025 / 0.051209² |
| `reasoning_quality` | 0.55 | see below |

Base-rate detail: the prediction's frozen context carries both `band` and `salience_version`, and the committed `metrics/statpack.md` *Segment base rate by salience band (sal-v4)* heading matches, so the `risk_set` basis applies. The table caption renders 10 of 10 Terms, so the rendered window is the whole pack; the Terms strictly before the case's Term 2025 are OT2017–OT2024. The pooled rate from the unrounded `statpack.json` prefix fields is 593 / 11,580 = 0.051209. No window divergence to flag.

`vote_accuracy` omitted (cert stage, never scored). `judgment_correct` null. No `semantic_grades` block: no semantic set is declared on a cert event and the prediction carries none.

## What the prediction got right

The disposition, the absence of a relist, the absence of a CVSG, and the absence of separate writing. The lowest probability of the three candidates, so the best Brier and skill on this cell.

## Reasoning quality — 0.55

The conclusion is right and the two load-bearing legal points are correct: the Seventh Amendment's civil-jury guarantee does not bind state courts, and a complaint about a state court's application of the summary-judgment standard to the facts is error-correction that Rule 10 disfavors. The absence of a brief in opposition and the lack of any asserted split are correctly noted.

Deductions, which are about the analysis rather than the number:

- **Base rate misread.** The anchor is stated as "~5.7% (reached)", which is the single OT2024 row of the sal-v4 table, not the rate pooled over the prior Terms the prompt directs (≈5.1%). The direction of the adjustment is unaffected, but the yardstick the predictor says it is adjusting from is not the registered one.
- **Thin engagement with the record.** The log shows the first hundred lines of the petition read and nothing of the remainder. The reasoning does not mention that the underlying action was an equitable reformation claim, that the Court of Appeals decision was unpublished, that state discretionary review was denied, or what the trial judge actually did that the petitioner calls fact-finding. The analysis would read the same for almost any state-court summary-judgment petition.
- **A loose docket inference.** "Placed on the long conference list, which typically signals a denial without further attention" treats routine summer distribution as a signal. Every petition docketed over the summer is distributed for the long conference; the denial rate off that conference is high, but the distribution itself conveys nothing about this petition.
- **Characterization.** The big-case rationale calls this a "pro se-style petition"; the petition was filed by counsel. The "-style" hedge keeps it from being wrong, but it suggests the petition's authorship was not checked.
- `confidence` is null and the document is a single paragraph with no stated limitations or sources beyond the statpack.

Sound bottom line, minimal and partly inexact support.

## Leakage

`mode: forward`. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Forward cell; prediction created 2026-09-17, well before the 2026-10-05 denial. Log has result_capture_coverage 0.0 (every call unobserved, an engine shape, not a defect), so each call is graded on its query: 25 calls, all local file reads of the prompt, AGENTS.md, the provisioned record, documents and statpack sections, plus the output writes and a validate run. No external call of any kind, no web search, no MCP call, no qp-topics path. Nothing retrieved could carry this case's outcome. Because every call is `unobserved`, the clean grade rests on the queries (all local, all provisioned or committed inputs) rather than on observed results; there is no external call whose result could have carried the outcome. The prediction predates the conference and the denial, so the forward routing was correct.

## Big-case read

My independent read, formed before reading the candidate's score: 0.05. Independent read formed before looking at the candidates' scores: a private deed-of-trust reformation dispute from an unpublished Washington Court of Appeals decision after discretionary state review was denied; the questions presented recast one summary judgment ruling as a Due Process and Seventh Amendment attack on summary judgment itself. No response was called for, one distribution, denied without noted dissent. Stakes for anyone beyond the parties are negligible. The candidate's 0.01 is lower still; the one-line rationale is consistent with mine in direction.
