# claude-baseline — P(grant) 0.20, predicted denied

## Outcome and scoring

Cert cell (`stage: cert`). The petition (No. 25-1427, *Independent Specialty Insurance Co. v. Apex Hospitality Group*) was distributed once (Aug 12 for the Sept 28 conference), a response was requested Aug 17, and on Oct 19, 2026 counsel filed a joint stipulation to dismiss under Rule 46; the petition was dismissed Oct 20. `actual_disposition` = `dismissed`, `actual_granted` = 0.

The prediction froze `context.band` = `baseline` (`sal-v4`), so the segment base rate, `brier_skill_score` and basis are the harness's to stamp; I wrote none of them — refer to the stamped segment base rate. `correct` is 0 on the exact-label axis (`denied` vs. `dismissed`), even though the binary no-grant call was right. No votes are scored on a cert cell; no semantic set is declared.

**Leakage:** forward cell, predicted 2026-10-06 against a 2026-10-05 snapshot; the event resolved 2026-10-20. Nothing in the log or prose surfaces the stipulation or dismissal. `not_applicable`, not suspected.

**Brier:** (0.20 − 0)² = 0.04.

## Reasoning quality: 0.75

The most thoroughly grounded analysis. It anchored on the pooled baseline (≈5.1%, OT2017–OT2024, table shown), identified the lead petition (No. 25-1383, *Indian Harbor v. Town of Vinton*) and read its public docket (waiver, amici, response requested, BIO, reply), and read the Fifth Circuit's *Town of Vinton* opinion itself, noting the state-law holding rests on a single sentence citing *Arthur Andersen*. The grant probability is explicitly decomposed as P(lead granted) × P(reversal) × P(GVR follows), and — uniquely among the candidates — it shaded down "for the chance the lead case settles or is dismissed during the hold" and named "a dismissal or withdrawal before redistribution" as the residual on its relist claim. That is the class of outcome that occurred (here on this docket rather than the lead), so the reasoning at least priced the right failure mode, if lightly. Its vehicle-problem discussion is apt, and its "where to discount me" section is candid about the unverified lead-case odds.

Weaknesses: the 0.30–0.35 lead-case grant estimate is high for a paid petition with a response requested and is unsupported by any corpus cut, and the derivative arithmetic leaves little room for this follower's own early termination. Still, the direction was right and the uncertainty well characterized.
