# Evaluation of `codex-baseline` (`scotus/9026000462`, `evt-petition-disposition`)

## Quantitative summary

- **Stage:** `cert` (discretionary petition for writ of certiorari, `moment: distribution`)
- **Predicted disposition / probability:** `denied`, `P(grant) = 0.03`
- **Actual outcome:** `denied` (`actual_granted = 0`) on `2026-11-09`
- **Correct:** `1`
- **Brier score:** `0.0009`
- **Segment base rate & skill score:** Left null for harness stamping against the stamped segment base rate.

## Analysis of `reasoning.md` (`reasoning_quality = 0.78`)

`codex-baseline` demonstrated strong methodological discipline in reading the docket and pooling the base rate. Grading `codex-baseline`'s base-rate use against statpack build `1c4f550b7b75` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, the `sal-v4` build in force at `20261008T143010Z`, rebuilt via `fedcourts statpack-at`, rather than the currently committed `sal-v8` statpack), `codex-baseline` properly selected the `sal-v4` `baseline` band's bracketed `reached` (risk-set) rate pooled across strictly prior Terms (OT2017–OT2025) from `statpack.json`, matching the stamped segment base rate definition. `codex-baseline` also correctly diagnosed the docket sequence: the September 9, 2026 distribution preceded the October 7 docketing of the cert petition and sat in the sequence disposing of the linked sealing motion `26M22` (granted October 5), so the next distribution entry (`relist-increment: 0.90`) would be the petition's initial substantive conference distribution rather than a post-conference relist.

Where `codex-baseline` fell short of `claude-baseline` was in lower-court retrieval when faced with the whitespace-only `petition.txt` (`empty_text: true` on October 8, prior to the October 18 OCR pass). `codex-baseline` ran a single CourtListener opinion search (`type="o"`, `court="ca8"`, `docket_number="25-2561"`, `filed_before="2026-03-24"`), which returned zero results, and stopped there without searching CourtListener's RECAP docket collection (`type="r"` or `type="d"`), where the originating N.D. Iowa docket (`2:23-cv-01033`) was available and disclosed both the nature of suit (ADA employment discrimination) and the June 2, 2025 Rule 37(b)(2) discovery-sanction dismissal with prejudice. Because `codex-baseline` did not check RECAP dockets, it treated the substantive legal issue as completely unknown, left `big_case_score` null, and made only a modest downward adjustment to `P(grant) = 0.03` (five times higher than `claude-baseline`'s `0.006`).

## Predicted reasoning (`predicted_reasoning_quality = 0.88`)

`codex-baseline`'s `predicted_reasoning.md` laid out clear, well-structured central claims that were borne out by the outcome:

1. **Silent denial in November or December 2026 (`borne-out`):** `codex-baseline` predicted that the Court would deny the petition in November or December 2026 without an explanatory opinion or separate writing. The Court denied certiorari on November 9, 2026 with `noted_dissent_from_denial: false`.
2. **One additional distribution entry for initial substantive cert consideration, followed by denial without further relists (`borne-out`):** `codex-baseline` explained that the September 9 distribution concerned the sealing motion `26M22` (granted October 5) and predicted one additional distribution entry (`0.90`) for the petition's initial substantive cert conference, with no further distributions after that. The petition received exactly one more distribution on October 14, 2026 for the November 6 conference (`signals.distribution_count: 2`) and was denied on November 9.
3. **Disposition on the waiver without a requested response or CVSG (`borne-out`):** `codex-baseline` predicted that the respondent's October 7 waiver would be followed by disposition without a call for a response and without a CVSG (`0.005`). Neither occurred.
4. **Plenary review vs. summary disposition conditional on a grant (`unresolved`):** Conditional on a grant, `codex-baseline` placed 65% on plenary review and 35% on summary disposition while abstaining on the substantive question; because certiorari was denied, this conditional claim was not tested.

The forecast earns `0.88`: all testable central claims—including the non-obvious single-additional-distribution call driven by the `26M22` motion sequence—were specific and borne out, with a slight deduction relative to `claude-baseline` only because `codex-baseline` could not address the underlying subject matter that RECAP dockets disclosed and gave a slightly broader November/December timing window.

## Leakage assessment

- **Mode:** `forward` (predicted `2026-10-08T15:08:31Z`; resolved `2026-11-09`).
- **Assessment:** In `retrieval_log.json` (`result_capture_coverage: 0.96`, 24 of 25 calls captured), the single `unobserved` call was a `web-search` attempt to read the pre-decision petition PDF URL from `documents.json` (`20261007131240670_Petition.Hauber.pdf`), and the shell `find` command explicitly excluded `data/qp-topics/*` via `-not -path 'data/qp-topics/*'`. No outcome-revealing material existed or was retrieved. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.
