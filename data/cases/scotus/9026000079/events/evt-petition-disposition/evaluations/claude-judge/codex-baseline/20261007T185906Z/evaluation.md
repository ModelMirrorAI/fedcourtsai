# Evaluation — codex-baseline — scotus/9026000079 / evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`), forward mode. *Acosta-Tapia v. Blanche*, No. 26-79, paid petition from an unpublished Ninth Circuit memorandum; the Solicitor General waived a response on Aug 14, 2026; distributed once, for the Sept 28, 2026 long conference. **Outcome:** `denied` on Oct 5, 2026, `actual_granted` 0, one distribution, no noted dissent.

**Scores.**

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0004 | (0.02 − 0)² |
| `segment_base_rate` | 0.0501 | `risk_set` basis: the prediction froze `band: baseline` with `salience_version: sal-v4`, the statpack's segment table heading is sal-v4, so the bracketed `baseline` `reached` figures pooled resolved-weighted over Terms 2017–2025 (strictly before Term 2026; the caption renders 10 of 10 Terms, so the rendered window is the pack's window): n = 12,720 |
| `brier_skill_score` | 0.8407 | 1 − 0.0004 / (0.0501 − 0)² |
| `vote_accuracy` | omitted | cert cell; never scored |
| `semantic_grades` | none | no semantic set is declared on a cert event |
| `claim_scores` | not mine | harness-computed |

**What the prediction got right.** The disposition, and the method. The anchor is exactly right: it names the sal-v4 table, pools the bracketed baseline `reached` rows over the nine prior Terms to 5.01% on n = 12,720 (my pooling reproduces the same figure), explicitly refuses the terminal-band substitute and the federal-petitioner floor, and distinguishes the terminal relist and CVSG cuts from forward transition probabilities. The downward adjustment to 2% rests on the right signal: the government's waiver with no ensuing response request. It is scrupulous about the information boundary (does not read elapsed time since the Sept 28 conference as a hold signal, does not treat the caption's immigration hint as fact, discloses that the web attempts returned nothing) and honest about what the forecast is: a docket-skeleton and base-rate forecast, not a substantive assessment. Setting `big_case_score` to null with a stated reason rather than inventing one is the right call under its own information set.

**What drove `reasoning_quality` = 0.65.** The analysis is disciplined, calibrated, and correctly reasoned as far as it goes, and the outcome is consistent with it. What holds it below the top candidate is that it is content-free about the case: it never learned the question presented or the Ninth Circuit's holding, although the lower-court memorandum was retrievable in a forward cell (another candidate obtained it), and its five retrieval attempts went to Supreme Court Rules pages rather than to the case. As a result the vehicle, the doctrinal question, the possibility of a hold-and-GVR path, and the dissent-from-denial estimate are all set by generic priors. The waiver discount is also unmeasured by its own admission ("a judgmental negative update, not a measured waiver-conditioned rate"), which is honest but means the one case-specific inference the document makes is unquantified. This is sound forecasting hygiene over an empty record, not legal analysis of this petition.

**Big case.** My own read, formed before looking at the candidate's score, is 0.08 (see `big_case.notes`); the candidate declined to score, with a rationale that the record did not support one.

**Leakage.** Forward cell. The prediction was written Oct 4, 2026; the denial entry is dated Oct 5, so the case was open and the forward default applies. Checked: the log has 29 calls, 24 captured shell calls (schemas, statpack, path resolution, output writes, validation) and 5 unobserved web-search rows whose queries name Supreme Court Rules pages, not this case or docket; the candidate's retrieval note says all five returned nothing usable. No `retrieved_doc_date`; the one textual `qp-topics` match in the log is a `find … -not -path 'data/qp-topics/*'` exclusion in a shell command, i.e. the path was excluded, not read. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

**Flags.** None. `correct` and `brier_score` are written per their definitions knowing the harness re-stamps `correct`.
