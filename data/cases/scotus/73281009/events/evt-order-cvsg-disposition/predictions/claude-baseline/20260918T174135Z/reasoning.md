# Why 0.55

## What I read

Provisioned inputs: `record/context.json` (mode `forward`, band `high` under `sal-v4`,
`distribution_count` 2, `cvsg_date` 2026-06-29, term 2025, cutoff 2026-06-30, cut kind
`date`), the snapshot `2026-06-30.json`, `questions-presented.txt`, `petition.txt`
(45 pp., full text), and `brief-in-opposition.txt` (a 94-page concatenation of five
respondent filings: Luzerne County in opposition, the Eakin/DSCC/DCCC/AFT-PA brief in
opposition, and briefs from Lehigh, Bedford et al., and York counties). None was
`empty_text`. The event is a `cert`-stage, `moment: cvsg` cell, so the cert-v2 five-claim
set applies and the statpack's CVSG cut and band table are the anchors.

## Anchors

- **Band table (sal-v4, matches the context's version).** The `high` column's bracketed
  `reached` rate pooled over the eight rendered Terms strictly before OT2025
  (OT2017-OT2024, n = 898 weighted) is about **35%** (313.9 / 898). The case's own
  Term row (42.6%, n=68) is excluded by the leakage rule but sits above the pool.
- **CVSG cut (paid scored segment).** `cvsg` bucket: granted 29.4% + gvr 5.5% =
  **34.9%** grant family, denied 62.0%, dismissed 3.1% (n=163 resolved).
- **Relist bucket 2:** 40.9% grant family, but this docket's second distribution is
  the response-request cycle (4/17 pulled, redistributed 6/25), not two considered
  conferences, so I weight it lightly.
- **Corpus priors.** `fedcourts query --court scotus --era 2020s --disposition granted`
  returned recent granted priors (mostly OT2025 substantive applications and paid
  petitions); none is a CVSG'd election-law petition, so the query informed nothing
  beyond confirming the corpus's recent slice. `corpus-info` is not runnable in the
  cell, so I cannot state the blob vintage beyond the query rows' own dates.

Starting point: ~0.35.

## Adjustments up

1. **The SG's likely position.** The Court's grant rate after a CVSG is dominated by
   the SG's recommendation (historically roughly three-quarters when the SG says
   grant, a quarter or less when the SG says deny). The current SG's office is
   institutionally aligned with the petitioners' side of this dispute (state authority
   over ballot-casting rules, skepticism of Anderson-Burdick as applied by federal
   courts), and the co-petitioner in 25-962 is the RNC. I put P(SG recommends grant or
   GVR) at about 0.75. Composed: 0.75 x 0.78 + 0.25 x 0.30 = about 0.66 conditional on
   the case staying live.
2. **The Court's own signals before the CVSG.** Every respondent waived, and the Court
   called for a response anyway on 4/1; then at the 6/25 conference it chose a CVSG
   over a denial or the requested GVR. The Third Circuit panel itself acknowledged the
   circuit split (App. 41a n.35), rehearing en banc was denied over two dissents
   (Phipps, Bove), and the petitioner is a State represented by its Attorney General.
3. **Demonstrated interest of at least three Justices** in this exact requirement
   (*Ritter v. Migliori*, 2022 stay dissent by Alito, Thomas, Gorsuch), and Justice
   Alito is the Third Circuit's Circuit Justice.

## Adjustments down

1. **Vehicle: *Baxter* is still pending.** The Pennsylvania Supreme Court heard
   argument on 10 Sept. 2025 on whether the date requirement violates the state
   Free and Equal Elections Clause (the Commonwealth Court held it does). My forward
   retrieval found no decision as of today; a year's silence after argument suggests
   division. If it strikes the requirement before the Court acts, the federal question
   becomes academic and a denial is the likeliest response. I put roughly a quarter on
   a mooting event landing inside the disposition window, with P(grant family | mooted)
   about 0.2 (a vacatur route survives).
2. **The State is divided against itself.** The Secretary of the Commonwealth and most
   county boards disclaimed any interest in the date at every stage; the Luzerne and
   Eakin briefs press this hard. It weakens the merits side and gives the SG a
   principled reason to say deny, though it also makes the "standard, not the
   interest" framing of 25-962 the natural grant vehicle.
3. **The BIO's answer to the GVR request is strong**: the Third Circuit had *Coalfield
   Justice* before it when it denied rehearing, which distinguishes *Lords Landing*.

Blend: 0.25 x 0.20 + 0.75 x 0.66 = 0.545, rounded to **0.55**.

## The other claims

- `relist-increment` 0.96: redistribution after the SG brief is mechanical; the
  residual is a withdrawal or dismissal before the SG files.
- `cvsg-increment` 0.02: a CVSG is already on the docket, so the claim is vacuous and
  the harness masks it; the number is a formality consistent with prior CVSG cells.
- `summary-disposition-route` 0.30: the petition's lead ask is a GVR and the SG may
  recommend one, against the CVSG itself signalling plenary interest and the Court
  having declined to GVR at the 6/25 conference. The statpack's gvr share of grants
  runs 16% in the CVSG bucket and 35% in the `high` band; I sit between them because
  the intervening-state-decision hook is explicit here.
- `dissent-from-denial` 0.40: well above the population rate because of the *Ritter*
  trio; discounted because a denial that follows a *Baxter* mooting draws less writing.

## Disposition label

With P(grant) 0.55 the binary is `granted = 1`. Among labels, my split is roughly
`granted` (plenary) 0.38, `gvr` 0.17, `denied` 0.43, `dismissed` 0.02, so `denied` is
marginally the modal single label; I write `granted` because the field must agree
with the binary and it is the likelier grant route.

## Where to discount me

The forecast leans on two things I cannot observe: what the SG will say, and when the
Pennsylvania Supreme Court will decide *Baxter*. A reader who believes the SG's office
will treat the intra-state disagreement as a vehicle defect should shade toward 0.45;
one who thinks *Baxter* will not land before the Court acts should shade toward 0.62.
`big_case_score` 0.72 rests on the QP, the 7-4 split and the battleground-state
posture, not on grant odds.
