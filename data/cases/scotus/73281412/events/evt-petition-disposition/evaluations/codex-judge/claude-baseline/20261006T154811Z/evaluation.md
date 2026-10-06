# Evaluation of claude-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline predicted `denied` with P(any grant) = 0.10: `correct = 1` and Brier = `(0.10 - 0)^2 = 0.01`.

The prediction froze Term 2025, band `elevated`, and salience version `sal-v4`. That version matches the heading in the committed `metrics/statpack.md`. I use the bracketed **reached** rates, not terminal-band rates and not the evaluator's decided-docket context. Every displayed strictly-prior Term contributes:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

The resolved-weighted pool is 484.386 / 2,810 = **0.17237935943060498**, using the published rounded percentages; 484.386 is the weighted rate numerator, not an exact count of grants. The table renders all ten of its ten Terms; 2025 and 2026 are excluded. `base_rate_basis = risk_set`; skill is `1 - 0.01 / 0.17237935943060498^2 = 0.6634655912806073`. This uses the committed table, not a live corpus estimate. A positive score describes this one realized denial, not demonstrated calibration across cases.

## Reasoning quality: 0.84

The rationale is substantial and case-specific. It distinguishes a response-request redistribution from a genuine post-consideration relist, anchors on the correct frozen risk set, and explains the downward adjustment through the disputed framing of the questions and defendant-specific vehicle obstacles. It gives counterweight to the requested response, lower-court dissent, severe alleged conditions, and potential summary correction. Its acknowledgment that the September snapshot contained an older payload appropriately limits inferences from an absent reply.

The main weaknesses are overconfidence in adopting respondents' descriptions of unchallenged or independently dispositive grounds, and somewhat speculative reliance on counsel profile, typographical quality, and how most Justices would react to the false suicide report. The provisioned opposition supports the existence of those vehicle arguments, but advocacy is not an adjudication of them. The rationale correctly says qualified immunity and municipal liability remained unresolved below, yet should distinguish those possible remand obstacles more sharply from grounds already decided. The response-request adjustment is candidly judgmental rather than backed by a published conditional rate.

The denial is consistent with the forecast, but the outcome supplies no explanation establishing that these considerations caused it. The score evaluates the soundness of `reasoning.md`, not hindsight agreement alone.

## Leakage assessment

The harness log identifies forward mode, with 28 of 28 call results captured. Its September 17 timestamps precede the October 5 resolution. Case-specific docket queries sought an unresolved petition; the retrieval note reports a null termination date and no docket-entry text. Earlier appellate decisions are legitimate forward inputs. The broad corpus query concerned other granted matters, and the rationale says it did not inform the number. A logged read of another prediction's tooling file does not itself demonstrate retrieval of this case's disposition.

No logged query, extracted document date, or passage of reasoning affirmatively reveals this petition's denial before prediction. Digests do not expose complete response text, and missing document dates are not evidence that a response was empty. On the available timing, queries, and prose, `retrieved_outcome_material = false`, influence is `not_applicable`, and leakage is not suspected.

## Scope

I read the forecast document for context only. Its forecast and the quantitative claims are not included in reasoning quality; mechanical claim scores belong to the harness. Cert votes are not scored, and no semantic grades apply. I omit the optional stakes assessment because I did not establish an independent score before seeing the candidate's score.
