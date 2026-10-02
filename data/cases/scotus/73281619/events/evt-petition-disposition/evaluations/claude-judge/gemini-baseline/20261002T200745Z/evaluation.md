# Evaluation — gemini-baseline — scotus/73281619 evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`), forward mode. Missionaries of Saint John the Baptist, Inc. v. Frederic, No. 25-1131, from the Supreme Court of Kentucky. Outcome: petition **granted** on October 1, 2026, limited to Question 1 (the RLUIPA substantial-burden question), plenary route, after two distributions (May 12 for the May 28 conference, then a call for a response on May 14; September 2 for the September 28 long conference). `actual_disposition` = `granted`, `actual_granted` = 1.

**The prediction.** `denied`, P(grant) = 0.05, frozen context `band: elevated`, `salience_version: sal-v4`, `term: 2025`, `mode: forward`, no cutoff, snapshot 2026-09-18.

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 0 | `denied` vs `granted` |
| `brier_score` | 0.9025 | (0.05 − 1)² |
| `segment_base_rate` | 0.172242 | sal-v4 `elevated` bracketed `reached` figure, pooled resolved-weighted over Terms 2017–2024 (484 / 2,810) |
| `base_rate_basis` | `risk_set` | the prediction froze both a band and a salience version, and the statpack table heading names the same version (sal-v4) |
| `brier_skill_score` | −0.3172 | 1 − 0.9025 / (0.172242 − 1)² = 1 − 0.9025 / 0.685183 |
| `reasoning_quality` | 0.25 | below |

The base rate is taken from the prediction's own frozen `context.band`, not re-derived from the decided docket. The per-Term table renders 10 of 10 Terms (2017–2026), so the rendered window and the pack's window coincide and every Term strictly before 2025 is pooled; no window divergence to flag. The pooled figure uses the `prefix_est_grant_rate` × `prefix_weighted_resolved` entries in `metrics/statpack.json` for the sal-v4 `elevated` segment, which reproduce the table's bracketed figures. No `vote_accuracy` (cert cell; the empty `votes` block is never scored here), no `judgment_correct`, no `semantic_grades` (no semantic set is declared on a cert event).

## What the reasoning got right and wrong

The one-paragraph rationale starts in the right place: it names the prior-Term `elevated` anchor at about 17 percent and identifies the genuine circuit split on both RLUIPA provisions. It also correctly spots the two vehicle arguments the brief in opposition presses hardest, invited error on the substantial-burden test and late preservation of the equal-terms claim.

From there the analysis fails in three ways that matter given the outcome.

1. **A severe, under-argued cut below the anchor.** The candidate itself says the base rate is about 17 percent and that a relisted petition with strong counsel runs 15 to 25 percent, then lands at 5 percent, below the terminal rate for the band and near the whole-docket paid rate. The only stated reason is that the respondents' vehicle arguments are "fatal." A brief in opposition's vehicle section is advocacy; nothing in the rationale tests it against the petition's answers or asks whether the Court could route around it. The Court did exactly that, granting on Question 1 alone and leaving the under-preserved equal-terms question behind. A reader weighing both briefs could have seen that the preservation problem attached to one question and not the other.

2. **Misreading the docket trajectory.** The rationale treats the two distributions as "the first relist," and the forecast repeats it. The second distribution followed a call for a response, two extensions, the brief in opposition and the reply; the Court had not yet voted the petition at all. The stronger reading of that sequence, a response requested after the respondents waived, is a grant-favoring signal the rationale never mentions.

3. **Ignored grant signals in the provisioned snapshot.** Sixteen cert-stage amicus briefs including a Kentucky-led state coalition appear in the docket entries the candidate read, and are absent from the analysis. Counsel is named but only as something the vehicle problems overcome.

The rationale is internally inconsistent (a stated 15 to 25 percent range, then 5 percent) and the correction it applies to the anchor runs in the wrong direction by a wide margin. The negative skill score reflects that: a forecaster who simply wrote the band rate would have scored better. The direction of the miss is not what drives the grade; the thinness of the argument for a very confident number is. Score 0.25.

## Leakage

Mode `forward` per the staged `retrieval_log.json`; the prediction (2026-09-18) predates the grant (2026-10-01). The log's `result_capture_coverage` is 0.0, so every row is graded on its query rather than its result: all 35 calls are file reads, directory listings, shell reads of the provisioned snapshot, context, event, petition, brief in opposition, and the committed statpack, plus the output writes and a validate run. No web or CourtListener call, no query reaching for this docket's result, no `retrieved_doc_date`, no read under `data/qp-topics/`. The reasoning cites nothing later than the snapshot. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Nothing suggests a decided case was provisioned forward: the 2026-09-18 snapshot ends at the September 2 distribution.

## Big case

Independent read 0.55, notes in `evaluation.json`. The predictors' own scores sit inside the staged `prediction.json`, so the read could not be formed strictly before seeing them; it rests on the record and the grant.

## Not graded

The forecast document (`predicted_reasoning.md`) and the five-claim block were read for context only; the harness scores the claims in code.
