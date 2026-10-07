# Evaluation: codex-baseline — scotus/73500242, evt-petition-disposition

## Outcome and scoring

Cert-stage cell, forward mode. The petition (No. 25-1340, Nwosu v. 1600 West Loop South) was distributed once, for the September 28, 2026 conference, and denied on October 5, 2026 with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- **Disposition:** predicted `denied`, actual `denied` → `correct` = 1.
- **Brier:** probability 0.025 → (0.025 − 0)² = **0.000625**.
- **Segment base rate (`risk_set`):** the prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is rendered under sal-v4, so the risk-set basis applies. Pooling the baseline band's bracketed `reached` figures, resolved-weighted, over every rendered Term strictly before the case's Term (OT2025), i.e. OT2017–OT2024 (11,580 weighted resolved), gives **0.05121** (593.0 / 11,580 from the unrounded `metrics/statpack.json` rows; the rendered percentages give 0.05120). The table renders "most recent 10 of 10 Terms", so the rendered window is the whole pack and matches the configured ten-Term lookback; no window divergence to flag.
- **Brier skill:** baseline Brier = 0.05121² = 0.002622; 1 − 0.000625 / 0.002622 = **0.762**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; omitted or null.

## Reasoning quality: 0.85

A careful, well-sourced analysis whose conclusions the outcome bore out. It is the most precise of the three in its reading of the lower-court opinion and the most explicit about what it did not know.

What it got right:

- **Anchor.** It pooled the baseline band's `reached` figure over OT2017–OT2024 from the unrounded JSON rows (593 / 11,580 = 5.12 percent), which is exactly the number I computed, and it said why the terminal rate and the modern-cert and circuit tables are not substitutes for the matched risk set. It also correctly refused to read the terminal relist buckets as forward transition probabilities.
- **Panel reading.** Its account of the Fifth Circuit opinion is the most accurate of the three: the panel reached only whether the discrimination concerned an enumerated activity, did not reach the burden-shifting steps, recognized benefits beyond the meal, and found neither a denied cognizable benefit nor harassment severe enough to force departure. It also correctly observed that the petition's "categorical requirement to leave" framing is broader than the panel's wording, which weakens the petition's text-versus-precedent argument.
- **Split check.** It pulled Christian v. Wal-Mart from CourtListener, read the "markedly hostile" passages, and concluded that the Sixth Circuit case involved a shopper forced to leave, so it does not establish the square conflict the petition implies. That is doing the work rather than taking the petition's word, and it is a correct conclusion.
- **Candour.** It states what it did not check (the other cited circuits), what it could not see (no brief in opposition, no photographs), and that no outcome was encountered.

Where I discount it: the cut from 5.1 to 2.5 percent is gentler than the record warrants. The document itself lists an unpublished unanimous application of circuit precedent, an error-correction petition, no demonstrated split, no opposition, and no attention signal, then gives "limited weight" to the record's silence "given the record's sparsity". A docket that is sparse because nobody opposed, no amicus filed, and the Court did not call for a response is not an uninformative docket; it is the informative shape of a weak petition. The result is a probability about twice claude-baseline's for a vehicle the candidate assessed, in substance, the same way. The prose is also denser than it needs to be, and the stakes paragraph (0.40 significance) reads the question's abstract breadth rather than this vehicle's, though that is the big-case dimension rather than the grant analysis.

I did not score `predicted_reasoning.md` or the claims block.

## Leakage

Mode `forward`, so the default is `not_applicable`. I checked rather than stamped it: the prediction was created 2026-09-17, eighteen days before the denial. Coverage is 0.92: the two unobserved rows are web searches whose queries concern Supreme Court Rule 10 and the Rules of the Court PDF, not this case, and the candidate reports both returned nothing usable; every captured call reads the provisioned record, the statpack, or the one CourtListener opinion lookup of Christian v. Wal-Mart (6th Cir. 2001), a 2001 authority. One shell call contains a `find` expression that names `data/qp-topics/` only to exclude it from the search; that is not a read of the path and I do not count it as one. Nothing is dated at or after resolution, and the candidate states it did not search for the disposition. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big-case read

My independent read is 0.08: a single-plaintiff, fact-bound section 1981 restaurant case on an unpublished per curiam, with no opposition, no amici, and a silent denial. The statutory question has some doctrinal interest but this vehicle carried none of it to the Court.

## Data note

The candidate flagged that the snapshot's proceedings list dates the petition filing April 13, 2026 while the PDF and docketing point to May 26 / June 1. I see the same thing in my cell's snapshot and have recorded it in this run's `flags.json` as an info-level data-quality note.
