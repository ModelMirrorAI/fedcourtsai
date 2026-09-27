# Evaluation: claude-baseline

## Outcome and scores

The supplied interim outcome records **withdrawn** on September 25, 2026, with `actual_granted=0`. The candidate's label is **denied**, so exact-label correctness is **0**. With P(grant)=0.03, the Brier score is **(0.03 - 0)^2 = 0.0009**. This is accurate anticipation of a low-probability grant on the binary axis, not an exact forecast of the procedural disposition. The supplied outcome gives no explanation for withdrawal and no adjudication of the underlying theory.

## Reasoning quality: 0.63

The rationale identifies the proper interim baseline, recognizes a mismatch between that broad cohort and capital applications, and supplements it with an explicitly described recent capital sample. It identifies a clemency-process theory, connects its stated doctrinal weakness to prospects for certiorari, and candidly distinguishes inference from the docket skeleton from analysis of actual filings. That candor and the attempt to supply relevant comparators strengthen the explanation of its low probability. It also recognizes withdrawal or mootness as possible alternative routes in its discussion of referral, though it does not develop them in the headline disposition analysis.

The adjustment to 3% remains under-supported. A recent, limit-selected set of denials is not a representative capital-stay rate; twelve capital rows also need not all be comparable execution-stay applications. Two recent institutional grants do not establish that the entire pooled substantive population is institutionally dominated. The legal assessment rests on party and lower-court identifiers rather than the actual submissions, a limitation the candidate appropriately acknowledges. The absence of escalation signals near arrival has limited negative force. Finally, a recent resolved prior does not establish corpus-wide freshness: its statement that the read is current is stronger than the vintage evidence it reports.

These deductions concern evidentiary support, selection, and calibration in `reasoning.md`. They do not score the structured claims or forecast document and are not penalties for the eventual withdrawal. I did not independently retrieve the candidate's cited authorities or prior cases.

## Stage and baseline

This is an **interim** cell, not a cert cell. The baseline and skill are harness-owned, so `segment_base_rate` and `brier_skill_score` are omitted and `base_rate_basis` is null. The committed interim section is present and its strictly prior application-Term rows exceed the registered 50-resolved floor for the frozen Term 2026; no missing-section or thin-pool refusal is apparent. The machine-match-selected population, withdrawal-as-ungranted rule, denial-first treatment of mixed dispositions, uneven parsing, and escalation-selected scoring cohort limit what any stamped skill can establish. No salience-band rate is substituted. Vote accuracy is prohibited for this stage, no semantic set is declared, and mechanical claim scores remain the harness's. The forecast document was read only for context.

## Leakage

The harness log records **forward**, and all 24 calls are dated September 1, before the supplied September 25 withdrawal. It shows reads of provisioned inputs, the statpack, and general corpus queries rather than a targeted search for this application's result. The one populated retrieved-document date is August 28. The rationale describes other applications' denials as priors and explicitly avoids live retrieval about this case or its linked petition; it does not presuppose the withdrawal.

Capture coverage is 1.0, although result digests are not full bodies available to this evaluator and some query strings are truncated. No visible date, query, or prose establishes that the case had already resolved at prediction time. `retrieved_outcome_material=false`, influence is `not_applicable`, and `leakage_suspected=false`. Ordinary forward retrieval of pre-resolution context is not leakage.
