# Evaluation: codex-baseline

The cert disposition call was correct: denial, against the recorded denial on November 16, 2026. With P(any grant) = 0.44 and actual_granted = 0, the Brier score is 0.1936.

`reasoning_quality = 0.88` grades reasoning.md alone. The analysis distinguishes three pre-conference reschedules from the first true post-conference relist, interprets the frozen anchor on the proper prior-Term population, and avoids multiplying correlated marginal signal rates. It weighs the petition's concrete disagreements against Maryland's facial-challenge, vehicle and percolation objections. It also distinguishes Wolford's private-property holding and the separate cross-petition from the live sensitive-place dispute. The upward adjustment from the anchor is transparent but remains a judgment call rather than an empirically established effect. Denial cannot establish which cert-selection argument persuaded the Court; the grade rewards the analysis, not a supposed explanation in an unreasoned order.

## Predicted reasoning

`predicted_reasoning_quality = 0.45`. The central denial and no-CVSG calls held. The specific procedural forecast failed: there was no additional distribution after the baseline five, and the petition was denied immediately after the November 13 conference, earlier than the late-November/December window. The modal silent-denial forecast also failed because the docket records a Thomas statement. The document acknowledged a separate-writing possibility, which limits the size of that miss. Its conditional grant and merits discussion earns neither credit nor penalty because no grant occurred. This is a mixed forecast near the midpoint, with significant procedural misses. No statement text is staged, so its substantive content cannot be checked.

## Leakage

The harness records forward mode. The prediction and all logged calls precede the November 16 resolution. No logged query or reasoning passage shows this petition's disposition. The two unobserved web calls concern Wolford; their missing results are not evidence that the searches failed or returned nothing. Pre-existing precedent and the separate cross-petition are legitimate forward information. Assessment: retrieved_outcome_material false, influence not_applicable, leakage_suspected false.

## Record and base-rate provenance

Base-rate references were checked against the candidates' shared recorded statpack, recovered with `fedcourts statpack-at`: build `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`. This differs from the current committed pack. Its prior-Term high-band rows reproduce the frozen anchor, and its relist, CVSG and amicus figures support the historical references. The segment base rate and skill are left for the harness to stamp; no independent baseline is supplied here. This is a cert cell: individual votes and semantic claims are not scored, and mechanical claims are left entirely to the harness.
