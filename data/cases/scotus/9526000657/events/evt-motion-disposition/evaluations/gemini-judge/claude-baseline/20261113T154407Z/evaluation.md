# Evaluation — `claude-baseline` on `scotus/9526000657` (`evt-motion-disposition`)

## Stage and scoring baseline

This cell evaluates an **interim**-stage arrival event (`evt-motion-disposition`, Application No. 26A657, *Paul Schultz v. Kevin McCarthy*). On November 10, 2026 — eight days after the November 2 submission — Chief Justice Roberts denied the stay application in chambers without requesting a response, referring the application to the full Court, or eliciting any amicus filings or separate writings (`actual_disposition: "denied"`, `interim_reading: "denied"`, `interim_granted: 0`). Because this is an interim cell, `segment_base_rate`, `brier_skill_score` (with `base_rate_basis: null`), and `claim_scores` (`interim-v3`) are computed and stamped by the harness against the stamped segment base rate; `vote_accuracy`, `judgment_correct`, and `semantic_grades` do not apply.

`claude-baseline` predicted `predicted_disposition: "denied"` (`granted: 0`) with `probability = 0.015`, earning `correct = 1` on the finer interim binary and `brier_score = 0.000225`.

## Reasoning quality (`0.84`)

`claude-baseline`'s `reasoning.md` is concise, disciplined, and quantitatively well-grounded:

- **Provisioned record & empty-text handling:** When the prediction ran on November 9, 2026, `record/documents/application.txt` carried 61 scanned pages with `empty_text: true` (prior to the November 11 OCR pass). `claude-baseline` properly treated the filing's text as unavailable rather than absent, extracted all key arrival signals from `2026-11-03.json` (pro se self-representation by Paul David Schultz, non-capital status, Fourth Circuit No. 26-2406, submission to The Chief Justice, zero escalation signals), and verified on the live Supreme Court docket on November 9 that no post-arrival entries had appeared.
- **Base-rate anchor (graded against statpack build `f0a8cabd41e6`, `sha256:b122cc43052b1328321031e3615601101a1b85c7dcdc87d23e5436373b03f133`):** Reconstructing the prediction-time statpack via `fedcourts statpack-at` (build `f0a8cabd41e6`, which predates the committed statpack overall while carrying the identical `interim` section) confirms that `claude-baseline` accurately pooled the strictly-prior OT2016–OT2025 `finer_granted`/`finer_resolved` counts (verifying the 50-resolution floor and `finer_unread = 0` in every pooled Term) to match the stamped segment base rate, and accurately cited the descriptive `private`/`unmarked` applicant-class cut (`63/906 = 7.0%`). It also cogently explained why `private`/`unmarked` mixes represented corporate, institutional, and election-law applicants with unrepresented individuals, justifying a substantial downward adjustment to `0.015` while keeping the probability above zero due to the unread application text.
- **Limitations:** On CourtListener, `claude-baseline` searched by party names (`Schultz` and `McCarthy`), uncovering the E.D. Va. bankruptcy adversary proceeding (`25-01061`) and 2026 E.D. Va. civil dockets, and prudently flagged its bankruptcy characterization as an unconfirmed inference. However, because it did not query Fourth Circuit docket `26-2406` directly (captioned *In re: Paul Schultz* on mandamus), it missed the Fourth Circuit's October 26, 2026 unpublished opinion denying Schultz's judicial-recusal mandamus petition. In addition, its rationale for `referral-increment = 0.15` relied on post-denial renewed applications to a second Justice ("often renew the application to another Justice, who usually refers it to the Court"), conflating post-disposition renewal practice with pre-disposition referral of this initial application event (`0.15` was noticeably high for an unrepresented bankruptcy stay at arrival).

## Predicted reasoning (`0.78`)

`claude-baseline`'s `predicted_reasoning.md` committed to specific, concrete claims on how the application would be resolved, nearly all of which held up cleanly against the staged record:

1. **In-chambers denial by The Chief Justice with no separate writings (`borne-out`):** Rather than hedging between the Chief Justice and the full Court, `claude-baseline` specifically forecast that The Chief Justice, acting as Circuit Justice for the Fourth Circuit, would deny the stay within one to three weeks of submission by an unexplained order with no noted dissent or separate writing. That exact disposition occurred eight days after submission on November 10, 2026.
2. **No call for a response (`borne-out`):** Correctly committed to disposition on the papers without requesting a response (`response_requested: false`).
3. **No referral to the full Court (`borne-out`):** Correctly forecast no referral on this application (`referred_to_court: false`), properly distinguishing a hypothetical post-denial renewal from action on this event.
4. **Zero amicus participation (`borne-out`):** Correctly forecast zero amicus briefs (`amicus_briefs: 0`).
5. **Calendar phrasing (`not-borne-out`):** A secondary timing bullet predicted denial in "mid-to-late November 2026," whereas the order issued on November 10, 2026 — slightly earlier than mid-November, though squarely inside the lead bullet's "one to three weeks of submission" window (November 9–23).

The document earns `0.78` — just above the `0.75` anchor — because its central procedural and dispositional commitments were specific and borne out, tempered slightly by the minor calendar miss on the secondary timing bullet and its generic substantive description (owing to not having located CA4 No. 26-2406 on CourtListener).

## Leakage (`not_applicable`, `leakage_suspected: false`)

`retrieval_log.json` records `mode: "forward"` on `2026-11-09T03:30Z`–`03:31Z` (one day before the November 10 denial) with `result_capture_coverage = 1.0` across all 18 calls. Checking `supremecourt.gov` on November 9 returned only the November 2 submission entry, and all corpus and CourtListener lookups predated disposition (latest `retrieved_doc_date: 2026-11-06`). No outcome material existed or was accessed.
