# Evaluation of `claude-baseline` (`scotus/9526000619` / `evt-motion-disposition`)

## Stage, Outcome, and Harness-Stamped Fields

This is an **interim-stage** arrival cell (`stage: interim`, `moment: arrival`) scoring Application No. 26A619 (*Denise Smith v. Brown, Savage, Britto, Stitely & Callahan, LLP, et al.*), submitted to Chief Justice Roberts on October 27, 2026, and docketed October 30, 2026. On November 3, 2026, the Chief Justice summarily denied the application in chambers (`actual_disposition: "denied"`, `actual_granted: 0`, `interim_reading: "denied"`, `interim_granted: 0`), with no response requested (`response_requested: false`), no referral to the full Court (`referred_to_court: false`), zero amicus briefs (`amicus_briefs: 0`), and no separate writings (`writing_roles: null`).

`claude-baseline` predicted `predicted_disposition: "denied"` (`granted: 0`) with `probability: 0.02`. Scored against `outcome.interim_granted = 0`, `correct = 1` and `brier_score = 0.0004`.

Because this is an interim cell, `segment_base_rate`, `brier_skill_score`, and `claim_scores` are computed and stamped by the harness (`stamp-cell`), and `base_rate_basis` is left `null`. Where the stamped segment base rate comes back `null` under the finer interim reading, that refusal reflects the committed `metrics/statpack.json` counts over the strictly-prior ten-Term lookback window (`OT2016`–`OT2025`): every Term in that window currently records `finer_resolved: 0` (`0 < 50`, below the pre-registered `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor) and non-zero `finer_unread` (`1,366` unread substantive applications across `OT2016`–`OT2025`, plus `16` unparsed).

## Reasoning Quality (`reasoning_quality`: 0.78)

`claude-baseline`'s rationale in `reasoning.md` is concise, accurate on the baseline rules, and sensible on the headline disposition:

- **Statpack and corpus grounding:** `claude-baseline` properly inspected `metrics/statpack.json` (`interim.terms[].finer_*`), recognized that every Term in `OT2016`–`OT2025` has `finer_resolved = 0` and non-zero `finer_unread` so no published finer-reading baseline exists, and used the older substantive reading (`160/1366`) and a `fedcourts query --include-applications` lookup (citing *Nichloson v. U.S. Bank*) strictly for descriptive shape.
- **Inference from docket metadata:** Faced with the blank `application.txt` (`empty_text: true` at prediction time), `claude-baseline` reasonably noted that a pro se stay application from the Supreme Court of Maryland against a law-firm respondent likely involved a collection, foreclosure, or fee dispute, while explicitly stating that its probability did not depend on guessing the subject matter.
- **Omission of party-level RECAP lookup and elevated referral increment:** Unlike `gemini-baseline`, `claude-baseline` did not search CourtListener RECAP for the parties, which would have surfaced the pre-cutoff October 5, 2026 District of Maryland opinion detailing the underlying foreclosure and state appellate dismissal. Additionally, `claude-baseline` set `referral-increment` to `0.12` on the ground that pro se applicants often renew to a second Justice after a chambers denial; however, `evt-motion-disposition` resolves upon the initial November 3 chambers denial (`referred_to_court: false`), making a 12% pre-disposition referral probability somewhat high.

## Predicted Reasoning (`predicted_reasoning_quality`: 0.72)

`claude-baseline`'s forecast document (`predicted_reasoning.md`) committed to four procedural claims, all of which held:

1. **In-chambers denial by the Chief Justice within about two weeks of docketing (`borne-out`):** Forecast that the Chief Justice, acting alone as Circuit Justice for the Fourth Circuit, would deny the stay application without asking for a response in November 2026, within about two weeks of docketing. Chief Justice Roberts denied the application in chambers on November 3, 2026—four days after docketing.
2. **No response requested or amicus filings (`borne-out`):** Forecast that a response call was unlikely (`3%`) and no amicus filings were expected (`1%`), matching `response_requested: false` and `amicus_briefs: 0`.
3. **No referral on initial submission (`borne-out`):** Forecast that referral was unlikely on initial submission to the Chief Justice, matching `referred_to_court: false`.
4. **One-line order with no separate writings (`borne-out`):** Forecast that any denial would be a one-line order with no separate writings, matching `writing_roles: null`.

While all of its procedural calls were accurate, the document is very brief and commits to no case-specific doctrinal or factual ground because `claude-baseline` did not investigate the underlying Maryland litigation in RECAP. Under the rubric, accurate procedural calls paired with generic substantive content place it at `0.72`.

## Leakage Assessment

- **Mode:** `forward`
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Evidence:** The prediction ran on `2026-11-03T22:39Z` against the `2026-10-28` arrival snapshot. `retrieval_log.json` shows a captured `web-fetch` of `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a619.html` at `2026-11-03T22:40:20Z`. As `claude-baseline` documented in both `reasoning.md` and `retrieval.md`, the live docket page at that timestamp still contained only the single October 27 submission entry (docketed October 30) and had not yet posted the November 3 denial.
