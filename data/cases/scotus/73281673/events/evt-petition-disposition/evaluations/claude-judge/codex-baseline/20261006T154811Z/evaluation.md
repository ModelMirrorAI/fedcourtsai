# Evaluation of codex-baseline — Gasper v. Wisconsin, No. 25-1191 (evt-petition-disposition)

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied on 2026-10-05** after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false, two distributions under `dist-v2`). The docket: petition filed April 14, Wisconsin waived April 21, distributed May 5 for the May 21 conference, response requested May 8, BIO June 1, one amicus June 8, redistributed June 17 for September 28, denied October 5.

## Scores

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `denied` == `denied` |
| `brier_score` | 0.0025 | (0.05 − 0)² |
| `segment_base_rate` | 0.1724 | elevated band, `sal-v4`, bracketed `reached` figures pooled resolved-weighted over Terms 2017–2024 (n = 2810) |
| `base_rate_basis` | `risk_set` | the prediction froze `band: elevated` with `salience_version: sal-v4`, and the statpack table heading is `sal-v4` |
| `brier_skill_score` | 0.916 | 1 − 0.0025 / 0.1724² |
| `reasoning_quality` | 0.85 | below |

Base-rate detail. The prediction's frozen `context` carries both `band` (`elevated`) and `salience_version` (`sal-v4`), Term 2025, so the risk-set basis applies. The "Segment base rate by salience band (sal-v4)" table renders 10 of 10 Terms; the Terms strictly before 2025 that carry data are 2017–2024 (2026 is empty). Pooling the bracketed `reached` rate × `n` across those eight rows: 484.4 weighted grants over 2810 weighted resolved = 0.17238. The in-code ten-Term lookback (2015–2024) is shortened by the pack's own coverage to the same eight Terms, so there is no window divergence to flag. `vote_accuracy` is omitted (cert stage; the empty vote list is not scored). No `semantic_grades` (no semantic set on a cert event). `claim_scores` and `process_version` are the harness's.

## What the prediction got right and wrong

Right: the label, and the direction and size of its move off the anchor. It pooled the anchor exactly as the contract specifies (17.24%, n = 2810, excluding the 2025 and 2026 rows, using the bracketed figure), then moved to 5% on three grounds that the record supports: the Wisconsin Supreme Court remanded for further proceedings and Gasper is unconvicted, so the BIO's 28 U.S.C. § 1257(a) objection (Cox Broadcasting, Florida v. Thomas) is a facial finality problem; the alternative-basis and good-faith arguments mean a win on the private-search question may change nothing; and the record on subjective expectation of privacy is contested. It correctly read the two distributions as a call-for-response cycle rather than repeated conference consideration, which is the reading the docket bears out (the Court denied at its first full look). The silent denial is consistent with its 8% conditional on separate writing.

Weaknesses, none large. The 5% number is aggressive relative to a conceded circuit split, a CFR after waiver, and an amicus with experienced Supreme Court counsel; a Justice inclined to reach the hash-match question could have read the Cox exceptions generously, and the candidate's own text concedes that upside. It relied on the filings' characterizations of the circuit decisions, since its verification attempts (one CourtListener lookup rate-limited, three web fetches with no usable content) failed, and it said so plainly. It did not retrieve anything beyond the record, so the widening of the split over the summer (which another candidate surfaced) was not in its information set; that did not hurt it here.

## Reasoning quality: 0.85

A complete, correctly anchored, candidly limited analysis whose main driver (finality) is the one the record most strongly supports and the one most consistent with a silent first-conference denial. Scored on soundness, not on the Brier: the number was well earned rather than lucky.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. The prediction was created 2026-09-16 from the 2026-09-15 snapshot, when the petition stood distributed for the 2026-09-28 conference, so the case was genuinely open; this was not a mis-provisioned decided case. Log: 31 calls, 28 collapsed to `other` (the engine's shell, reading the prompt, schemas, the provisioned record, and the statpack) and 3 `web-search` rows, all `unobserved`, so graded on their queries, which concern Florida v. Thomas only. No retrieved document dates; no query names this petition, its docket number, or its outcome. The only `data/qp-topics` mention in the log is a `find ... -not -path 'data/qp-topics/*'` exclusion, not a read. The candidate's `flags.json` is not staged, so its absence from view is weighed as the contract says: the `not_applicable` grade rests on the log and the reasoning, not on silence.

## Big case

My independent read is 0.45. The underlying question (whether an officer may open a hash-matched CyberTip file no human at the provider has viewed) is a genuine, respondent-conceded, six-circuit split governing a nationwide investigative pipeline, and a grant would have been a significant Fourth Amendment case. The vehicle was an interlocutory state criminal suppression ruling with a facial finality defect, one amicus, no CVSG, and a silent denial. Big issue, modest case. Disclosure: I printed the staged `prediction.json` files whole before writing, so the predictor's `big_case_score` was visible before I fixed my number; the read above is formed from the record.
