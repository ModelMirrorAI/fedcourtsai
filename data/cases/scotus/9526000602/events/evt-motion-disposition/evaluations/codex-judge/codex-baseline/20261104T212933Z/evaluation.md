# Evaluation: codex-baseline

## Outcome and scoring

This is an **interim**, arrival-moment cell. The November 3, 2026 denial by Justice Thomas gives `interim_reading = denied` and `interim_granted = 0`. codex-baseline's `denied` label is correct (`correct = 1`), and `(0.04 - 0)^2 = 0.0016`. No difference between the older unqualified-grant binary and the finer reading affects this outright denial.

The baseline and Brier skill are the harness's to stamp. The committed statpack has the interim section and an applicable strictly-prior 2016–2025 pool larger than its 50-resolution minimum; no missing-section or thin-pool refusal is apparent. No substitute rate is quoted here and `base_rate_basis` remains null. Votes are not scored on interim cells, no semantic set applies, and mechanical claim scores are left entirely to the harness.

## Reasoning quality: 0.90

The rationale carefully separates what the arrival snapshot discloses from what an unreadable application cannot establish. It does not infer either a particular foreclosure theory from the bank's name or a skipped appellate proceeding from the lower-court metadata. That caution is consequential: the evaluator's now-readable application actually identifies Eleventh Circuit No. 26-13319 and asks for temporary protection against eviction while an appellate stay request is pending.

The rationale uses the correct interim population, prior-Term window, and integer totals. It recognizes that the pooled population is not conditioned on the arrival state, that escalation columns include pending cases, and that a query restricted to denials cannot estimate a grant rate. It explicitly declines to treat unrelated cert petitions as interim analogues. It also distinguishes zero escalation at arrival from a subsequent judicial decision not to escalate. These are strong safeguards against selection bias and double counting.

The downward adjustment remains a coarse subjective assessment of a thin civil-dispute record, not a case-specific demonstration that the stay factors fail. Absence of visible positive evidence is not itself strong negative evidence, and the rationale appropriately says so. Missing application content therefore limits the precision of the probability and prevents a maximum soundness grade. The realized denial does not retroactively verify a particular doctrinal ground. Conversely, the larger Brier loss than the other candidates is not a reason to lower this separate analysis-quality grade.

All candidates report a blank application, whereas the evaluator's manifest reports nonempty OCR. I grade the candidate's treatment of its actual information gap, not its ability to anticipate later extraction. The cell's flags record that provisioning difference. The metadata discussion does not establish leakage: later docketing and attachment-fetch metadata are not this application's later disposition.

## Predicted reasoning

**Grade: 0.90.** The main forecasts are specific and borne out: denial by Thomas, no response/referral/amicus escalation, and disposition two to four weeks after October 20. November 3 is exactly fourteen days after submission. These procedural commitments earn substantial credit even though the document responsibly avoids selecting an unsupported substantive legal theory.

The absence of a new legal rule and of explanatory or separate writings cannot be conclusively checked against the staged bare docket entry and null writing roster; those claims are unresolved, not misses. The conditional explanation of a hypothetical grant was never tested and earns neither credit nor penalty. Generic statements about success and irreparable injury earn no independent credit. The grade stays below full verification and is separate from both the rationale grade and all structured claims.

## Leakage

The log records `forward` mode and 28 calls dated October 31, before the November 3 resolution. Twenty-five calls are captured; three general-rules web lookups are `unobserved`, yielding capture coverage of approximately 0.893. I do not adopt the retrieval note's statement that those calls returned no usable text as a captured fact: their queries, not absent results, are the observable evidence. The queries concern general stay rules, not this application's disposition.

The corpus call's readable April 29 document date and the note's other-case October dispositions do not identify an outcome for this application. Nothing in the queries, rationale, forecast, or retrieval note shows this case's disposition being known. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
