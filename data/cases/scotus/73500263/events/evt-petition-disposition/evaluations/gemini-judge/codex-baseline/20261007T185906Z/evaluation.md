# Evaluation of codex-baseline

This is a cert-stage prediction for a petition that was ultimately denied.
The prediction assigned a probability of 0.012 to a grant, correctly forecasting the denial.

## Base Rate and Skill
The candidate accurately anchored on the `baseline` band for OT2025 using `sal-v4`. By pooling the `reached` rate for the `baseline` band over Terms strictly prior to OT2025 (OT2017-OT2024), the baseline rate is approximately 5.12% (`segment_base_rate` = 0.0512). The forecast of 0.012 yields an excellent Brier score of 0.000144 and a high skill score.

## Reasoning Quality
The reasoning quality is very high (0.9). The predictor read the Fourth Circuit opinion and correctly identified that the lower court's actual holding did not present the Chenery problem claimed by the petition. It observed the lack of a response (a waived response) and correctly noted preservation issues that made it a poor vehicle, confidently dropping the probability below the anchored base rate.

## Leakage
The prediction was made in `forward` mode. The retrieval log confirms only searches for the lower court opinion and Court rules, with no leakage of the eventual disposition.
