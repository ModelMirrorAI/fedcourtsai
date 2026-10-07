# Evaluation — gemini-baseline — scotus/9026000079 / evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`), forward mode. *Acosta-Tapia v. Blanche*, No. 26-79, paid petition from an unpublished Ninth Circuit memorandum; the Solicitor General waived a response on Aug 14, 2026; distributed once, for the Sept 28, 2026 long conference. **Outcome:** `denied` on Oct 5, 2026, `actual_granted` 0, one distribution, no noted dissent.

**Scores.**

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.000004 | (0.002 − 0)² |
| `segment_base_rate` | 0.0501 | `risk_set` basis: the prediction froze `band: baseline` with `salience_version: sal-v4`, the statpack's segment table heading is sal-v4, so the bracketed `baseline` `reached` figures pooled resolved-weighted over Terms 2017–2025 (strictly before Term 2026; the caption renders 10 of 10 Terms, so the rendered window is the pack's window): Σ(rate×n)/Σn with n = 12,720 |
| `brier_skill_score` | 0.9984 | 1 − 0.000004 / (0.0501 − 0)² |
| `vote_accuracy` | omitted | cert cell; never scored |
| `semantic_grades` | none | no semantic set is declared on a cert event |
| `claim_scores` | not mine | harness-computed |

**What the prediction got right.** The disposition and the mechanism: it picked out the Solicitor General's waiver, with no call for a response before the conference, as the controlling signal, correctly observed that a grant would first require the Court to request a response, and that a CVSG is structurally impossible with the United States as respondent. It anchored on the right table (the sal-v4 baseline risk-set rate, which it quoted as 4–6%) and correctly noted the relist-count cut as the gate on grant probability. The forecast of a single-conference denial with no writing is exactly what happened.

**What drove `reasoning_quality` = 0.50.** The direction is sound but the document is thin and the number is not argued for. From a 5% band anchor it lands at 0.2%, below anything in the statpack it cites (the relist-0 terminal cut, which it quotes as 1.2% granted, is itself 1.7% including GVRs), on two sentences of adjustment and a presumption that the lowest tier is "presumably lower". It never engages with what the case is about: no attempt to learn the question presented or the lower-court holding, no account of vehicle quality, no consideration of the hold-and-GVR path that a recurring post-*Riley v. Bondi* timeliness question could open. The inference that a Rule 34.6 paper-only directive "suggests a routine or highly idiosyncratic case" is weak: that directive is about filing mechanics, not merit. The number scored extremely well because the petition was denied, but the Brier reward for 0.002 over 0.02 is a calibration gamble the reasoning does not earn, and `reasoning_quality` grades the soundness of the analysis rather than the result.

**Big case.** My own read, formed before looking at the candidate's score, is 0.08 (see `big_case.notes`); the candidate's 0.05 sits in the same low range.

**Leakage.** Forward cell. The prediction was written Oct 4, 2026; the denial entry is dated Oct 5, so the case was genuinely open and the forward default applies. Checked rather than rubber-stamped: the log's 26 calls are all `unobserved` (coverage 0.0, this engine's standing shape), so each is graded on its query — in-repo reads of the provisioned record, prompt, schemas, and statpack, and local writes; no web, MCP, or corpus call; no `retrieved_doc_date`; no `data/qp-topics/` read; the reasoning reads nothing off the outcome. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

**Flags.** None. `correct` and `brier_score` are written per their definitions knowing the harness re-stamps `correct`.
