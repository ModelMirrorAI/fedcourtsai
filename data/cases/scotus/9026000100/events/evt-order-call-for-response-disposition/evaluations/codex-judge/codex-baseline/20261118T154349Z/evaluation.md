# Evaluation: codex-baseline

The prediction correctly called denial. With P(grant) = 0.12 and actual_granted = 0, `correct = 1` and `brier_score = 0.0144`.

Reasoning quality is **0.92**. The rationale separates a response request from four votes to grant, uses the appropriate prior-Term risk-set population, and treats terminal relist, CVSG, and amicus statistics as descriptive context rather than independent transition rates. Its quoted historical figures agree with the reconstructed build. The legal analysis weighs genuine interest in the issue against an unpublished decision, disputed evidence, comparator differences, and the unpleaded accommodation claim. Those distinctions are supported by the petition's appended appellate memorandum and district court order (Appendices A and B, especially 18a–25a). It also separates allegations from judicial findings and correctly limits what the earlier separate opinions establish. The upward adjustment remains a qualitative judgment without a response-request-conditioned empirical table; one denial cannot establish calibration. The lower probability forecasts' better realized scores do not by themselves make this rationale unsound.

## Predicted reasoning

Forecast quality is **0.88**. The central denial, response-before-disposition route, further-distribution range, year-end timing, and absence of a CVSG were borne out. In particular, one further distribution set the November 13 conference, followed by the November 16 denial. This is more specific than a bare denial forecast, although its distribution range is fairly broad and redistribution itself was largely implied by the response request. The outcome explicitly records no noted dissent. The wider prediction of no separate writing remains unresolved because writing roles and order text are unavailable, and the grant-only question and route were never tested. Those unresolved claims earn neither credit nor penalty. The denial does not reveal the Court's internal reasons.

## Retrieval integrity and stakes

The forward prediction preceded resolution. The 52-call harness log shows 46 captured calls and six unobserved web calls. I assess the latter by their earlier-authority queries, without inferring that they returned no material. The visible calls and rationale disclose no retrieval or use of this petition's disposition. `influenced_prediction = not_applicable` and `leakage_suspected = false`.

My significance read is **0.40**: the proposed change to national employment-discrimination procedure is consequential, while this individual unpublished vehicle and eventual denial have limited precedential reach.

This is a cert-stage response-requested cell. Correctness compares the disposition labels, and the Brier score uses the recorded binary grant outcome of 0. Votes are not scored on this stage; no semantic grade set is declared. The harness owns the stamped segment base rate, its basis, skill, and quantitative claim scores, which I have not supplied.

Base-rate use was checked against the prediction-time statpack reconstructed by `fedcourts statpack-at`: build `7bcde3b105cb212283905eda17b827efc188e80c`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, landed October 28, 2026. All three reconstructions selected this same build with no alternative. This historical build, rather than today's committed pack, governs my assessment of quoted figures; it does not replace the harness's stamped segment base rate.
