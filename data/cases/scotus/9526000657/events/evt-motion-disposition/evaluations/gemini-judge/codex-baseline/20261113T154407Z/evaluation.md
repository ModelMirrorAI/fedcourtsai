# Evaluation — `codex-baseline` on `scotus/9526000657` (`evt-motion-disposition`)

## Stage and scoring baseline

This cell evaluates an **interim**-stage arrival event (`evt-motion-disposition`, Application No. 26A657, *Paul Schultz v. Kevin McCarthy*), resolved on November 10, 2026 when Chief Justice Roberts denied the stay application in chambers without requesting a response, referring the application to the full Court, or drawing any amicus briefs or separate writings (`actual_disposition: "denied"`, `interim_reading: "denied"`, `interim_granted: 0`). Because this is an interim cell, `segment_base_rate`, `brier_skill_score` (with `base_rate_basis: null`), and `claim_scores` (`interim-v3`) are computed and stamped by the harness against the stamped segment base rate; `vote_accuracy`, `judgment_correct`, and `semantic_grades` do not apply.

`codex-baseline` predicted `predicted_disposition: "denied"` (`granted: 0`) with `probability = 0.07`, earning `correct = 1` on the finer interim binary and `brier_score = 0.0049`.

## Reasoning quality (`0.68`)

`codex-baseline`'s `reasoning.md` paired meticulous statistical mechanics with weak retrieval follow-through and an overly conservative refusal to condition below the broad `private`/`unmarked` class rate:

- **Exemplary statpack verification (graded against statpack build `f0a8cabd41e6`, `sha256:b122cc43052b1328321031e3615601101a1b85c7dcdc87d23e5436373b03f133`):** Reconstructing the prediction-time statpack via `fedcourts statpack-at` (build `f0a8cabd41e6`, which predates the committed statpack overall while carrying the identical `interim` section) confirms that `codex-baseline` verified every single Term's `finer_granted`/`finer_resolved` counts across OT2016–OT2025, checked `finer_unread = 0` and the `unparsed` counts (15 in OT2016, 1 in OT2017), noted why the right-censored ladder counts are not arrival-conditioned transition rates, and cleanly separated the whole-pool scoring baseline (the stamped segment base rate) from the descriptive `private`/`unmarked` applicant-class cut (`63/906 = 6.9536%`). It also avoided leaping from respondent's name ("Kevin McCarthy") to an unfounded political-figure assumption when `application.txt` had `empty_text: true` on November 9.
- **Substantial retrieval and calibration gaps:**
  1. **Prematurely abandoned lower-court retrieval:** Despite running in `forward` mode, `codex-baseline` issued only a single CourtListener RECAP search (`court="ca4"`, `docket_number="26-2406"`, `filed_before="2026-11-03"`) and stopped when that date-filtered query returned zero hits. Dropping the unnecessary `filed_before` filter or searching by party names (`Schultz` / `McCarthy`) immediately surfaced Fourth Circuit No. `26-2406` (*In re: Paul Schultz*, decided October 26, 2026) and the underlying E.D. Va. Chapter 7 bankruptcy appeals. Likewise, in its `fedcourts query` call, `codex-baseline` omitted `--include-applications`, retrieving five denied cert petitions rather than interim stay comparators.
  2. **Failure to adjust for pro se emergency-docket posture:** Even from the provisioned arrival snapshot alone (`2026-11-03.json`), applicant Paul David Schultz was listed as his own counsel of record (`pro se`) in a non-capital case with zero escalation signals. `codex-baseline` noted this self-representation but refused to adjust downward from the `6.95%` `private`/`unmarked` rate (`probability = 0.07`, alongside `response-requested-increment = 0.12` and `referral-increment = 0.30`). Because the `private`/`unmarked` grants in OT2016–OT2025 come overwhelmingly from represented institutional, corporate, religious-liberty, and election-law applicants rather than unrepresented litigants at arrival, leaving `P(grant)` at `7%` and `P(referral)` at `30%` discarded a strong, reliable structural signal on the emergency docket and left `big_case_score` unestimated (`null`).

## Predicted reasoning (`0.62`)

`codex-baseline`'s `predicted_reasoning.md` was directionally accurate across all procedural steps that occurred, but remained hedged and generic:

1. **Denial via unexplained short order with no separate writings (`borne-out`):** Correctly forecast denial by a short unexplained order with no Justice writing separately, though it hedged on the acting decision-maker ("The Court or the Chief Justice will deny application 26A657") rather than committing to in-chambers disposition by the Chief Justice.
2. **Response probably not requested (`borne-out`):** Forecast that a response would "probably" not be called for (`12%` probability), matching `response_requested: false`.
3. **Resolved without full-Court referral (`borne-out`):** Forecast that the application would "probably" be resolved without referral (`30%` probability), matching `referred_to_court: false`.
4. **Zero additional amicus filings (`borne-out`):** Forecast that the amicus count would remain zero (`amicus_briefs: 0`).
5. **Disposition window of roughly November 9–23 (`borne-out`):** Accurately placed the November 10, 2026 denial inside its one-to-three-week window from submission.

Under the forecast-document rubric, a document that is right in direction but generic sits near `0.50`, while concrete procedural commitments lift it above that floor. Calling no response, no referral, no amici, no separate writings, and the November 9–23 disposition window earns credit above `0.50`, but hedging between "The Court or the Chief Justice," framing ladder calls with wide uncertainty ("probably" against a 30% referral probability), and offering zero case-specific context caps the grade at `0.62`.

## Leakage (`not_applicable`, `leakage_suspected: false`)

`retrieval_log.json` records `mode: "forward"` on `2026-11-09T03:31Z`–`03:34Z` (one day before the November 10 denial) with `result_capture_coverage = 0.9` (27 of 30 calls captured). Evaluating the three `unobserved` `web-search` calls by their queries confirms they targeted general Supreme Court Rule 23 URLs/queries (`2023RulesoftheCourt.pdf`, `Rule 23 stay application relief lower court`, `2026rulesofthecourt_web.pdf`), while all corpus and CourtListener calls were pre-disposition and `rg` explicitly excluded `data/qp-topics/**`. No outcome material existed or was accessed.
