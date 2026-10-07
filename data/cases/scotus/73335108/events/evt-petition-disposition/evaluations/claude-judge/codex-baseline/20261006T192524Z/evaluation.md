# Evaluation: codex-baseline — Watson v. Mason, No. 25-1279 (scotus/73335108), evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition was **denied** on 2026-10-05 at its first conference (one distribution, no relist, no CVSG, no noted dissent). The candidate predicted `denied` with P(grant) = 0.008.

| field | value | basis |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.000064 | (0.008 − 0)² |
| `segment_base_rate` | 0.0512 | `risk_set`; see below |
| `brier_skill_score` | 0.9756 | 1 − 0.000064 / 0.0512² |
| `reasoning_quality` | 0.82 | see below |

**Base rate.** The prediction's frozen context carries `band: baseline` **and** `salience_version: sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set`. I pooled the bracketed `reached` figure for the `baseline` column, resolved-weighted, over the rendered Terms strictly before this case's Term (2025): Terms 2017–2024, n = 11,580, ≈ 592.9 weighted grants, rate ≈ 0.0512. The caption renders 10 of 10 Terms, so the rendered window is the pack's window and no window divergence arises; the configured ten-Term lookback would reach 2015 but the pack carries nothing before 2017, so the in-code pool is bounded to the same eight Terms.

## Leakage

Forward cell, graded from the harness-captured log. The prediction was created 2026-09-16 against a snapshot whose last proceeding is the 2026-06-17 distribution; the denial came 2026-10-05, nineteen days later. The 35-call log shows record reads, ten `web-search` rows (all `unobserved`, so graded on their queries: Rule 10, the Court's rules-guidance page, Estelle v. McGuire) and captured `curl` fetches of the Cornell LII Rule 10 and Estelle pages. No query names this docket or caption, no `retrieved_doc_date` is at or after the resolution, and nothing touches `data/qp-topics/`. The reasoning conditions throughout on an open docket. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. No mis-provisioning: the case was genuinely open when predicted.

## What the reasoning got right

- **The anchor is exactly the one the contract asks for**, computed correctly: the bracketed `reached` baseline figure pooled over Terms 2017–2024 with n = 11,580 and ≈ 5.12%. It explicitly excludes the case's own Term and refuses the terminal figure, and it says the pool is a weighted average of rounded displayed rates rather than a reconstruction of counts.
- **Case-specific discounting is grounded in the right doctrine.** The vehicle is an unpublished COA denial; the petition's federal hook depends on converting a Wisconsin-law inconsistency into a due-process violation, which Estelle v. McGuire makes hard; the asserted "split" on petition page 22 names no comparator jurisdiction. Each of these is a real reason this petition sits at the weak end of the baseline pool.
- **It keeps conditional and unconditional probabilities apart** (the 60% summary-route figure is stated as conditional on a grant and converted to 0.48% unconditional), and it is careful about what it does not know: no appendix, no lower-court opinion, petitioner's account of the acquittal is not a finding.
- **Provenance is honest.** It states which external fetches succeeded and which did not, and that no outcome was sought.

## Where it falls short

- **The discount is less sharp than the record supports.** It lands at 0.8%, roughly a six-fold cut from the anchor, without engaging the strongest negatives the other features of this petition present: the petitioner is self-represented, the capital-sentencing authorities (Lockett, Eddings) are inapplicable to a guilt-phase instruction in a non-capital case, and Patterson/Martin v. Ohio already let States allocate the self-defense burden. Those are the features that push a petition like this toward the bottom of the band, and the reasoning does not name them.
- **It does not read the waiver as a signal** beyond "supports staying below the broad baseline". On a paid docket where the Court distributes without calling for a response, that is a meaningful negative, and the reasoning treats it very lightly.
- **The stakes read (0.16) is high for this petition** and the rationale half-concedes it ("serious individual liberty claim" versus "no developed interjurisdictional conflict"). That is the predictor's `big_case_score`, graded elsewhere by rank-agreement, so it does not move `reasoning_quality`; I note it because the same instinct seems to keep the probability from dropping further.
- Some of the document is about the run environment (a read-only uv cache, failed browser calls), which belongs in a retrieval note rather than in the rationale for the number.

`reasoning_quality` = 0.82: correct anchor and basis, sound and well-sourced legal discounting, candid about limits, but the adjustment leaves the most powerful case-specific negatives unused.

## Big case

My independent read is 0.04, formed from the record and the outcome before weighing the candidate's own score (which is visible in the staged `prediction.json`, so I could not avoid seeing it; I set my number from the record first). A pro se, paid, non-capital state habeas petition from an unpublished COA denial, turning on one Wisconsin statute and one pattern instruction, with the State waiving and the Court denying at first conference without writing. Stakes beyond the petitioner are negligible.

## Not scored here

`vote_accuracy` is omitted (cert stage; no votes were predicted or noted). `claim_scores` is the harness's. No `semantic_grades` block: no semantic set is declared on a cert event. The forecast document was read for context only and is unscored.
