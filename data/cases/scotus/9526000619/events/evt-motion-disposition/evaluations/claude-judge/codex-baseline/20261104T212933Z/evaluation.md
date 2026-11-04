# Evaluation of codex-baseline

**Cell:** scotus/9526000619 · evt-motion-disposition · **interim** stage (application 26A619, a stay of a Maryland writ of possession, submitted to the Chief Justice on Oct 27, 2026).
**Outcome:** denied by The Chief Justice on Nov 3, 2026 (`interim_reading` denied, `interim_granted` 0); no response requested, no referral, no amici.

**Scoring.** The outcome records the finer interim reading, so the cell is scored on `interim_granted` = 0. A `denied` prediction falls on the ungranted side, so `correct` = 1. `brier_score` = p². This is an interim cell, so the segment base rate and the skill score come from the harness stamp (pooled from the interim slice over application Terms before 2026) and I wrote neither. Every candidate reports that the committed pack's finer-reading pool for 2016–2025 has zero resolved applications. If that holds, the stamp will come back null because the pool is below its floor and unread rows remain, not because the section is missing. No vote accuracy is scored on this stage, and no semantic set is declared.

**Leakage.** The log's mode is forward. The Nov 3 denial came on the same date the predictions were made (~22:4xZ), so I did not pass the cell by default. I checked each log for this case's own disposition (see the note below and flags.json).

## codex-baseline: p = 0.03, denied → correct 1, Brier 0.0009

**Reasoning (0.70).** The structure is sound. The candidate correctly treats this as an interim event and sets cert bands aside. It audits the finer-reading pool and declines to substitute the older rate. It states the *Hollingsworth* stay standard, which it checked against primary text. It is honest that the application text was empty and does not invent facts about the dispute. What holds it back: it did no case-specific research even though forward mode allowed it. Its docket metadata showed a pro se applicant against a private law firm, out of a state high court, and that alone justified a lower number. As a result 3% is well calibrated in direction but more diffuse than the record warranted. The 20% referral increment is high for an unrepresented in-chambers stay, though it did not come up.

**Leakage.** None. No query touched the case's caption, docket or outcome. The web calls were uncaptured, but their queries are the stay standard and the Court's rules.

## Predicted reasoning (0.70)

Central claims: (1) the Chief Justice denies without explanation and without referral; (2) no response request, no referral, no amici; (3) disposition around Nov 3–17; (4) no separate writing. All four were borne out, and the denial came on Nov 3. These are the modal calls for this kind of application, and the document says little a competent reader could have gotten wrong. The conditional ground ("failure to meet the stay factors") is untested by an unexplained order. That makes it specific enough to sit above 0.5, but not the top of the scale.
