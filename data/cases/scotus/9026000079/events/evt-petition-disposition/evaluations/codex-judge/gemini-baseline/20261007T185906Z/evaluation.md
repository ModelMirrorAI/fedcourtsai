# Evaluation of gemini-baseline

## Outcome and scores

This is a cert-stage distribution event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline predicted `denied` with P(any grant) = 0.002. Thus exact-label correctness is 1 and Brier loss is `(0.002 - 0)^2 = 0.000004`.

## Baseline

The prediction freezes Term 2026, band `baseline`, and version `sal-v4`. The committed statpack's band-table heading matches that version. I use the bracketed baseline `reached` rates for every displayed prior Term, 2017–2025, excluding 2026. Rates and weighted resolved denominators are: 2025, 3.9%/1140; 2024, 5.7%/1271; 2023, 5.9%/1312; 2022, 5.8%/1192; 2021, 5.6%/1500; 2020, 4.5%/1739; 2019, 4.6%/1399; 2018, 4.6%/1524; 2017, 4.7%/1643.

The weighted numerator reconstructed from those rounded percentages is 637.385, over a weighted denominator of 12,720, giving 0.05010888364779874. This is an approximate, denial-reweighted paid-segment risk-set baseline, not an exact count of grants or a freshly queried corpus estimate. The table renders 10 of 10 Terms; there is no rendered-window truncation. The consulted markdown supplies no corpus-refresh timestamp, so these figures describe that committed artifact only. I do not substitute the evaluator's terminal context. Skill is `1 - 0.000004 / baseline^2 = 0.9984069458565274`; this favorable single-event score is not evidence of calibrated near-certainty.

## Reasoning quality: 0.50

The rationale identifies the government response waiver and lack of visible escalation as relevant negative signals. It recognizes the baseline risk-set rate and reaches the correct modal disposition without pretending to possess petition text.

However, the move from roughly 5% to 0.2% is insufficiently supported. The zero-relist table describes a terminal population, not the future prospects of a petition that has not yet relisted. Its 1.2% figure also excludes the separately reported 0.5% GVR share, although the headline probability includes any grant. Treating those numbers as a reason for near-zero odds mixes populations and axes. The further inference that paper-only filing or unavailable documents indicates a routine or idiosyncratic petition is unsupported: an evidence-access limitation does not establish weak substantive merits. The categorical CVSG assertion is stronger than necessary to support a low grant forecast. The realized denial does not validate those analytical shortcuts or reveal the Court's reasons.

This grade concerns `reasoning.md` only. The forecast document was read for context; neither it nor the structured claims was separately scored or folded into the quality grade. Cert votes and semantic grades are not scored.

## Leakage

The captured mode is forward. All 26 calls occurred on October 4, before the October 5 resolution. Their queries concern local inputs, the statpack, schemas, and production/validation; none seeks an already-issued disposition. The prose treats denial as a forecast. Every result is unobserved, so I cannot verify returned contents from this transcript and do not treat null result dates or digests as proof of no retrieval. On the available timing, query, and reasoning evidence, no outcome material is shown and there is no indication of a decided case provisioned forward: `retrieved_outcome_material = false`, influence `not_applicable`, suspicion false.
