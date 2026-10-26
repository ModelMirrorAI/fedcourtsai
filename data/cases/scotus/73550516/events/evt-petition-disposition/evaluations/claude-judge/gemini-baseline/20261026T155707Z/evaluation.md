# gemini-baseline — P(grant) 0.18, predicted denied

## Outcome and scoring

Cert cell (`stage: cert`). The petition (No. 25-1427, *Independent Specialty Insurance Co. v. Apex Hospitality Group*) was distributed once (Aug 12 for the Sept 28 conference), a response was requested Aug 17, and on Oct 19, 2026 counsel filed a joint stipulation to dismiss under Rule 46; the petition was dismissed Oct 20. `actual_disposition` = `dismissed`, `actual_granted` = 0.

The prediction froze `context.band` = `baseline` (`sal-v4`), so the segment base rate, `brier_skill_score` and basis are the harness's to stamp; I wrote none of them — refer to the stamped segment base rate. `correct` is 0 on the exact-label axis (`denied` vs. `dismissed`), even though the binary no-grant call was right. No votes are scored on a cert cell; no semantic set is declared.

**Leakage:** forward cell, predicted 2026-10-06 against a 2026-10-05 snapshot; the event resolved 2026-10-20. Nothing in the log or prose surfaces the stipulation or dismissal. `not_applicable`, not suspected.

**Brier:** (0.18 − 0)² = 0.0324.

## Reasoning quality: 0.40

The rationale is a single paragraph. Its structure is sound — anchor on the ~5% baseline, then treat the grant probability as essentially P(lead case granted) × P(reversal → GVR) — and it reached the best-calibrated number of the three. But it is thin and partly inaccurate: it calls the split "clean 4-1" on the petition's word, without the qualification the record warrants (the Fifth Circuit's position and *GE Energy*'s reservation are not engaged); it gives the lead case's number as No. 25-1524, a figure the petition does not supply (it cites only the extension application, No. 25A1099) and that no logged lookup shows being verified; its ~25% lead-case figure is asserted, not derived; and it states that the response request "guarantees" redistribution — a certainty that the actual outcome (dismissal before any redistribution) shows was overstated. No consideration of settlement, vehicle issues, or what the response request does and does not imply. The low Brier owes more to the number than to the analysis.
