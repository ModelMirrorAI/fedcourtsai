# Rationale for the numbers

**P(grant) = 0.20; predicted disposition: denied.**

## Anchor

Cell: forward mode, cert stage, `moment: distribution`, OT2026, paid docket.
`record/context.json` carries `band: baseline` under `sal-v4`, which matches
the statpack's band table version, with `distribution_count: 1` and no CVSG.
The anchor is therefore the `baseline` column's bracketed `reached` rate
pooled over the Term rows strictly before OT2026 that the table renders
(OT2017 through OT2025; OT2026's row is empty):

| Term | reached rate | n |
| --- | --- | --: |
| 2025 | 3.9% | 1140 |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Weighted pool: roughly 637 grants over 12,720 petitions, about **5.0%**. That
is the yardstick this cell is scored against. The relist-count cut (one
distribution: granted 8.2%, gvr 5.1%) and the CVSG cut (none: granted 4.0%,
gvr 2.3%) describe terminal buckets and sit in the same neighborhood; the
Ninth Circuit's originating-circuit rate (granted 2.1%, gvr 1.1%) is a
whole-docket figure diluted by IFP filings and is below the paid-segment anchor.

## Adjustments upward

- **The Court requested a response after Paramount waived** (August 17, 2026).
  That is the strongest pre-relist signal on a cert docket: a paid petition
  that draws no response is almost never granted, and a call for a response is
  an affirmative act by at least one chambers. The salience band does not key
  on it, so the baseline anchor understates this petition's position. This is
  the bulk of my move from 5% to 20%.
- **Three cert-stage amicus briefs**, all filed before the response request:
  the National Society of Entertainment and Arts Lawyers, Professors Daryl Lim
  and Eugene Volokh, and the Music Artists Coalition with the Independent Book
  Publishers Association. Cert-stage amici on a private copyright petition
  signal that the bar treats the question as recurring, which supports the
  petition's importance section.
- **Counsel.** Jeffrey Lamken (MoloLamken) is counsel of record, with Alex
  Kozinski, a former Ninth Circuit chief judge, on the brief. Paramount has
  retained Anton Metlitsky (O'Melveny) for the response, so the opposition will
  be serious, but the matching of elite counsel is itself a marker that both
  sides see grant risk.
- **A clean, published vehicle.** The Ninth Circuit opinion (163 F.4th 685,
  Judge Miller for a unanimous panel with Judges Hurwitz and Sung; confirmed
  published on CourtListener) resolved the case on the extrinsic test at
  summary judgment alone. Copying and copyrightability were not disputed, the
  split was pressed in the en banc petition, and no alternative ground
  (fair use, thin copyright for software, de minimis use) complicates review.
- **The split is real and old.** The petition's account of the Ninth, Fourth
  and Eighth Circuits' extrinsic/intrinsic dissection versus the Second, Third,
  Fifth, Seventh and D.C. Circuits' ordinary-observer test is a fair reading of
  the case law, and the two largest copyright circuits sit on opposite sides.

## Adjustments back down

- **The Court has let this split sit for decades.** Petitions attacking the
  Ninth Circuit's substantial-similarity methodology have been denied before
  (the Led Zeppelin "Stairway to Heaven" petition in 2020 is the recent
  example). The Court's copyright docket has favored statutory questions (fair
  use, registration, remedies) over infringement methodology, which it may view
  as fact-bound and ill-suited to a clean rule.
- **The BIO will have good material.** Paramount can argue the split is
  largely verbal: every circuit filters unprotectable elements, the Second
  Circuit's "more discerning observer" test does the same work as the
  extrinsic test where a work mixes protected and unprotected material, and
  the Ninth Circuit here expressly addressed selection and arrangement. It can
  also argue the result would be the same under any test because "Top Guns" is
  a nonfiction article about a real training program, so the shared material
  is largely factual. The response has not been filed (due October 16, 2026),
  so I am weighing the opposition from the docket and the opinion, not from its
  text; `documents.json` lists no BIO.
- **Fact-bound posture.** A nonfiction magazine article versus a feature-film
  sequel invites the Court to see the dispute as a case-specific application
  rather than a test case, and the panel's reasoning leaned on the factual
  nature of the overlaps.
- **Base rate discipline.** Even with a response request, most such petitions
  are denied. I treat the response request as moving this petition into a
  population that grants at roughly one in six to one in eight, and the amici,
  counsel and vehicle quality as pushing to about one in five.

## The other claims

- **relist-increment 0.97.** One distribution shown; the response request
  pulled the petition from the September 28 conference, so a fresh
  distribution after the BIO and reply is near-certain barring withdrawal.
- **cvsg-increment 0.12.** No federal interest or agency role; the Court
  occasionally invites the Solicitor General on recurring IP methodology
  questions, which keeps this above the no-CVSG floor but low.
- **summary-disposition-route 0.03 (conditional on grant).** No intervening
  decision to GVR against; not a summary-reversal shape.
- **dissent-from-denial 0.08 (conditional on denial).** No Justice has a
  staked position on this test; a statement respecting denial is possible but
  not expected.

## Uncertainty and where to discount me

- The main uncertainty is how the Court weighs the "split is illusory"
  argument the BIO will make against a petition that frames the conflict well.
  My 0.20 could reasonably be 0.15 or 0.28.
- I have not read the BIO, because it does not exist yet.
- The corpus query (`fedcourts query --court scotus --disposition granted
  --era 2020s --limit 8`) returned rows without captions or topics, so it gave
  me no subject-matched priors; the base-rate work rests on the statpack.
- I know nothing about this petition's disposition from training; the docket
  is pending and the live supremecourt.gov page matched the snapshot exactly.

## Stakes

`big_case_score` 0.55: the caption is famous and the question governs nearly
every copyright infringement case, but it is a methodological ruling, not a
headline constitutional or statutory question.
