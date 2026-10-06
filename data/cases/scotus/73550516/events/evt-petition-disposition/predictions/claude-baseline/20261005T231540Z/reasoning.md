# Why 0.20, and not another number

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json` (three docket entries:
petition filed June 2, 2026 and docketed June 29; distributed August 12 for the
September 28 conference; response requested August 17, due September 16),
`record/context.json` (mode `forward`, band `baseline` under `sal-v4`,
`distribution_count` 1, no CVSG, Term 2025, no cutoff), the event definition
(`stage: cert`, `moment: distribution`), `record/documents/petition.txt` (45
pages, text extracted, no truncation) and `questions-presented.txt`. No brief in
opposition was provisioned, and none is on the snapshot — consistent with the
response having been requested on August 17 and not yet docketed as filed on
the snapshot date.

Beyond the provisioned inputs (all logged in `retrieval.md`): the Fifth
Circuit's *Town of Vinton* opinion (161 F.4th 282, December 8, 2025) and its
September 3, 2026 *Transportation Consultants* opinion, which records that the
insurers were still preserving the *Town of Vinton* question "for further
review" as of that date; CourtListener's docket record for this case (last
modified August 17, 2026, so nothing later is known to it); and the public
supremecourt.gov docket page for the lead case, No. 25-1383. The same page for
this case returned empty content twice, so this docket's post-snapshot state is
unknown to me beyond what CourtListener's modification date implies.

## The anchor

Band `baseline`, `sal-v4`, matching the statpack's segment table version. The
leakage-safe anchor is the bracketed `reached` rate for `baseline` pooled over
Term rows strictly before this petition's Term (2025), i.e. OT2017 through
OT2024:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Weighted pool ≈ 593 / 11,580 ≈ **5.1%**. That is the rate for a paid private
petition that reached the baseline band, and it is the yardstick I am scored
against. For shape only, the relist-count cut puts a petition at one
distribution and never relisted at a 1.7% grant family, and the CVSG cut's
`none` bucket at 6.3%; neither is my state once the response request is read.

## Why I move up, to 0.20

1. **This is a companion of No. 25-1383, and the lead case has a serious
   trajectory.** The petition itself asks to be held for *Indian Harbor v.
   Town of Vinton*. That docket (public page read October 5–6, 2026) shows:
   petition filed June 11 by Skadden (Shay Dvoretzky); respondents waived July
   2; distributed July 8 for September 28; two amicus briefs (the American
   Property Casualty Insurance Association, and a group of arbitration scholars
   led by Dr. Crina Baltag); **response requested July 27**; brief in
   opposition August 26; reply September 9. The corpus still lists its
   disposition event as open, and the Fifth Circuit's September 3 opinion
   treats it as pending. A response requested after a waiver, plus amici and
   repeat Supreme Court counsel, is the classic pre-grant shape short of a
   relist. I put the lead case's grant-family probability at roughly 0.30–0.35.
2. **The Court requested a response on this docket too.** On its own that is
   the strongest signal visible here — it means at least one chambers wanted
   the respondent heard before denial — and it is consistent with the Court
   treating the two petitions as a pair.
3. **The legal question is genuinely open at the Court's own invitation.**
   *GE Energy* (2020) held the Convention does not bar domestic equitable
   estoppel doctrines but declined to say which body of law governs. The
   petition claims a 4–1 split (CA1, CA2, CA4, CA9 federal common law; CA5
   state law). Reading *Town of Vinton*, the Fifth Circuit's state-law holding
   is a single sentence citing *Arthur Andersen v. Carlisle*, a Chapter 1 case,
   so the conflict is real if thin, and it was outcome-determinative there
   because the Louisiana Supreme Court's *Police Jury* decision forecloses
   estoppel under state law.
4. **The GVR channel.** If the lead case is granted and the Fifth Circuit is
   reversed or vacated (the ordinary outcome of a grant, roughly two in three),
   this held petition is GVR'd, and a GVR counts as a grant on the scored
   binary. Arithmetically: P(lead granted) ≈ 0.32 × [P(consolidated grant)
   ≈ 0.10 + P(held) ≈ 0.90 × P(reversal or vacatur) ≈ 0.68 × P(GVR follows)
   ≈ 0.95] ≈ 0.32 × 0.68 ≈ 0.22. I shade to 0.20 for the chance the lead case
   settles or is dismissed during the hold, and for my own uncertainty about
   the lead case's odds.

## Why I do not move higher

- Most paid petitions on which a response is called for are still denied; the
  response request lifts a petition from the one-percent floor to the
  high-single or low-double digits, not to even odds.
- The lead case has vehicle problems the Court may dislike: an antecedent
  contract-construction holding (separate bilateral contracts), a Louisiana
  anti-arbitration insurance statute in the background, municipal respondents,
  and a question the Court could think *Arthur Andersen* already answers.
- The Court has no reason to grant this petition instead of, or alongside, the
  lead: it is a ten-page petition from an unpublished per curiam with no
  independent record, so its grant probability is almost entirely derivative.
- Nothing after August 17 is visible on this docket. If the respondent (a small
  New Orleans firm) obtained an extension, the brief in opposition may land
  late and the petition could lag the lead case by a conference or two; that
  changes timing, not the odds.

## The other claims

- **relist-increment 0.94.** One distribution shown; the response request took
  the petition off the September 28 conference, so a redistribution is all but
  mechanical once the response arrives. The residual is a dismissal or
  withdrawal before redistribution.
- **cvsg-increment 0.05.** The federal interest (treaty obligations, uniformity)
  makes a CVSG conceivable in the lead case, perhaps one in six; a CVSG issued
  on this companion docket is a small fraction of that.
- **summary-disposition-route 0.85.** Conditional on a grant here, the GVR after
  a hold dominates; a consolidated plenary grant is the remainder.
- **dissent-from-denial 0.06.** No Justice has a visible investment in this
  question; a companion docket would at most carry a "would grant" notation
  mirroring one in the lead case.

## Where to discount me

My lead-case estimate is the load-bearing number and it rests on docket shape,
not on reading the brief in opposition or the reply, neither of which I could
retrieve. I could not read this docket's post-August state. I did not find a
published base rate for response-requested petitions in the statpack, so the
upward move from the 5.1% anchor is judgment calibrated on general knowledge of
the call-for-response population, not a corpus cut. I do not know the outcome
of either petition; nothing I retrieved disclosed one, and both the corpus and
the Fifth Circuit's September 3 opinion treat the lead case as pending.
