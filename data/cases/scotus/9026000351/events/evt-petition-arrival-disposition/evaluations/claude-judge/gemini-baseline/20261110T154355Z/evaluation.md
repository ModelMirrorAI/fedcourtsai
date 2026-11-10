# Evaluation — gemini-baseline

**Cell:** scotus/9026000351 (No. 26-351, Dreiling v. United States), `evt-petition-arrival-disposition`, stage `cert`, arrival moment. **Outcome:** denied (Nov 9, 2026) after an SG waiver (Oct 16) and a single distribution for the Nov 6 conference; no CVSG, no noted dissent. The segment base rate and skill score are the harness's to stamp from the frozen `baseline` band (sal-v4); this write-up quotes no rate of its own. No semantic set on a cert cell; no votes scored.

## Score
Predicted **denied** at P(grant) = 0.001 → `correct` = 1, Brier = 0.000001.

## Reasoning quality (0.50)
The conclusion is right and the main vehicle points are named: a pro se collateral attack by a third-party litigant on the Newman suspension, and an idiosyncratic Tucker Act/§ 354 theory. But the analysis is thin and mostly assertion. It never engages the decisive concession that the constitutional question was not decided below, the money-mandating doctrine, or the prior mandamus denial. "Pro se petitions of this nature have a negligible chance" is stated rather than supported. The base-rate description ("preceding 10 Terms") does not match the nine displayed Terms whose counts it quotes. The drop from about 5% to 0.1% is reasonable in direction but is not argued for at that size.

## Predicted reasoning (0.68)
Central claims: an SG waiver leading to a swift denial; a single distribution and no relists; no CVSG; no dissent or statement. All held (waiver Oct 16, one distribution for Nov 6, denied Nov 9). The waiver call is a modest specific commitment. The rest is the standard forecast for this kind of petition, with no timing given. Its claim that a grant would require reaching QP 1 depends on a grant that never happened, so it earns neither credit nor penalty, although it sits uneasily with the concession that QP 1 was not decided below.

## Leakage
Forward cell (cutoff 2026-09-17). Its log shows only provisioned inputs and the committed statpack, with no web, MCP or corpus retrieval. Result-capture coverage is 0.0 (a standing engine shape), but every call is a local file read or write whose command is visible. `influenced_prediction` = not_applicable.
