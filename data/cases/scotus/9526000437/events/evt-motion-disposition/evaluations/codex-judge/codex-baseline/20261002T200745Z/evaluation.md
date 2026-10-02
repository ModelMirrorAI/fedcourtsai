# Evaluation: codex-baseline

## Outcome and numerical scores

The interim application was denied by the Chief Justice on October 1, 2026. The prediction correctly selected `denied`, so `correct = 1`. With grant probability 0.04 and recorded `actual_granted = 0`, the Brier loss is `(0.04 - 0)^2 = 0.0016`.

The interim baseline and skill belong to the harness and are omitted; `base_rate_basis` is null. The committed statpack contains the relevant interim section and 296 resolved substantive applications in eligible prior-Term rows for application Term 2026, exceeding the floor of 50. Neither a missing section nor a thin pool appears to require refusal; the post-run stamped result is not yet available. These are committed-pack counts, not a live-corpus freshness claim. Machine-matched resolution, uneven historical parsing, and selection differences constrain any later skill interpretation. No votes or semantic propositions are scored on this stage, and the harness alone scores mechanical claims.

## Reasoning quality: 0.90

The rationale distinguishes observed docket facts from inferences, identifies the arrival-position boundary correctly, and does not mistake no response or referral at arrival for terminal judicial disinterest. It explicitly treats unreadable application text as missing evidence rather than evidence of a deficient application. It avoids claiming that the listed trial court proves unexhausted state appeals, and does not invent an underlying legal issue.

Its interim baseline selection is transparent and appropriately restricted to prior application Terms. It recognizes coverage and selection limitations, distinguishes subjective adjustments from measured conditional rates, and retains uncertainty about the unread application. These evidentiary disciplines justify a higher reasoning-quality assessment even though its realized Brier loss is larger than those of the two 1% forecasts.

The remaining limitation is calibration: the reduction from the pooled anchor to 4% is judgmental, not supported by a matched applicant-class dataset or readable merits and harm evidence. The rationale supports a broad denial preference better than the precise number. The Court's unexplained denial confirms the forecast label but not a particular merits or jurisdictional explanation. This score grades `reasoning.md` alone; it does not reward the forecast document's procedural details or grade the structured claims.

## Leakage and timing

The log records forward mode. It shows reads of the frozen snapshot, context, document manifest, and committed statpack. Twenty of 22 calls have captured results; the two unobserved web calls seek general injunction precedent and a general precedent page, not the applicant or this application's disposition. I do not adopt the candidate's assertion that those calls returned nothing as a fact proven by the log. Their query subjects, however, supply no concrete route to this case's outcome. No own-case disposition is quoted or presupposed in the reasoning.

I record `retrieved_outcome_material = false`, forward `influenced_prediction = not_applicable`, and `leakage_suspected = false` on this evidence. The prediction timestamp, 21:59:25 UTC on October 1, 2026, falls on the recorded resolution date. The exact order-publication time is unavailable; the cell-level flag requests review of that timing rather than silently treating the September 29 snapshot date as the forecast's creation date. Same-day timing without demonstrated exposure does not establish influence.

The evaluator's October 2 document manifest now reports OCR-derived application text, whereas the candidate describes its contemporaneous file as empty. The prediction's original snapshot and document bytes are not staged here. I therefore neither substitute the refreshed OCR for the candidate's information set nor treat the changed manifest as evidence that the candidate ignored available substance.
