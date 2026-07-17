# Hughes v. Locure, No. 25-1242 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.07.**

## The case

Petitioner is the estate of Edwin Dewayne Moss, killed on January 19, 2021 when
Macon County, Alabama Deputy Sheriff Darian Locure — intoxicated, off any
official business, driving his patrol truck at ~70 mph in a 25-mph zone at
night with no headlights — struck the car in which Moss was a passenger, then
fled the scene. Locure was indicted for reckless manslaughter and later died;
his estate is the respondent. The § 1983 claim asserts a Fourteenth Amendment
substantive due-process violation (bodily integrity). The district court
denied qualified immunity at the motion-to-dismiss stage. A divided Eleventh
Circuit panel reversed (Hughes v. Locure, 166 F.4th 121 (11th Cir. 2026),
Brasher, J.): assuming the conduct shocks the conscience, the right was not
"clearly established" under circuit precedent (Cannon, Rooney), and
out-of-circuit authority (Browder (10th Cir. 2015, Gorsuch, J.); Dean (4th
Cir. 2020)) cannot clearly establish law. Chief Judge Pryor concurred,
doubting Locure even acted under color of state law. Judge Jordan dissented on
obvious-clarity grounds.

The petition (filed by Morgan & Morgan, a personal-injury firm, not a Supreme
Court specialist shop) presents whether Lewis footnote 13 (County of
Sacramento v. Lewis, 523 U.S. 833, 854 n.13 (1998) — "intentional misuse" of a
police vehicle) clearly established the right, and whether the Eleventh
Circuit's holding splits with Browder and Dean.

## Base rates

From the committed statpack (live/historical slice, denial-reweighted):
modern discretionary-cert petitions grant at ~3% overall (Term 2025: 2.5%;
2024: 3.0%; 2023: 3.3%). This is a **paid** petition — paid-class grant rates
run ~5.4% (T2025) and ~6.9% (T2024) per the statpack JSON's fee-class detail.
Eleventh Circuit petitions in the modern-cert cut grant at 4.4%. The docket
shows **zero relists** so far (just distributed July 15 for the September 28,
2026 long conference) and **no CVSG**, so neither of the classic pre-grant
signals is present yet. (The statpack version in this checkout carries no
salience-band table; I anchored on the paid fee-class rate as the closest
available yardstick for a selected paid petition.)

## Grant-positive factors

- **A genuine, crisply framed circuit conflict.** The Eleventh Circuit's
  published holding is difficult to reconcile with Browder (10th Cir.) and
  Dean (4th Cir.) on materially similar facts — off-duty/non-emergency officer
  driving that kills a bystander — and the Seventh Circuit (Flores, 2021)
  leans the plaintiffs' way too. The petition's split table is fair on the
  substance.
- **A published opinion with a forceful dissent** (Jordan, J.) explicitly
  endorsing the other circuits' approach — a classic certworthiness marker.
- **Vivid, egregious facts** that make the qualified-immunity result look
  stark, in the vein the Court has occasionally corrected summarily on
  obvious-clarity grounds (Taylor v. Riojas (2020)).
- **Fresh vehicle for the split**: my CourtListener checks found no prior
  SCOTUS petition out of Dean or Flores, so the Court has not obviously passed
  on this question before.

## Grant-negative factors

- **A serious preservation / party-presentation problem, well-executed in the
  BIO.** Respondent documents that petitioner relied *only* on the
  obvious-clarity prong below, never cited Browder or Dean to the Eleventh
  Circuit, expressly disclaimed the existence of materially-similar or
  broader-principle caselaw, and raises the Lewis footnote-13 theory for the
  first time at the cert stage. "Not pressed or passed upon below" is a
  denial-grade vehicle defect, and it also blunts the split (a future litigant
  can tee the theory up cleanly).
- **Antecedent merits questions make the vehicle messy**: the color-of-state-law
  issue is open (Pryor, C.J., flagged it), the case sits at the
  motion-to-dismiss stage on an interlocutory qualified-immunity appeal, and
  respondent has a live alternative-grounds argument (no substantive
  due-process claim at all; adequate state remedies under Parratt).
- **The Court's revealed preference in qualified-immunity cases** is to deny
  plaintiff-side petitions asking it to find rights clearly established, or at
  most to act summarily; it has turned away many QI-reform vehicles with far
  more amicus support than this one shows.
- **Factbound application**: whether one circuit's clearly-established
  analysis of unusual facts conflicts with another's is the kind of dispute
  Rule 10 treats as weak, and the BIO plausibly recasts the "split" as
  case-by-case application of Lewis's context-dependent test.
- **No specialist counsel, no visible amici, no CVSG, no relists yet**, and a
  first distribution to the long conference, where grant rates are depressed.

## Weighing

Start at the paid-petition anchor (~5–7%). The real split, published dissent,
and summary-reversal possibility push up; the preservation defect, the open
color-of-law question, the interlocutory posture, and the Court's consistent
reluctance in this space push down at least as hard. The likeliest path to
"granted" is not plenary review but a Taylor v. Riojas-style summary
disposition, which I fold into the probability. Net: **P(grant incl. GVR /
summary action) ≈ 0.07; predicted disposition: denied.** If the case is
relisted after the long conference, that would be a material upward update;
this prediction is made with zero relists on the docket.

No votes predicted: a denial produces no recorded merits votes, and I have no
basis to predict recorded dissents from denial.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), the questions
presented, the full petition text, and the full brief in opposition
(`record/documents/`). Retrieval beyond the provisioned inputs is logged in
`retrieval.md`. I have no prior knowledge of this case's outcome; it is
genuinely pending (forward mode) as of 2026-07-17.
