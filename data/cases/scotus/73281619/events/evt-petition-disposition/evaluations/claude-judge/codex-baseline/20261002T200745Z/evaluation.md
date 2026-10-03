# Evaluation — codex-baseline — scotus/73281619 evt-petition-disposition

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
| `reasoning_quality` | 0.70 | below |

The base rate is taken from the prediction's own frozen `context.band`, not re-derived from the decided docket. The per-Term table renders 10 of 10 Terms, so the rendered and held windows coincide and every Term strictly before 2025 is pooled; no window divergence to flag. The candidate anchored on the same figure (484 / 2,810) by the same route, which is the correct self-selection for this cell. No `vote_accuracy` (cert cell), no `judgment_correct`, no `semantic_grades` (no semantic set is declared on a cert event).

## What the reasoning got right and wrong

This is a careful, well-bounded rationale. It identifies the right anchor and pools it correctly. It reads the docket trajectory accurately: the two distributions are a call-for-response cycle, not a relist, and the candidate says so explicitly and refuses to treat the interval as evidence of a hold. It registers the grant-favoring signals in the snapshot, the response requested after a waiver, sixteen amici including a state coalition, recurring statutory questions, and it treats each brief's circuit count as advocacy rather than established fact. The one external lookup, Livingston's treatment of Holt, is used narrowly and for the purpose stated. The candidate is candid that the reply was not read and that the net move from 17 to 30 percent is judgment rather than estimation.

Where it fell short, given the outcome:

- **The vehicle counterweights were weighted as if they attached to the whole petition.** The rationale lists invited error, preservation of the equal-terms claim, and the statutory-coverage objection as reasons to stay "well below one-half." Preservation attaches to Question 2 only, and the invited-error point is about which framework the state court applied rather than whether a federal question was decided. The Court resolved both by granting on Question 1 alone. The rationale never asks whether a limited grant was the natural way out, though the forecast document (not graded here) does name Question 1 as the likelier lead question.
- **The call for a response is noted but under-weighted.** The candidate lists it among the reasons for the upward adjustment but gives no sense that it is the single strongest cert-stage signal on this docket, an affirmative act by at least one chambers before any amicus wall formed.
- **Reasoning on the second distribution cuts both ways and the candidate took only one.** Treating it as "partly procedural" is correct as far as it goes, but a fully briefed petition set for the long conference with a state coalition behind it is the profile the Court grants from; the discount applied for the procedural reading was not balanced against that.

The number landed well above the anchor and in the right direction, the analysis is honest about its limits, and the conditional claims are stated as conditionals. The main weakness is that a correct diagnosis of the vehicle problems was not carried through to the question of how the Court would handle them. Score 0.70.

## Leakage

Mode `forward` per the staged `retrieval_log.json`; the prediction (2026-09-18) predates the grant (2026-10-01). `result_capture_coverage` 0.91. Three rows are `unobserved` (two web searches on DOJ RLUIPA topics and one open of a DOJ guidance URL) and are graded on their queries, none of which names this case, docket, or the parties. The captured rows are shell reads of the provisioned inputs, the statpack and schemas, and two CourtListener calls fetching Livingston Christian Schools (6th Cir. 2017) and a Holt passage within it. No call touches this docket's disposition, no `retrieved_doc_date` post-dates the event, no read under `data/qp-topics/`. The candidate's `retrieval.md` disclosure matches the log. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Nothing suggests a decided case was provisioned forward.

## Big case

Independent read 0.55, notes in `evaluation.json`. The predictors' own scores sit inside the staged `prediction.json`, so the read could not be formed strictly before seeing them; it rests on the record and the grant.

## Not graded

The forecast document (`predicted_reasoning.md`) and the five-claim block were read for context only; the harness scores the claims in code.
