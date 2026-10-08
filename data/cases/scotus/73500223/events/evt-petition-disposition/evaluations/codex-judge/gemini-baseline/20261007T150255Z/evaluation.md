# Evaluation: gemini-baseline

## Outcome and quantitative scores

The event is cert-stage and the outcome records denial on October 5, 2026, with `actual_granted = 0`. The provisioned October 5 snapshot likewise lists the denial. gemini-baseline forecast `denied`, so `correct = 1`; the grant probability 0.03 yields `(0.03 - 0)^2 = 0.0009`.

The prediction freezes band `baseline`, version `sal-v4`, and Term 2025. The committed statpack's sal-v4 heading matches. The risk-set baseline pools the bracketed reached percentages and their weighted resolved counts for all displayed Terms strictly preceding 2025: 2017 (4.7%, 1643), 2018 (4.6%, 1524), 2019 (4.6%, 1399), 2020 (4.5%, 1739), 2021 (5.6%, 1500), 2022 (5.8%, 1192), 2023 (5.9%, 1312), and 2024 (5.7%, 1271). The sum of weighted denominators is 11,580. The resulting rate is 0.05120250431778929, calculated from the rounded printed percentages, and `base_rate_basis = risk_set`.

Skill is `1 - 0.0009 / 0.05120250431778929^2 = 0.6567108291485383`. The lower grant probability beats the baseline on this realized denial. That favorable one-event score is distinct from whether the rationale justified the probability well, and is not evidence of aggregate calibration.

The table displays ten of ten pack Terms, of which eight precede this case's docket Term. The outcome's calendar date does not move the baseline to a later Term, and the evaluator's terminal context does not replace the prediction's frozen band. These are historical, denial-reweighted estimates in the supplied committed pack, not a live corpus measurement; no refreshed corpus vintage is asserted.

## Reasoning quality: 0.52

The short rationale correctly recognizes the first distribution, baseline band, low prior-Term reached rate, constitutional overruling request and lack of an obvious federal-government interest. It is coherent about denial being the modal outcome and does not claim that the merits must fail simply because certiorari is unlikely.

Its decisive downward adjustment is weakly justified. Having no relist before the first scheduled conference is not an observed failure to attract further consideration. Rarity of an immediate first-distribution grant does not, without an additional transition model, establish a correspondingly low probability of ultimate grant: the petition can still be relisted. The rationale acknowledges that possibility but supplies no empirical or case-specific basis for the size of its downward adjustment below the approximately 5.1% reached baseline. This risks substituting terminal or immediate procedural frequencies for the unresolved event's probability.

The analysis also omits the most concrete vehicle issues developed in the supplied opposition: preliminary-injunction posture, undeveloped record, lack of an established federal split, and the subsequent-precedent distinctions that the parties dispute. Merely identifying a challenge to PruneYard from a state court does not examine those competing arguments. The deduction is for missing analytical support, not for brevity alone, lack of external tool use, or an incorrect outcome label. Its excellent Brier result on this denial does not supply the missing reasoning.

Only `reasoning.md` is qualitatively graded. The forecast document and the claims receive no separate qualitative score, and their accuracy does not enter this rating. The denial supplies no statement of the Court's actual reasons.

## Leakage and scoring scope

The captured query transcript identifies a September 17 forward run, before the September 28 conference and October 5 denial. All 27 call results are marked `unobserved`, with coverage 0.0. That is a telemetry limitation, not proof that the calls returned nothing and not itself a defect to flag. Query scopes are confined to provisioned inputs, statpack, schemas and writing or checking outputs; the prose discusses a pending conference rather than a known disposition. There is no positive evidence that a decided case was provisioned forward or that this petition's disposition was retrieved. Accordingly, outcome-material retrieval is false on the visible record, influence is `not_applicable`, and suspected leakage is false. This assessment does not claim to inspect the unobserved results or infer anything from the unstaged flags.

Vote accuracy is omitted because this is cert-stage. There is no semantic grading set, quantitative claim scores remain the harness's, and no independent big-case score is supplied.
