# Evaluation — claude-baseline — scotus/73281619 evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`), forward mode. Missionaries of Saint John the Baptist, Inc. v. Frederic, No. 25-1131, from the Supreme Court of Kentucky. Outcome: petition **granted** on October 1, 2026, limited to Question 1 (the RLUIPA substantial-burden question), plenary route, after two distributions (May 12 for the May 28 conference, then a call for a response on May 14; September 2 for the September 28 long conference). `actual_disposition` = `granted`, `actual_granted` = 1.

**The prediction.** `denied`, P(grant) = 0.30, frozen context `band: elevated`, `salience_version: sal-v4`, `term: 2025`, `mode: forward`, no cutoff, snapshot 2026-09-18.

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 0 | `denied` vs `granted` |
| `brier_score` | 0.49 | (0.30 − 1)² |
| `segment_base_rate` | 0.172242 | sal-v4 `elevated` bracketed `reached` figure, pooled resolved-weighted over Terms 2017–2024 (484 / 2,810) |
| `base_rate_basis` | `risk_set` | the prediction froze both a band and a salience version, and the statpack table heading names the same version (sal-v4) |
| `brier_skill_score` | 0.2849 | 1 − 0.49 / (0.172242 − 1)² = 1 − 0.49 / 0.685183 |
| `reasoning_quality` | 0.75 | below |

The base rate is taken from the prediction's own frozen `context.band`, not re-derived from the decided docket. The per-Term table renders 10 of 10 Terms, so the rendered and held windows coincide and every Term strictly before 2025 is pooled; no window divergence to flag. The candidate anchored on the same figure (17.2 percent, n = 2,810) by the same route. No `vote_accuracy` (cert cell), no `judgment_correct`, no `semantic_grades` (no semantic set is declared on a cert event).

## What the reasoning got right and wrong

This is the most complete analysis of the three. It reads the docket trajectory correctly (a call-for-response cycle, "the Court has never yet voted the petition up or down") and names the response requested after a waiver as the strongest single signal, which is the right ranking. It weighs the sixteen amici and the Kentucky-led twenty-state coalition, the counsel on both sides, the Court's acknowledged interest in religious land use this Term (Grand), and, importantly, verifies on CourtListener that a published, divided Third Circuit decision (Anash, July 30, 2026) sharpened the substantial-burden split after the petition was filed, a fact the candidate correctly infers the reply would lead with. On the deny side it marshals the invited-error and preservation points, the odd posture (private neighbors enforcing a state statute, the RLUIPA claimant having won before the board), and a specific track record of recent RLUIPA land-use denials. It separates the preservation problem (Question 2) from the substantial-burden question (Question 1), which is the distinction the Court's limited grant turned on. Its "where to discount me" section is candid and accurate.

Where it fell short, given the outcome:

- **The landing undervalues its own analysis.** The candidate says a clean municipal-denial vehicle would put it at 0.45 to 0.50 and then pulls back "hard" to 0.30. The pull-back rests on vehicle flaws that the rationale itself has already shown attach mostly to Question 2 and to a threshold argument it calls "not really an independent state ground." Having identified that the Court could grant Question 1 alone, the rationale did not price that path.
- **The track-record argument is weaker than presented.** None of the four cited denials carried a response requested after a waiver plus a state coalition, so the comparison class does not match the signals the candidate had just ranked highest.
- **One retrieval was outside the record for this case.** The candidate read a sibling docket's event file and one of its prediction files (Grand, scotus/73281006) to learn that case's question presented. It is a different case and carries nothing about this petition's result, so it is not leakage, and the candidate disclosed it; but a prediction file is not a case record, and the same fact was available from the CourtListener cluster it also fetched.

The analysis found more of the grant-favoring structure than either other candidate and identified the exact shape of the outcome as the most likely grant form. The probability it reported did not fully reflect that. Score 0.75.

## Leakage

Mode `forward` per the staged `retrieval_log.json`; the prediction (2026-09-18) predates the grant (2026-10-01). `result_capture_coverage` 1.0. CourtListener rows: a zero-result docket search for No. 25-965, Anash v. Borough of Kingston (`retrieved_doc_date` 2026-07-30), a zero-result search for Spirit of Aloha Temple, Grand v. University Heights at the Sixth Circuit (2025-11-13) and its cluster record. One corpus query returned five generic recent grants (its `ranged corpus reads` line is in the candidate's `retrieval.md`). Shell reads cover the provisioned inputs, the statpack, schemas, and the Grand sibling-case files noted above. No row names this docket's disposition, no `retrieved_doc_date` post-dates the event, no read under `data/qp-topics/`. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Nothing suggests a decided case was provisioned forward.

## Big case

Independent read 0.55, notes in `evaluation.json`. The predictors' own scores sit inside the staged `prediction.json`, so the read could not be formed strictly before seeing them; it rests on the record and the grant.

## Not graded

The forecast document (`predicted_reasoning.md`) and the five-claim block were read for context only; the harness scores the claims in code.
