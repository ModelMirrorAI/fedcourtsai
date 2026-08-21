# Rationale for the numbers — claude-baseline, run 20260820T181919Z

## The anchor

`record/context.json` freezes this cell at band `baseline` under `sal-v3`,
which matches the committed statpack's band table version, so I anchor on the
baseline band's bracketed `reached` rate pooled over the rendered Terms
strictly before this case's Term (2026): Terms 2017–2025, weighted by their
risk-set denominators, ≈ **6.5%** (individual Terms range 5.4%–7.9%,
pooled n ≈ 13,163). That is the rate a live paid petition that has reached
the baseline band actually faces, and the yardstick this cell is scored
against.

## Adjustments

**Up from 6.5%:**

- **Three cert-stage amicus briefs filed before the BIO** (Professors Vladeck
  and Finkelstein, and September Eleventh Families for Peaceful Tomorrows with
  66 victim families). Cert-stage amicus support is among the strongest
  observable grant signals and is not captured by the salience band, which
  keys on distributions and CVSG.
- **Originating court is the D.C. Circuit** — the highest-granting circuit in
  the statpack's reweighted cut (granted 5.5% vs. 1–3% elsewhere).
- **A sharply divided panel below.** Judge Wilkins's dissent called the
  majority "stunning" and charged it with creating two acknowledged circuit
  splits; rehearing en banc was sought and denied (Jan. 6, 2026).
- **Two genuinely pleaded splits**: QP1's conflict with the Tenth Circuit's
  McVeigh rule (no mandamus where Congress foreclosed interlocutory criminal
  appeals — an OKC-bombing-era holding the petition uses well) and QP2's
  three-way division on the "clear and indisputable" standard (4th/5th
  Circuits en banc vs. 2nd/8th).
- **Elite counsel and maximal salience** — Steptoe's Michel Paradis, the
  leading military-commissions appellate advocate, in the most watched
  criminal case in the country.

**Down toward the anchor:**

- **The Solicitor General won below and opposes.** The Court rarely grants
  over the SG's opposition in national-security criminal matters.
- **A two-decade pattern of staying out of Guantanamo.** The Court has denied
  certiorari on every military-commission mandamus dispute since Boumediene,
  including al-Nashiri and Baluchi from the same court below.
- **Interlocutory posture.** The commission proceedings continue; nothing
  forces the Court's hand now (though petitioners argue, with some force, that
  the government's asymmetric appellate rights mean the issue will never
  return in a cleaner posture).
- **Vehicle entanglement.** Both QPs are wrapped in the commissions' unique
  appellate structure (10 U.S.C. § 950d), letting the Court treat the splits
  as not squarely presented.
- **The equities of the bottom line.** A grant would put the Court in the
  position of potentially reinstating plea agreements that spare the accused
  9/11 plotters capital punishment — an outcome several Justices will not
  want to own, and cert votes are discretionary.
- **Kavanaugh's recusal** from the sealing motion, if carried to the petition,
  leaves eight Justices and one fewer potential grant vote.

Net: **P(grant family) = 0.10**, `predicted_disposition` = `denied`,
`granted` = 0. The up-adjustments justify well above the 6.5% anchor; the
GTMO-aversion track record and SG opposition keep me from the ~20%+ a
split-plus-dissent-plus-amici petition might otherwise earn.

## The other claims

- **relist-increment 0.97.** The frozen `distribution_count` of 1 is the
  sealing motion's June 10 distribution; the petition itself has not yet been
  conferenced and the BIO is due Aug. 26, 2026. A petition distribution
  (raising the count past 1) is near-certain; the residual covers withdrawal,
  dismissal, or a summary disposition without a further recorded
  distribution. See flags.json on the count's semantics.
- **cvsg-increment 0.01.** The United States is the respondent; a CVSG cannot
  issue. Stated near zero rather than at it only for resolution noise.
- **summary-disposition-route 0.03** (conditional on grant). No intervening
  decision exists to GVR against, and the questions presented are
  jurisdictional/structural — plenary material.
- **dissent-from-denial 0.15** (conditional on denial). Noted dissents are
  rare in the population at large, but this petition is at the extreme of
  salience and raises an institutional question (government mandamus as
  substitute for appeal, in a capital case) that has drawn separate writings
  from the current Court's left flank.

## Uncertainties and discounts

- **I predict before the opposition exists.** The BIO is due six days after
  my snapshot; I have the petition's account of the case and the D.C.
  Circuit's published opinion posture, but not the government's cert-stage
  argument. My read of the opposition is inference, not text.
- **The distribution-count semantics** (motion vs. petition) mean the
  relist-increment claim is stated from a count whose one unit is not a
  petition conference; if the resolver counts only petition distributions,
  the increment is still near-certain, so the claim is robust either way.
- **Training-data familiarity.** This case was extensively covered through my
  knowledge cutoff (the D.C. Circuit's July 2025 ruling and the January 2026
  en banc denial). The cert petition's disposition post-dates everything I
  could know and the docket confirms it is pending, so no outcome knowledge
  exists to leak; background familiarity with the plea-deal controversy is
  pre-snapshot public context, used as legitimate forward signal.
- **Sample-size caveat on the CADC cut**: the circuit cut's grant rates are
  reweighted estimates on modest per-circuit denominators; I used it
  directionally, not as a multiplier.
