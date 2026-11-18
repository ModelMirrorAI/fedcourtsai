# Evaluation of `gemini-baseline` — *Jack Rabbit, LLC v. Visa Inc., et al.* (`scotus/9026000420`, `evt-petition-disposition`)

## Quantitative Summary

- **Stage:** `cert` (`moment: distribution`)
- **Predicted / Actual Disposition:** `denied` / `denied` (`correct = 1`)
- **Predicted Grant Probability:** `0.01` vs. `actual_granted = 0` (`brier_score = 0.0001`), achieving the lowest (best) Brier score in the cohort and substantially outperforming the stamped segment base rate.
- **Semantic Grades:** Omitted (`cert` stage declares no semantic claim set).

## Reasoning Quality (`reasoning.md`) — `0.78`

`gemini-baseline` combined the deepest substantive legal analysis of the lower-court record in the cohort with a surprising set of concrete factual misstatements about the Supreme Court docket entries in Section 1 of `reasoning.md`:

1. **Strengths — doctrinal depth, record mastery, and probability calibration:**
   - `gemini-baseline` delivered an incisive five-part vehicle critique grounded in the full lower-court record: (a) the Second Circuit decided Jack Rabbit's appeal (`No. 24-1808(CON)`) in a non-precedential summary order that did not mention or pass upon Jack Rabbit's Article III, Rule 23, or Clayton Act § 4 arguments; (b) Jack Rabbit was a collateral gasoline-retailer objector that was not even a party to the companion published appeal in *Old Jericho Enterprise, Inc. v. Visa Inc.*, 175 F.4th 172 (2d Cir. 2026) (`Pet. App. 28a n.4`); (c) class certification and settlement approval became final after *Fikes Wholesale, Inc. v. Visa U.S.A., Inc.*, 62 F.4th 704 (2d Cir. 2023), foreclosing collateral attack on the 2019 certification order; (d) Judge Brodie's May 28, 2024 order (`735 F. Supp. 3d 249`) resolved a motion by Visa and Mastercard to enforce the 2019 release against Square, Intuit, and the *Lanning* plaintiffs under New York contract law; and (e) under *Lexmark International, Inc. v. Static Control Components, Inc.*, 572 U.S. 118, 128 n.4 (2014), *Illinois Brick* direct-purchaser status goes to statutory merits under Clayton Act § 4 rather than Article III jurisdiction, and settling parties are entitled to compromise disputed statutory defenses without litigating them to judgment during claims administration.
   - `gemini-baseline` also checked *Sunoco* (`No. 26-1`, denied Oct. 5, 2026), *Pickett* (`No. 25-677`, pending), *Takeda* (`No. 25-625`, denied Mar. 23, 2026), and *Labcorp* (`No. 24-304`, DIG'd June 5, 2025), and decomposed `P(grant) = 0.01` cleanly (`P(CFR/relist) = 0.04` × `P(grant | CFR/relist) = 0.25`).
   - Against its placement statpack build (`dedb32b153e6`, digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, reconstructed via `fedcourts statpack-at`), `gemini-baseline`'s cited counts for `relist_bucket = 0` (`1.8%` over `n=10,204`), `cert_amicus = 0` (`3.8%` over `n=11,109`), `cvsg = none` (`6.4%` over `n=13,549`), and `ca2` (`4.9%` over `n=2,101`) match exactly.
2. **Factual errors on the Supreme Court docket and minor slips docking the score:**
   - In Section 1 of `reasoning.md`, `gemini-baseline` stated that `record/snapshots/2026-10-31.json` showed *"all three respondents—Mastercard Incorporated (Oct. 21, 2026), Visa Inc. (Oct. 26, 2026), and the Rule 23(b)(3) Class Plaintiffs (Oct. 26, 2026)—waived their right to respond."* In fact, the Supreme Court docket (`2026-11-16.json`) lists **only two respondents**—Visa Inc. and Mastercard Incorporated—who filed waivers on **October 16, 2026** and **October 19, 2026**, respectively. There is no respondent entry or waiver for "the Rule 23(b)(3) Class Plaintiffs" on the docket (`October 26, 2026` was simply the original response due date printed in the September 22 petition-filing entry).
   - Three smaller inaccuracies appear in `reasoning.md`: (1) quoting `response_requested: false` from `context.json` when `context.json` stores `response_requested: null`; (2) reporting the `sal-v6` baseline terminal range across `OT2017–OT2025` as `1.3%–2.0%`, overlooking `OT2017`'s `0.7%` (`n=1,343`) in build `dedb32b153e6`; and (3) assigning tied highest `order-writers` weight (`0.004`) to Justice Alito despite Justice Alito's standard recusal in Visa/Mastercard cases.
   - Because inventing a third respondent waiver and misstating both actual waiver dates are concrete factual errors about the staged Supreme Court docket, `reasoning_quality` is docked from the top tier to **`0.78`**.

## Predicted reasoning (`predicted_reasoning.md`) — `0.83`

`predicted_reasoning.md` committed specifically to five central claims (four unconditional, one conditional on grant):

1. **Denial on the first conference without calling for a response or relisting (`relist-increment: 0.04`)** (`borne-out`): Confirmed by `signals.distribution_count = 1` and `2026-11-16.json`.
2. **No CVSG invitation (`cvsg-increment: 0.005`)** (`borne-out`): Confirmed by `signals.cvsg_date = null`.
3. **Summary denial without comment at the November 13, 2026 Conference on the Order List of November 16, 2026 (`disposition: 0.01 — denied`)** (`borne-out`): Exact match to `outcome.json` (`denied`, `resolved_at: "2026-11-16"`) and `2026-11-16.json`.
4. **If granted, plenary review (85% vs. 15% summary route) limited to QP 1, likely ending in affirmance or DIG given *Fikes* finality and *Lexmark*** (`unresolved`): Untested given the denial; neither credited nor penalized.
5. **No dissent or statement respecting denial (`dissent-from-denial: 0.015`, naming Thomas, Alito, or Gorsuch as most plausible separate writers)** (`borne-out`): Confirmed by `noted_dissent_from_denial = false` and the absence of any separate writing.

Under the forecast-document rubric (*"Grade the thrust, not the margins... A minor detail wrong in a forecast whose central claims held costs little"*), `gemini-baseline` earns **`0.83`**: every testable central claim—including the exact conference date, exact November 16, 2026 Order List date, absence of CFR/relist/hold, absence of CVSG, and silent summary denial—was specific and borne out, with a modest deduction for two marginal inaccuracies inside `predicted_reasoning.md` itself (repeating the non-existent third waiver by "the Rule 23(b)(3) Class Plaintiffs" in Section 1, and naming Justice Alito in Section 3 as a plausible separate writer when Justice Alito took no part in the consideration or decision of the petition).

## Big-Case Read & Leakage Check

- **Evaluator `big_case` read (`0.15`):** Notwithstanding the $5.6 billion MDL settlement fund, this solo-objector petition from an unpublished contract-interpretation summary order drew respondent waivers, zero amici, no CFR, and a routine first-conference summary denial without dissent. (`gemini-baseline`'s `0.55` explicitly weighted conditional merits stakes heavily despite recognizing the vehicle flaws.)
- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction (`run_id: 20261031T173439Z`) run 16 days before the November 16, 2026 order. All 50 logged calls in `retrieval_log.json` (`result_capture_coverage: 0.0`, `outcome_only` capture normal for this engine adapter) were pre-outcome local reads, statpack reads, corpus queries on related dockets, and CourtListener searches of prior lower-court/SCOTUS history.
