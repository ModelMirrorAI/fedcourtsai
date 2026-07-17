# Zook v. Fuqua, No. 25-1108 — cert petition disposition

## The case

Three Santa Fe County deputies petition from *Fuqua v. Santa Fe County
Sheriff's Office*, 157 F.4th 1288 (10th Cir. Nov. 4, 2025) (rehearing en banc
denied Dec. 22, 2025), a divided published panel that affirmed the denial of
qualified immunity at the Rule 12(b)(6) stage in a § 1983 fatal-shooting suit.
The decedent, Jason Roybal, led officers on a vehicle pursuit, fired what
turned out to be a BB gun at officers from the car, then fled on foot toward
an occupied civilian vehicle after dropping the gun; officers shot him as he
ran. The operative (First Amended) complaint pleaded only that he was
"unarmed and fleeing," omitting the chase, the shot fired at officers, and
the occupied vehicle. The full encounter is on three dashcams and three
bodycams, which both sides placed in the record and which plaintiff's counsel
admitted using to draft the complaint. The district court and the Tenth
Circuit majority refused to look at the videos at the pleading stage and held
the complaint plausible and *Tennessee v. Garner* clearly established the
violation. Judge Tymkovich dissented on both points.

## Questions presented

1. Whether courts may (or must) consider objective video evidence at the
   12(b)(6) stage when it is central to the complaint and blatantly
   contradicts its allegations, given an acknowledged split (6th/11th
   Circuits yes; 10th Circuit no).
2. Whether a plaintiff can satisfy *Iqbal*/*Twombly* plausibility by
   strategically omitting known dispositive facts.
3. Whether *Garner* alone can clearly establish the law at the pleading
   stage in a factually complex shooting, contrary to *White v. Pauly* and
   *Rivas-Villegas*.

## Signals pointing toward a grant

- **Call for response.** Respondent initially did not respond; the petition
  was distributed for the May 21, 2026 conference and the Court then
  requested a response (May 15). A CFR means at least one chambers took an
  interest — historically it multiplies the paid-petition grant rate several
  times over.
- **Published, divided panel with an acknowledged split.** The majority
  expressly declined to follow the Sixth Circuit's blatant-contradiction rule
  (*Bell v. City of Southfield*, *Saalim*) and the Eleventh Circuit
  (*Johnson v. City of Atlanta*); Judge Tymkovich's dissent tracks the
  petition's theory. QP1 presents a genuine, recurring methodological
  question in the age of ubiquitous bodycams.
- **Officer-side qualified-immunity petition.** The Court has repeatedly
  intervened — often summarily — where circuits define clearly established
  law at *Garner*-level generality (*White*, *Kisela*, *City of Tahlequah*,
  *Rivas-Villegas*, *Mullenix*), which makes a summary reversal or GVR-style
  disposition a live tail scenario here, not just plenary review.

## Signals pointing toward denial

- **The BIO reveals a serious vehicle problem.** Respondent has already
  moved — unopposed — for leave to file a Third Amended Complaint in the
  district court, and the order allowing it has been entered. The amendment
  pleads the previously omitted facts (the chase, the BB gun). The complaint
  the Tenth Circuit analyzed is no longer operative: QP2 (strategic
  omission) is largely mooted, and the pleading-stage rulings on QP1/QP3
  now address a superseded pleading. Clerks flag exactly this kind of
  intervening development, and it gives the Court an easy pass.
- **Interlocutory, pleading-stage posture.** The officers lose nothing
  permanently by a denial — the videos will indisputably be considered at
  summary judgment (*Scott v. Harris*), where they can renew qualified
  immunity on the full record. That undercuts urgency.
- **The split is contestable at the margins.** The BIO argues (with some
  force) that *Bailey* is an incorporation-by-reference case, that *Saalim*
  and *Chrestman* show the Sixth Circuit's rule often changes nothing, and
  that these videos do not "blatantly contradict" a complaint alleging
  Roybal was unarmed and shot in the back while fleeing — the Tenth Circuit
  panel said as much in the alternative (App. 15a). If the video would not
  alter the outcome even under the Sixth Circuit rule, the split is not
  outcome-determinative in this case.
- **The Court's appetite for QI summary reversals has cooled** in recent
  Terms relative to the 2015–2021 run of per curiams, and pleading-stage
  (rather than summary-judgment) QI vehicles are rarer grants.
- **Base rates.** Modern paid cert petitions grant at ~5.4% (Term 2025
  statpack; 6.9% in Term 2024). The petition has zero relists so far
  (relist bucket 0 base rate: <1% grant); the CFR is the main upgrade.

## Weighing

The CFR takes this well above the ordinary paid-petition baseline, and the
subject matter (video at the pleading stage; *Garner*-generality) is squarely
in the Court's recurring-interest zone. But the Third Amended Complaint is a
substantial vehicle defect that surfaced only in the BIO — the Court rarely
grants to review rulings about a superseded pleading when the same fight can
return cleanly (here, on a renewed motion against the TAC or at summary
judgment). The most likely path: distribution for the late-September long
conference, possibly a relist, then denial — perhaps with a statement or
dissent from denial by one or two Justices on the video question.

**P(any grant, including GVR/summary reversal) ≈ 0.10.** Predicted
disposition: **denied**. Confidence 0.6: the CFR keeps genuine upside risk
(a relist-then-summary-reversal on QP3, or a plenary grant limited to QP1,
would not shock), but the TAC development and posture make denial the clear
modal outcome.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-16.json` (docket through the
  July 15, 2026 BIO filing) and `record/context.json` (mode: forward).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (full 33-page petition).
- The BIO itself, fetched directly from the supremecourt.gov docket link in
  the snapshot (its text was not provisioned; forward-mode retrieval — see
  `retrieval.md`). This is the source of the Third Amended Complaint fact
  that materially lowered my probability.
- Committed `metrics/statpack.md` / `statpack.json` for base rates (paid vs
  IFP, relist, CVSG, circuit cuts).
