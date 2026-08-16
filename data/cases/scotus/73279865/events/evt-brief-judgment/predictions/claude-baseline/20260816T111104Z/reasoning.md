# Rationale for the numbers (evt-brief-judgment, claude-baseline)

**P(disturbed) = 0.78; judgment = reversed; votes = 9–0 majority.**

## Anchor

The committed `metrics/statpack.md` merits section ("The merits docket
(granted cases)") publishes an `excluded` count (67 pack-level, per-Term
column present), so its pooled rate is quotable and is the scored baseline.
This case's grant date is April 6, 2026 → grant Term 2025. Pooling `disturbed`
over `parsed` across the ten grant Terms strictly before (2015–2024; the pack
holds parsed rows for 2017–2024, and Terms with no parsed judgment are
omitted): disturbed 50+34+49+46+57+42+50+31 = 359 over parsed
73+55+72+65+69+54+75+52 = 515 → **69.7%**, comfortably over the 30-parsed
floor. That is the bar my Brier skill is scored against.

## Adjustments from the anchor

Up from 0.697 to 0.78, on:

- **Minority-side grant on a lopsided acknowledged split.** The petition
  documents a 6–2 circuit split with the Eleventh Circuit (joining the Eighth)
  against six circuits that retain district-court jurisdiction. Grants from
  the minority side of a lopsided split disturb more often than baseline.
- **An on-point unanimous precedent runs petitioner's way.** *Johnson v.
  Robison* construed the predecessor no-review clause not to reach
  constitutional challenges to acts of Congress, and the VJRA retained the
  operative "decision ... of the Secretary ... under a law" language. The
  reenactment-era textual argument is strong for petitioner.
- **Doctrinal trajectory.** *Axon v. FTC* (2023) was a unanimous
  pro-district-court-jurisdiction result on channeling of constitutional
  claims with this bench; the pro-veteran access-to-courts framing helps too.
- **One-sided merits amicus field.** Nine-plus amicus briefs on the
  petitioner-side schedule spanning veterans' organizations (NVLSP, MVA,
  law-school veterans clinics), libertarian/anti-channeling groups (IJ, NCLA,
  PLF, WLF, NCLA), NTEU, and the Federal Circuit Bar Association; as of the
  August 16 snapshot no amicus appears on the respondent-side schedule
  (respondent's brief was filed July 13; that window has passed).
- **Elite petitioner representation** (Stanford Supreme Court Litigation
  Clinic with Bondurant Mixson).

Back down from where those signals alone would put it (~0.85), on:

- **The SG acquiesced in cert while defending the judgment.** The brief in
  opposition expressly said review is warranted and the petition should be
  granted. This is not the classic grant-over-opposition-to-reverse setup;
  the Court may have taken the case as much because both sides sought
  resolution as to fix the minority rule.
- **The government's merits position is substantial.** § 511(a)'s "all
  questions of law ... necessary to a decision by the Secretary" wording
  differs from the § 211(a) text *Robison* construed (the Eleventh Circuit
  called the scheme "materially different"), and § 7292(c) expressly empowers
  the Federal Circuit to decide statutory validity — a real *Elgin*-style
  channeling argument, from a Court that decided *Elgin* for channeling.
- **Recent veterans cases** (*Arellano*, *George*, *Bufkin*) have gone against
  the veteran, though all were statutory-benefits merits questions rather
  than jurisdiction-stripping.

Net: 0.78.

## Vote block and confidence

All nine Justices predicted `majority`: I expect an *Axon*-like unanimous or
near-unanimous reversal, and for each individual Justice P(in the majority) is
well above one half even under the divided branches. The likeliest single
dissenter, if any, is Thomas (author of *Elgin*), discussed in
`predicted_reasoning.md`. `confidence` 0.6 reflects genuine uncertainty about
the lineup shape rather than the direction. No `writing` values are forecast.

## What I worked from, and where to discount

- **Inputs:** the provisioned snapshot (full docket through the Aug 12 reply
  brief and the Aug 4 argument setting), the petition text, the questions
  presented, and the provisioned respondent-side text — which concatenates the
  March 6 cert-stage BIO and the July 13 merits brief for respondent (I read
  the merits brief's summary of argument directly, so the government's actual
  merits theory is on my desk, not inferred). I did **not** retrieve
  petitioner's merits brief or the amicus briefs; my read of petitioner's
  merits theory is from the petition, whose argument section the merits brief
  presumably tracks. This is a forward cell, so that was a budget choice, not
  a leakage constraint.
- **Mode:** `forward` — the judgment does not exist yet (argument is set for
  October 5, 2026). Nothing outcome-revealing was encountered.
- **Salience band:** context carries `band: elevated` (sal-v3); per the
  stage rule it scores the settled grant question and I did not anchor on it.
- **Corpus retrieval:** one `fedcourts query` by citation ("415 U.S. 361")
  returned no rows — the citation column is sparse (161 of 590k SCOTUS rows),
  a coverage gap, not evidence of no precedent. I did not retry sparse
  filters and used the committed statpack for all base rates.
- **Discount where:** my split-direction and amicus-asymmetry adjustments are
  judgment calls without a committed conditional cut behind them; and the
  government's textual distinction of *Robison* is the kind of argument this
  Court sometimes accepts (an affirmance here would look like *Elgin*
  redux). If the Court divides on the *Thunder Basin* framework's
  applicability, my all-majority vote block loses a Justice or two.
