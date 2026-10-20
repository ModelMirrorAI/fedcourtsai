# Evaluation of `claude-baseline` — `scotus/9026000005` (`evt-petition-disposition`)

## Outcome & Quantitative Summary

- **Stage:** `cert` (frozen `context.band`: `elevated`, `sal-v4`; segment base rate and Brier skill score are harness-stamped against the stamped segment base rate).
- **Predicted vs. Actual Disposition:** Predicted `denied` (`P(grant) = 0.08`) vs. actual `denied` (`actual_granted = 0`, resolved October 19, 2026, with no noted dissent from denial and `distribution_count = 2`).
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.0064`, substantially outperforming the stamped segment base rate.

## Reasoning Quality (`0.94`)

`claude-baseline` delivered an analytical, well-verified rationale in `reasoning.md`:

1. **Direct Verification of Controlling Intervening Precedent:** Rather than relying solely on the Solicitor General's adversarial summary in the Brief in Opposition, `claude-baseline` retrieved the opinion text of *Trump v. Slaughter* (decided June 29, 2026) via CourtListener MCP. It accurately identified that *Slaughter* overruled *Humphrey's Executor*, held that enforcing federal statutes through in-house adjudication "is executive," cited the *Wilcox* district court decision as an illustration of *Humphrey's Executor*'s indeterminacy, and reserved only non-Article III courts (such as the Tax Court and Court of Federal Claims) and Federal Reserve-lineage entities.
2. **Sharp Analysis of Companion Case and Procedural Posture:** `claude-baseline` properly weighed the June 30, 2026 cert denial in *Harris v. Bessent* (No. 25-1110), the consolidated D.C. Circuit companion case concerning the MSPB, and explained why petitioner's fallback request for a GVR failed under *Lawrence v. Chater* because the D.C. Circuit had already ruled for the government in harmony with *Slaughter*.
3. **Accurate Reading of Distribution History:** `claude-baseline` recognized that the docket's two distribution entries (August 5 for the September 28 conference, followed by an August 13 response request, the September 14 BIO, and a September 30 redistribution for the October 16 conference) meant the petition was heading to its first post-BIO conference rather than having been relisted out of conference.
4. **Calibration:** `claude-baseline`'s upward adjustments above the floor—accounting for the August 13 call for a response, the narrow non-Article III court reservation in *Slaughter*, and the SG's alternative invitation to grant and summarily affirm—were clearly reasoned, though `0.08` was slightly conservative given the decisive force of *Slaughter* and the *Harris* denial.

## Leakage Assessment

- **Mode:** `forward` (`2026-09-30`, before the October 16, 2026 conference and October 19, 2026 denial).
- **Findings:** `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The retrieval log (`result_capture_coverage = 1.0`) shows reads of the provisioned `2026-09-30` snapshot and case filings, committed statpack, two historical corpus queries, and CourtListener MCP lookups of *Trump v. Slaughter* (`2026-06-29`) and *Harris v. Bessent*. All consulted material predated the prediction run and the event's resolution.
