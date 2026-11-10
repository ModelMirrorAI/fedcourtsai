# Evaluation — claude-baseline

**Cell:** scotus/9026000351 (No. 26-351, Dreiling v. United States), `evt-petition-arrival-disposition`, stage `cert`, arrival moment. **Outcome:** denied (Nov 9, 2026) after an SG waiver (Oct 16) and a single distribution for the Nov 6 conference; no CVSG, no noted dissent. The segment base rate and skill score are the harness's to stamp from the frozen `baseline` band (sal-v4); this write-up quotes no rate of its own. No semantic set on a cert cell; no votes scored.

## Score
Predicted **denied** at P(grant) = 0.005 → `correct` = 1, Brier = 0.000025.

## Reasoning quality (0.82)
Sound and well-grounded. It reads the posture correctly: a nonprecedential summary affirmance, a lead constitutional question conceded as undecided below, a request to overrule *United States v. Jones*-line money-mandating doctrine with no split, and a prior mandamus denial on the recusal theory. It anchors on the baseline-band reached rate and moves well below it with reasons stated, and it checks the Federal Circuit originating-court cut. It also confirms the petitioner's lower-court history through RECAP. Deductions: it read only about the first half of the petition (to its credit, it says so). "Pro se paid petitions of this shape are granted at a rate well under one percent" is asserted without a cited figure. "A CVSG cannot issue" overstates a strong practical point.

## Predicted reasoning (0.80)
Central claims: denial at the first conference with no GVR or summary route; an SG waiver; exactly one distribution, for an early-to-mid November conference; no CVSG and no dissent. All are borne out by the docket: waiver Oct 16, distributed Oct 21 for the Nov 6 conference, denied Nov 9. The waiver and conference-window calls are specific commitments a reader could have got wrong, which lifts the document above the generic denial forecast. The companion-petition (No. 26-9) claim is unresolved on this record. Its account of which question presented the Court would take only applies if cert were granted, so it earns neither credit nor penalty.

## Leakage
Forward cell (cutoff 2026-09-17). CourtListener searches for the petitioner returned only lower-court RECAP dockets, the latest filed 2025-12-17, plus empty SCOTUS results. One corpus query returned unrelated interim applications. One shell call listed predictions on *other* dockets' arrival events, which looks like a format check and concerns no outcome of this case. No outcome material for this petition. `influenced_prediction` = not_applicable.
