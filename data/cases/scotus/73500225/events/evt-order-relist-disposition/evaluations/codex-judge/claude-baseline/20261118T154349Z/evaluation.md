# Evaluation: claude-baseline

The cert disposition call was correct: denial, against the recorded denial on November 16, 2026. With P(any grant) = 0.36 and actual_granted = 0, the Brier score is 0.1296.

`reasoning_quality = 0.80` grades reasoning.md alone. It correctly separates the three reschedules from the genuine relist, uses the frozen anchor rather than the whole docket, and balances post-Bruen salience against percolation and the broad facial vehicle. It treats Wolford as an already-issued but narrower decision, explains why a GVR remains possible, and also recognizes that relists may precede a separate writing rather than a grant. Its reference to reversal concerning alcohol and demonstrations describes reversal of the district court; the petition appendix confirms that the Fourth Circuit thereby upheld those bans.

The analysis is less developed on the competing location-specific splits and the historical-analogy arguments than on docket posture. Its movement from the anchor to the final probability is mostly qualitative, and its additional-relist estimate rests on analogies without a measured conditional frequency. These limit the analysis's precision without making the denial reasoning unsound. The denial order supplies no reason from which to establish that the Court actually preferred more percolation.

## Predicted reasoning

`predicted_reasoning_quality = 0.65`. The forecast correctly chose denial, no CVSG, and a separate writing with Thomas as the likeliest author. The docket identifies a statement respecting denial rather than expressly labeling it a dissent, so credit attaches to the separate-writing and author forecast. Possible joinders and the statement's substance remain unresolved because no writing text is staged. The central prediction of several more relists and waiting for Koons failed: the next scheduled conference produced the November 16 denial without another distribution. That procedural commitment keeps the grade below the mostly-borne-out anchor. Conditional grant and merits discussion earns neither credit nor penalty.

## Leakage

The harness records forward mode and captures all 20 calls. The direct live-docket fetch and own-case search occurred on November 9, a week before resolution, and are permissible forward retrieval. The reasoning and retrieval note report an open docket through the baseline's November 9 distribution; neither reveals the subsequent denial. Related-case information does not reveal this petition's result. Assessment: retrieved_outcome_material false, influence not_applicable, leakage_suspected false.

## Record and base-rate provenance

Base-rate references were checked against the candidates' shared recorded statpack, recovered with `fedcourts statpack-at`: build `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`. This differs from the current committed pack. Its prior-Term high-band rows reproduce the frozen anchor, and its relist, CVSG and amicus figures support the historical references. The segment base rate and skill are left for the harness to stamp; no independent baseline is supplied here. This is a cert cell: individual votes and semantic claims are not scored, and mechanical claims are left entirely to the harness.
