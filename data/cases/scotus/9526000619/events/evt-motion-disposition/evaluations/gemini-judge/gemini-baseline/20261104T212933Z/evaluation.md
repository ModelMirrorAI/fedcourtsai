# Evaluation of `gemini-baseline` (`scotus/9526000619` / `evt-motion-disposition`)

## Stage, Outcome, and Harness-Stamped Fields

This is an **interim-stage** arrival cell (`stage: interim`, `moment: arrival`) scoring Application No. 26A619 (*Denise Smith v. Brown, Savage, Britto, Stitely & Callahan, LLP, et al.*), submitted to Chief Justice Roberts on October 27, 2026, and docketed October 30, 2026. On November 3, 2026, the Chief Justice summarily denied the application in chambers (`actual_disposition: "denied"`, `actual_granted: 0`, `interim_reading: "denied"`, `interim_granted: 0`), with no response requested (`response_requested: false`), no referral to the full Court (`referred_to_court: false`), zero amicus briefs (`amicus_briefs: 0`), and no separate writings (`writing_roles: null`).

`gemini-baseline` predicted `predicted_disposition: "denied"` (`granted: 0`) with `probability: 0.002`. Scored against `outcome.interim_granted = 0`, `correct = 1` and `brier_score = 0.000004`.

Because this is an interim cell, `segment_base_rate`, `brier_skill_score`, and `claim_scores` are computed and stamped by the harness (`stamp-cell`), and `base_rate_basis` is left `null`. Where the stamped segment base rate comes back `null` under the finer interim reading, that refusal reflects the committed `metrics/statpack.json` counts over the strictly-prior ten-Term lookback window (`OT2016`–`OT2025`): every Term in that window currently records `finer_resolved: 0` (`0 < 50`, below the pre-registered `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor) and non-zero `finer_unread` (`1,366` unread substantive applications across `OT2016`–`OT2025`, plus `16` unparsed).

## Reasoning Quality (`reasoning_quality`: 0.96)

`gemini-baseline`'s analysis in `reasoning.md` is exemplary:

- **Pre-cutoff factual reconstruction despite a blank staged PDF:** When the prediction cells ran against the `2026-10-28` snapshot, `record/documents/application.txt` had `empty_text: true` (`ocr_derived: false`). Rather than stopping at the caption, `gemini-baseline` searched CourtListener RECAP for the parties (`Denise Smith` and `Brown, Savage, Britto, Stitely & Callahan`) and retrieved Chief Magistrate Judge Timothy J. Sullivan's October 5, 2026 Memorandum Opinion in *Denise R. Smith v. Nationstar Mortgage LLC, et al.*, No. 8:25-cv-02817-TJS (D. Md.) (`recap_document_id: 496317114`). That pre-cutoff federal opinion laid out the entire procedural history behind Supreme Court of Maryland Petition No. 119—the 2018 foreclosure sale of 917 Jennings Mill Drive in Bowie, Maryland (`CAEF17-36003`), the March 2019 bankruptcy consent order (`18-20825`), the 2025 writ of possession, the Appellate Court of Maryland's April 14, 2026 dismissal of `ACM-REG-1051-2025` for failure to file a compliant brief, and the Supreme Court of Maryland's June 23, 2026 certiorari denial. The 37-page OCR-derived `application.txt` now present in the evaluation record confirms every detail of that reconstruction.
- **Statpack and corpus calibration:** `gemini-baseline` accurately audited `metrics/statpack.json` and `metrics/statpack.md` (identifying the `finer_resolved = 0` / non-zero `finer_unread` refusal across `OT2016`–`OT2025`) and used `fedcourts query` to pull directly comparable `OT2026` pro se stay denials—including `scotus/9526000602` (*Nichloson v. U.S. Bank National Association*, another pro se foreclosure stay denial)—as well as contrasting granted substantive applications (`26A512`, `26A476`).
- **Probability and increment calibration:** Its probabilities (`0.002` for relief, `0.008` for response requested, `0.003` for referral, `0.002` for amicus, `0.001` per Justice for `order-writers`, and `0.01` for `big_case_score`) are tightly calibrated to the procedural and substantive posture of an unrepresented state foreclosure/eviction stay application barred by an independent state procedural default.

## Predicted Reasoning (`predicted_reasoning_quality`: 0.95)

`gemini-baseline`'s forecast document (`predicted_reasoning.md`) made specific, concrete, and non-hedged commitments on both the procedural path and the underlying legal posture, all of which were borne out:

1. **In-chambers summary denial by Chief Justice Roberts within 3–10 days of docketing (`borne-out`):** Forecast that Chief Justice Roberts would summarily deny Application 26A619 in chambers within roughly three to ten days of its October 30 docketing (early November 2026) via a standard one-line order. Chief Justice Roberts denied the application in chambers on November 3, 2026—four days after docketing—in a one-line order.
2. **No response request or referral to the full Court (`borne-out`):** Forecast that neither the Chief Justice nor the Clerk would call for a response (`0.008`) and that the application would not be referred to the full Court (`0.003`). Both resolved `false` in `outcome.json`.
3. **No amicus activity or separate writings (`borne-out`):** Forecast zero amicus filings (`0.002`) and no separate opinion or statement by any Justice (`0.001` each). `outcome.json` records `amicus_briefs: 0` and `writing_roles: null`.
4. **Specific underlying dispute and *Hollingsworth v. Perry* threshold failure (`borne-out`):** Accurately identified the underlying dispute as an effort to stay a Maryland writ of possession following residential foreclosure (`CAEF17-36003`), bankruptcy stay-relief (`18-20825`), and the Appellate Court of Maryland's dismissal of `ACM-REG-1051-2025` for failure to file a brief prior to the Supreme Court of Maryland's cert denial in No. 119, explaining why that independent state procedural bar foreclosed a reasonable probability of certiorari or reversal. The OCR-derived `application.txt` in the staged record confirms this exact posture.

## Leakage Assessment

- **Mode:** `forward`
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Evidence:** The prediction ran on `2026-11-03T22:40Z` against the `2026-10-28` arrival snapshot. `retrieval_log.json` and `retrieval.md` show that external lookups retrieved the October 5, 2026 District of Maryland opinion (`recap_document_id: 496317114`), which predated the October 27 Supreme Court application by more than three weeks, and no disposition of Application 26A619 was reported or accessed.
