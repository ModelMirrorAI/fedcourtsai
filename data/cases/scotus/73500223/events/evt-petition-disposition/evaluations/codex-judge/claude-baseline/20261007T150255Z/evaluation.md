# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage event. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`; the October 5 snapshot independently lists "Petition DENIED." claude-baseline's September 17 prediction names `denied`, so `correct = 1`. Its 0.10 grant probability gives `(0.10 - 0)^2 = 0.0100`.

The baseline uses the prediction's frozen `baseline` band, `sal-v4` version and docket Term 2025, not the evaluator's decided-docket context or the Term in which denial occurred. The committed statpack heading matches `sal-v4`. Pooling the bracketed reached rates over every rendered strictly-prior Term gives:

| Term | Reached grant rate | Weighted resolved n |
| --- | --- | --- |
| 2017 | 4.7% | 1643 |
| 2018 | 4.6% | 1524 |
| 2019 | 4.6% | 1399 |
| 2020 | 4.5% | 1739 |
| 2021 | 5.6% | 1500 |
| 2022 | 5.8% | 1192 |
| 2023 | 5.9% | 1312 |
| 2024 | 5.7% | 1271 |

The denominator is 11,580; the resolved-weighted rate from these rounded printed percentages is 0.05120250431778929. Thus `base_rate_basis = risk_set` and skill is `1 - 0.01 / 0.05120250431778929^2 = -2.8143241205717966`. The prediction correctly named denial but assigned more grant probability than this baseline, producing a worse Brier score on this one outcome. This is not an aggregate performance claim.

The table renders all ten of the pack's ten Terms, with eight preceding this case's Term; there is no hidden-window divergence to flag. These are the supplied committed pack's historical, denial-reweighted estimates, not a refreshed corpus measurement. No live corpus vintage is asserted.

## Reasoning quality: 0.84

The rationale provides substantial, case-specific analysis rather than merely selecting the common outcome. It identifies the preliminary-injunction posture and undeveloped record, distinguishes state constitutional variation from a demonstrated federal split, and confronts the opposition's argument that Cedar Point and Moody distinguish rather than discard PruneYard. Those considerations are supported by the provisioned opposition, especially its introduction and vehicle discussion. It also articulates why a substantial overruling request, organized amicus interest and counsel experience might move the forecast above the band rate. The matched risk-set anchor and explicit acknowledgment that the uplift is judgmental are strengths.

The principal limitations are evidentiary and calibrational. The asserted counsel grant advantage has no denominator or estimated effect; the rationale's prior cert-denial examples are expressly unverified memories. Describing the interlocutory problem as one the reply cannot argue away is stronger than the supplied analysis establishes: preliminary posture is a substantial vehicle concern, not by itself a demonstrated categorical jurisdictional bar. The rationale's inference of supportive amicus weight also exceeds what the docket's filing titles alone establish. These limitations warrant a deduction without treating the eventual denial as proof that the 10% forecast was irrational.

The quality score evaluates only `reasoning.md`. The forecast document was read for context, not separately graded or folded into this score. The outcome supplies no explanation of why certiorari was denied, so the asserted screening considerations remain plausible ex ante reasons, not findings about the Court's actual motivation.

## Leakage and scoring scope

The log identifies a forward run on September 17, before the September 28 conference and October 5 disposition. All 33 logged calls have captured results. The three CourtListener searches have captured throttled status, including the request for this case's live docket; that request was permissible while the event remained open. The corpus requests seek general grants and an older precedent, not a known denial in this petition. The prose and query record show no already-decided disposition. I record outcome-material retrieval as false, influence as `not_applicable`, and suspected leakage as false. This conclusion rests on chronology and the logged queries as well as the rationale, not merely on absence of a disclosure; the candidate's flags were not staged.

Cert votes are not scored. No semantic set is declared for this stage. Quantitative claims and their score block are left to the harness, and no independent big-case score is supplied.
