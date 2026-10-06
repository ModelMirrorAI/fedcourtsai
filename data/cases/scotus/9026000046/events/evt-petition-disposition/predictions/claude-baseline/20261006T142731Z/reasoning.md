# Rationale for the numbers

**P(any grant) = 0.60; predicted disposition `gvr`; granted = 1.**

## What I read

Provisioned inputs: `record/snapshots/2026-10-06.json`, `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, `signals_observable: true`), `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (80 pages, text extracted, not truncated; it carries the Second Circuit summary order as Appendix A). `documents.json` lists no brief in opposition, which matches the docket: the City waived on August 6, the Court called for a response on September 8, and the response is now due November 23, 2026. So my read of the City's position is inference, not text.

## Anchor

The statpack's "Segment base rate by salience band (sal-v4)" table matches my context's salience version, and my band is `baseline`. Pooling the bracketed `reached` figure over the nine prior Term rows the table renders (OT2017 through OT2025, n from 1140 to 1739 per Term) gives a weighted rate of about **5.0%**. That is the yardstick the evaluator scores against, and it is where I start. The modern discretionary-cert split (grant 655, GVR 577 among roughly 43,700 resolved) and the relist cut (relist bucket 1: granted 8.2%, GVR 5.1%) are consistent with a low prior for a once-distributed paid petition.

## Why I move far above the anchor

1. **A directly on-point merits case is pending and the petition asks to be held for it.** *Viramontes v. Cook County* (No. 25-238) was granted June 30, 2026, consolidated with *Grant v. Higgins* (No. 25-566), with argument set for December 2, 2026 and review limited to whether the Second and Fourteenth Amendments protect AR-15-platform rifles "in common use." *Grant* arrives from the Second Circuit under the same *Antonyuk* / *NAGR v. Lamont* / *Gomez* framework the summary order below applied, in which "common use" is a step-one burden on the plaintiff. Whatever the Court says about where common use sits and who bears the burden speaks to the only ground the courts below relied on. The Court holds generously for pending Second Amendment merits cases and has GVR'd the held petitions after each of *Bruen* and *Rahimi*; the baseline band rate does not see this feature at all.

2. **The call for a response after a waiver is the Court's own signal of attention.** The statpack carries no response-requested cut, so I cannot quote a committed rate for it, but a CFR is a necessary step before any grant or GVR over a waiver and moves a petition out of the summary-denial pile. It is also consistent with a clerk flagging the petition as a hold candidate.

3. **The petition's substantive profile is strong.** *Caetano v. Massachusetts* (2016) already summarily vacated a state high court ruling that denied Second Amendment protection to stun guns; the petition is credibly framed as "Caetano 2.0." Counsel is Cooper & Kirk (David Thompson), with Second Amendment Foundation and Firearms Policy Coalition as institutional petitioners, and two cert-stage amicus briefs are already on file. The lower courts never reached the historical step, so the record problem the summary order identified (no evidence of common use introduced below) disappears if the burden belongs to the government.

4. **Wolford v. Lopez (June 25, 2026)** gives the petition a fresh intervening-development hook: the majority treated the challenged conduct as within the plain text and the Barrett concurrence criticized lower courts for importing regulatory limits into the plain-text stage. On its own that would support at most a weak GVR argument; combined with the pending *Viramontes*/*Grant* it strengthens the hold case.

## How I arrived at 0.60

Rough decomposition: P(the Court holds rather than denies at the January conference) ≈ 0.85. Conditional on a hold, P(a *Viramontes*/*Grant* outcome favorable enough that the Court GVRs the held arms-ban petitions) ≈ 0.75, and the Court GVRs this one given that ≈ 0.9; if *Viramontes* is narrow or fractured (≈ 0.10) a GVR is still more likely than not; if it affirms the bans (≈ 0.15) this petition is most likely denied. That gives roughly 0.65 through the hold path, plus a few points for a summary reversal or plenary grant before or instead of the hold. I shade down to **0.60** for things I cannot see: the City's brief in opposition, which will press the Rule 56 framing (petitioners simply failed to put in evidence) and the unpublished, non-precedential form of the order; the possibility that the clerks treat a record-failure summary order as a poor hold candidate; and the general unpredictability of clean-up orders after a fractured merits opinion.

## Claims

- `disposition` 0.60, equal to `probability`.
- `relist-increment` 0.97: one distribution shown; a CFR with a November 23 response date guarantees redistribution unless the petition is withdrawn or dismissed, which is rare for an institutional petitioner.
- `cvsg-increment` 0.03: no federal interest, no federal party, and a pending merits vehicle already on the question.
- `summary-disposition-route` 0.88, conditional on grant: almost all of my grant mass is a GVR riding *Viramontes*/*Grant*, with a small summary-reversal slice; plenary review is the residual.
- `dissent-from-denial` 0.45, conditional on denial: Justice Thomas writes often on arms-ban denials and *Caetano* is his and Justice Alito's; but a denial that follows a fresh merits opinion on common use frequently passes without writing.

## Big case score

0.45. The stakes are real (a non-lethal arms ban in the largest US city; the common-use placement question controls every arms-ban case), but the modal GVR disposition would make this case a footnote to *Viramontes*/*Grant* rather than a decision of its own.

## Where to discount me

- I know the content of *Wolford* and of the *Viramontes*/*Grant* grant only from the petition and from web search summaries, not from the opinion text; if *Wolford* said less about the plain-text stage than the petition suggests, item 4 is weaker, though item 1 does not depend on it.
- The statpack publishes no response-requested or hold-pending cut, so the single largest adjustment I make rests on my general knowledge of the Court's practice with held petitions, not on a committed base rate.
- The mode is forward, so everything retrieved is pre-outcome; nothing I saw revealed a disposition, and the snapshot (polled today) shows the petition pending with a response due November 23, 2026.
- Corpus freshness: the `fedcourts query` priors were read through the cell's corpus service; I did not run `corpus-info`, so I quote no corpus vintage beyond the snapshot date of 2026-10-06. The GVR priors it returned (recent OT2025 GVRs) were not informative about this case and did not move the number.
