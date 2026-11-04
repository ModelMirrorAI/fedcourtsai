# Evaluation of `codex-baseline` (`scotus/9526000619` / `evt-motion-disposition`)

## Stage, Outcome, and Harness-Stamped Fields

This is an **interim-stage** arrival cell (`stage: interim`, `moment: arrival`) scoring Application No. 26A619 (*Denise Smith v. Brown, Savage, Britto, Stitely & Callahan, LLP, et al.*), submitted to Chief Justice Roberts on October 27, 2026, and docketed October 30, 2026. On November 3, 2026, the Chief Justice summarily denied the application in chambers (`actual_disposition: "denied"`, `actual_granted: 0`, `interim_reading: "denied"`, `interim_granted: 0`), with no response requested (`response_requested: false`), no referral to the full Court (`referred_to_court: false`), zero amicus briefs (`amicus_briefs: 0`), and no separate writings (`writing_roles: null`).

`codex-baseline` predicted `predicted_disposition: "denied"` (`granted: 0`) with `probability: 0.03`. Scored against `outcome.interim_granted = 0`, `correct = 1` and `brier_score = 0.0009`.

Because this is an interim cell, `segment_base_rate`, `brier_skill_score`, and `claim_scores` are computed and stamped by the harness (`stamp-cell`), and `base_rate_basis` is left `null`. Where the stamped segment base rate comes back `null` under the finer interim reading, that refusal reflects the committed `metrics/statpack.json` counts over the strictly-prior ten-Term lookback window (`OT2016`–`OT2025`): every Term in that window currently records `finer_resolved: 0` (`0 < 50`, below the pre-registered `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor) and non-zero `finer_unread` (`1,366` unread substantive applications across `OT2016`–`OT2025`, plus `16` unparsed).

## Reasoning Quality (`reasoning_quality`: 0.80)

`codex-baseline`'s rationale in `reasoning.md` is methodical, well-structured, and contract-compliant:

- **Stage and baseline discipline:** `codex-baseline` properly recognized that cert salience bands do not apply to an interim application (`context.band: null`) and audited both `metrics/statpack.md` and `metrics/statpack.json` over the strictly-prior `OT2016`–`OT2025` window. It accurately identified that the finer-reading columns contain zero resolved rows and 1,366 unread rows across those ten Terms, and rightly declined to substitute an unconditioned escalation ratio or a cert-stage rate.
- **Handling of the provisioned filing gap:** At the time the prediction cells ran against the `2026-10-28` snapshot, `record/documents/application.txt` had `empty_text: true` (`ocr_derived: false`), whereas the post-resolution evaluation record now includes the 37-page OCR-derived text. `codex-baseline` handled the blank text appropriately by treating it as an extraction limitation rather than evidence that no application was filed, and justified leaving `big_case_score` null on that basis.
- **Limitations in external investigation and increment calibration:** Unlike `gemini-baseline`, `codex-baseline` did not search CourtListener RECAP or the web for the named parties (`Denise Smith` and `Brown, Savage, Britto, Stitely & Callahan, LLP`), which would have surfaced the pre-cutoff October 5, 2026 District of Maryland opinion detailing the underlying Bowie, Maryland residential foreclosure and state appellate default. In addition, `codex-baseline`'s `referral-increment` of `0.20` (and `response-requested-increment` of `0.08`) is high for an unrepresented state-court civil stay application at the arrival cut with no response requested, as Circuit Justices almost always deny such applications in chambers without referring them to the Conference.

## Predicted Reasoning (`predicted_reasoning_quality`: 0.78)

`codex-baseline`'s forecast document (`predicted_reasoning.md`) committed to four central claims, all of which were borne out by the staged record:

1. **In-chambers denial by the Chief Justice without referral or written opinion (`borne-out`):** Forecast that the Chief Justice would most likely deny the stay without a written explanation and without referring it to the full Court. On November 3, 2026, Chief Justice Roberts denied Application 26A619 in chambers in a standard one-line order (`referred_to_court: false`, `writing_roles: null`).
2. **Modal path with zero escalation signals (`borne-out`):** Forecast that the modal path would add no response request, no referral, and no amicus filings. All three resolved at zero/false in `outcome.json`.
3. **Resolution timing within one to three weeks (`borne-out`):** Specifically forecast disposition roughly between November 3 and November 17, 2026. The application was denied on November 3, 2026—seven days after submission.
4. **No new legal rule or separate writing (`borne-out`):** Forecast a summary disposition with no separate writing by any Justice, matching the realized one-line order.

Because `codex-baseline` did not uncover the underlying foreclosure/eviction dispute from pre-cutoff public records, its substantive description of the expected failure under the stay factors is generic and its referral probability (20%) is somewhat hedged, placing the forecast document near the `0.75` anchor (`0.78`).

## Leakage Assessment

- **Mode:** `forward`
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Evidence:** The prediction ran on `2026-11-03T22:40Z` against the `2026-10-28` arrival snapshot. `retrieval_log.json` and `reasoning.md` show no queries for the target application's docket or outcome; external calls were restricted to pre-2026 cert denials via `fedcourts query` and *Hollingsworth v. Perry*, 558 U.S. 183 (2010).
