# Reasoning — P(disturbed) = 0.88, judgment `vacated`

**Inputs used.** Snapshot `2026-08-26.json` (cutoff 2026-08-26, forward mode);
provisioned `questions-presented.txt`, `petition.txt` (skimmed),
`merits-brief-petitioner.txt` and `merits-brief-respondent.txt` (summaries of
argument, statement, conclusions read). The Court-appointed amicus's brief, filed
on 2026-08-25, is a docket line only — its text was not provisioned and I did not
retrieve it, nor the October 13, 2026 argument. No CourtListener or corpus
`query` retrieval was done; this forecast rests on the provisioned record.

**Anchor.** `metrics/statpack.md`, "The merits docket (granted cases)", which
publishes an `excluded` count and so is quotable. Grant date 2026-04-20 → grant
Term 2025. Pool over grant Terms 2015–2024 strictly before; the table carries no
parsed rows for 2015–2016, so the pool is 2017–2024: 360 disturbed / 516 parsed
= **69.8%** (coverage: parsed is 516 of 539 granted across those Terms, well above
the 30-judgment floor).

**Adjustments up.**
- *Confession of error.* The respondent United States agrees the judgment
  should be vacated (its brief argues Stinson must be read in light of Kisor and
  the Fifth Circuit erred by deferring reflexively). When both parties seek
  vacatur and the Court appoints an amicus to defend the judgment, the Court
  disturbs the judgment in a strong majority of cases.
- *The grant itself.* The Court rewrote the QP to ask whether Stinson "still
  correctly states the rule" — a framing that signals at least some Justices see
  Kisor/Loper Bright tension. Seven distributions preceded the grant.
- *Paths to vacatur are many.* Whether the Court adopts petitioner's no-deference
  rule, petitioner's alternative Kisor rule, or the SG's Kisor-limits position,
  each requires vacating a judgment that rested on Vargas's reflexive deference.
  Only the amicus's position (Stinson survives intact) or an affirm-on-harmlessness
  route preserves the judgment.

**Adjustments down / uncertainty.**
- *Harmlessness.* The district court stated it would impose the same sentence
  regardless of the guideline range, and the SG concedes resentencing is unlikely
  to change anything. A Justice or majority could affirm on that ground, or the
  Court could DIG once the vehicle problem is ventilated at argument. The Court
  usually declines first-view harmless-error rulings, which is why I do not shade
  further.
- *Kisor may favor the commentary.* The SG argues commentary will "frequently"
  warrant deference; a majority could hold Kisor applies but that Application
  Note 2 is a reasonable reading of a genuinely ambiguous term and affirm. I put
  this at a few percent; the Court is a court of review and the lower courts never
  ran the Kisor analysis.
- I have not seen the amicus brief or the argument, so a strong amicus showing
  is unpriced.

Net: from 0.70 to 0.88. Votes: all nine in the majority on the judgment
(confidence 0.7 overall; Alito is my likeliest dissenter if one appears).
`big_case_score` 0.55: an important cross-cutting sentencing-law rule, but not a
headline case.

The cert band in `context.json` (`high`, sal-v4) scores grant likelihood and is
not used here, per the merits-stage rule.
