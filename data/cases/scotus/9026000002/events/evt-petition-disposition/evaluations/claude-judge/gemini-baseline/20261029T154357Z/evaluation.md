# gemini-baseline — scotus/9026000002, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`stage: cert`), forward mode. Outcome: `dismissed`, `actual_granted` 0, resolved 2026-10-26 — the docket shows a joint stipulation to dismiss under Rule 46 filed 2026-10-23 and "Petition Dismissed - Rule 46" on 2026-10-26. All three candidates predicted `denied`, so `correct` = 0 for each on the exact-label axis (dismissed ≠ denied), though each was right on the binary no-grant axis that the Brier score reads.

The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and refer only to "the stamped segment base rate".

Leakage: forward; prediction made 2026-10-06 against a snapshot ending 2026-08-14, a fortnight before the Rule 46 stipulation existed. No retrieved document dates on or after resolution, no query reaching this docket's disposition, no qp-topics read. `not_applicable`, `leakage_suspected` false.

No semantic set is declared on a cert cell, so no `semantic_grades`. Votes not scored (cert stage).

## This candidate

P(grant) 0.25, predicted `denied`. Brier 0.0625.

**reasoning_quality 0.35.** The core signal — a response requested after waiver — is correctly identified as the main upward lever, and the split description (CA5 applying state law vs. CA1/2/4/9 federal law) is accurate. But the analysis is thin and partly mistaken:

- It states the petition text and documents manifest were "unavailable"; the log shows it read `record/documents.json` (the wrong path — the manifest sits under `record/documents/`), so it never read the provisioned petition. The petition itself asks to be held for the lead Fifth Circuit petition, which is the single most important fact about this docket's path, and the candidate missed it.
- Its anchor ("a base grant rate of roughly 1%") is asserted without showing which statpack figure it came from.
- Because it missed the tag-along posture, its forecast that a summary disposition is "highly unlikely" runs opposite to the record's most plausible grant route (hold then GVR).
- No consideration of non-merits termination (withdrawal, settlement), which is what happened.

The 0.25 is a defensible magnitude for a response-requested petition, but it was reached without engaging the record it was given.
