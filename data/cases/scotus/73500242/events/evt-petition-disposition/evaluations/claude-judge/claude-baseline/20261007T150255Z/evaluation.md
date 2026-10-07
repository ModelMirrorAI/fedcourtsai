# Evaluation: claude-baseline — scotus/73500242, evt-petition-disposition

## Outcome and scoring

Cert-stage cell, forward mode. The petition (No. 25-1340, Nwosu v. 1600 West Loop South) was distributed once, for the September 28, 2026 conference, and denied on October 5, 2026 with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- **Disposition:** predicted `denied`, actual `denied` → `correct` = 1.
- **Brier:** probability 0.012 → (0.012 − 0)² = **0.000144**.
- **Segment base rate (`risk_set`):** the prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is rendered under sal-v4, so the risk-set basis applies. Pooling the baseline band's bracketed `reached` figures, resolved-weighted, over every rendered Term strictly before the case's Term (OT2025), i.e. OT2017–OT2024 (n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271; 11,580 in all), gives **0.05121** (593.0 weighted grants / 11,580, from the unrounded `prefix_est_grant_rate` rows in `metrics/statpack.json`; the rendered percentages give 0.05120). The table renders "most recent 10 of 10 Terms", so the rendered window is the whole pack and matches the configured ten-Term lookback; no window divergence to flag.
- **Brier skill:** baseline Brier = 0.05121² = 0.002622; 1 − 0.000144 / 0.002622 = **0.945**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; omitted or null.

## Reasoning quality: 0.88

This is a sound and well-grounded analysis, and the outcome bore out every piece of it.

What it got right:

- **Anchor.** It took the frozen band under the frozen version, pooled the bracketed `reached` figure over OT2017–OT2024 and arrived at 5.1 percent, which matches my own pooling to the rounding. It also correctly noted that the OT2025 row contains the case itself and must be excluded.
- **Vehicle reading.** Every negative it listed is in the provisioned record and correctly characterized: an unpublished per curiam affirmance "not designated for publication", a split section that concedes the circuits "have not reached a consensus, to the extent that they have reached the issue", a Part I that asks for Tolan-style error correction, no brief in opposition, no amici, no call for a response, and non-specialist counsel. Its reading of the panel opinion is accurate: the panel reached only the third prima facie element and did not get to the burden-shifting steps.
- **Mechanism.** The residual 1.2 percent is assigned to identifiable paths (a Rule 56 summary reversal; a late call for a response), and the document says where a reader should discount it.
- **Disclosure.** The retrieval section states what was looked up and that none of it moved the number, which is what a forward cell's prose should do.

Where I would discount it slightly: the claim that the disputed facts "go to elements the panel did not actually decide against her" is overstated. The panel did lean on the "quietly approached" and "four-and-a-half hours" recitals in holding the treatment did not rise to the level that would force her to leave, so the facts are not wholly orthogonal to the holding. The holding also rested on her concessions about the dress code and the service she received, so the candidate's conclusion that a Tolan correction was unlikely still stands; the premise was just stated more cleanly than the opinion supports. The dissent-from-denial figure (4 percent) is a judgment call with no rendered rate to check against, but it is in the plausible range for a baseline-band paid petition.

I did not score `predicted_reasoning.md` or the claims block; the forecast was read only for context on how the number was formed.

## Leakage

Mode `forward`, so the default is `not_applicable`. I checked rather than stamped it: the prediction was created 2026-09-17, eighteen days before the denial; the log is fully captured and shows one corpus query for 2020s granted priors, a docket-entries call (0 rows), two CourtListener searches (both 0 results), and a dockets item read whose only legible date is the 2026-06-01 filing date, with the candidate reporting `date_terminated` null. No web search, no read under `data/qp-topics/`, nothing dated at or after resolution, and the reasoning reads nothing off a decided docket. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big-case read

My independent read is 0.08: a single-plaintiff, fact-bound section 1981 restaurant case on an unpublished per curiam, with no opposition, no amici, and a silent denial. The statutory question has some doctrinal interest but this vehicle carried none of it to the Court.
