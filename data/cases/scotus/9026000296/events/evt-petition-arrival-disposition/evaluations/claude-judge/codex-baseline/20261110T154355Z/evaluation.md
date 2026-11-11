# Evaluation: codex-baseline

This is a **cert** cell: the arrival moment of the petition in *Sethi v. United States Court of Appeals for the Ninth Circuit*, No. 26-296, mode forward. **Outcome:** `denied` (`actual_granted` 0), resolved 2026-11-09. The record shows respondents waived their response on Sep 18, the petition was distributed on Oct 14 for the 11/6/2026 conference, and it was denied on Nov 9 with no noted dissent and no CVSG. The segment base rate and skill score are stamped by the harness; any comparison here refers only to "the stamped segment base rate". The claims block is scored in code and not graded here. No semantic set applies at the cert stage.

**Score:** predicted `denied` at P(grant) = 0.03, which is correct. Brier = 0.0009.

## Reasoning quality: 0.80
The rationale is disciplined. It anchors on the sal-v4 baseline band's reached rate pooled over prior Terms (about 5%). It explicitly declines the terminal zero-relist bucket as an arrival prior, which is the right conditioning. It then adjusts down for sound reasons: the asserted conflict applies settled notice principles (Ruffalo) to a specific record, the petition concedes defective verification and an express show-cause notice, it admits the failure to request a hearing, and it acknowledges that its disciplinary-standards "split" is not aligned and is not a question presented. It checked Ruffalo itself rather than relying on the petition's description. It also separates significance from grant likelihood carefully. One weakness: it stopped at 3%, and the discipline-of-a-circuit's-own-bar posture, where the Court almost never intervenes, arguably justified going lower. It is also somewhat long relative to what drives the number.

## Predicted reasoning: 0.60
I treated four claims as central: denial with no writing, one distribution with no relist, no CVSG, and the conditional grant content. The first three were borne out exactly. However, each is close to the default path for a paid baseline petition with the SG as respondent, so these claims show little a competent reader could have called differently. The document does not commit to a waiver or to timing. The question-presented and route forecasts depend on a grant that never happened, so they earn neither credit nor penalty. The result is correct but mostly generic, a little above the middle anchor because the procedural path was stated specifically and held.

## Leakage
Forward and clean (`not_applicable`). The candidate made no query for this docket's disposition, and its `find` over `data/` excluded qp-topics with `-not -path`. The Ruffalo lookup is historical precedent.

## Big case
My own read is 0.15: a narrow, fact-bound attorney-discipline petition with a topical AI backdrop, which the Court treated as routine.
