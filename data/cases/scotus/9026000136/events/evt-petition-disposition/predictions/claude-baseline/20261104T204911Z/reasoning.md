# Reasoning — Tesla, Inc. v. Granite Vehicle Ventures LLC (No. 26-136)

**P(any grant) = 0.09. Call: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-11-04.json` (forward mode, no cutoff). Paid petition from a
  Federal Circuit order (Feb. 27, 2026) denying mandamus. The PTO had denied IPR institution on
  the ground of expected time to trial in parallel district-court litigation. The federal
  respondent (the SG) filed a BIO on Sep 25 and the petitioner replied on Oct 13. The petition
  was distributed for the 11/6 conference, **rescheduled** on Oct 22 and redistributed on Nov 4
  for 12/4. Two amicus briefs were filed (Askeladden; US\*MADE et al.), and Unified Patents moved
  for leave to file one.
- `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt` and `cert-reply.txt`
  (all extracted text, none OCR-derived or truncated). The QP asks whether courts can review a PTO
  non-institution decision that rests on a ground contrary to statute.
- `context.json`: band `elevated` (sal-v6), distribution_count 2, no CVSG,
  `cert_anchor.rate` = 0.248 (10-Term lookback).
- `same-question.json`: empty list (nothing scored at or above 0.5).

## Anchor
The frozen anchor is the elevated band's reached rate of **~24.8%**. That band fits a petition
with amici and a distribution plus a reschedule. The relist-count cut's "2" bucket (28% granted
plus 13% GVR) overstates this case, because a reschedule before the first conference inflates the
count. The statpack's own caption warns about this.

## Adjustments (all downward, one partial offset)
1. **A companion vehicle was just denied.** The petitioner's reply (fn. 3) lists the
   "confluence of vehicles": Intel v. Squires (26-73), Google v. VirtaMove (25-1230), Kahoot! v.
   Interstellar (26-198) and this case. A corpus lookup shows **Google v. VirtaMove (25-1230),
   also a Federal Circuit mandamus denial on the same reviewability question, was denied on
   2026-10-19** after two distributions. The Court has also denied earlier Fintiv-reviewability
   petitions, as the BIO notes (Apple v. Vidal, Mylan, Intel v. VLSI, Optis). A mandamus-posture
   vehicle denied two weeks ago is the strongest single signal on the record.
2. **Posture and the SG's opposition.** The case comes up on mandamus with §314(d)'s "final and
   nonappealable" bar and Cuozzo/Thryv against it. The SG argues the petition does not even
   engage the mandamus standard, so it is a poor vehicle. An SG BIO as the respondent's brief
   weighs against a grant.
3. **Partial offset: the reschedule.** Moving the petition from 11/6 to 12/4 most plausibly lets
   the Court consider it alongside Intel v. Squires (26-73). That case raises the question through
   a direct APA challenge (a cleaner vehicle) and had not been distributed as of its last poll
   (2026-11-02). If the Court grants Intel, this petition could be held and later GVR'd. I put
   P(Intel granted) at ~0.25 and P(GVR | held behind a petitioner win) at roughly a third. That
   gives ~0.06 through the hold path, plus ~0.03 for a direct grant here.

Net: **0.09**, well below the 0.248 band anchor. I am deliberately betting that the case-specific
evidence, chiefly the VirtaMove denial, beats the band.

## Claims
- relist-increment 0.40: the docket shows 2 distributions (one distribution plus a
  reschedule-redistribution). A further one comes if the Court reschedules again or holds the
  petition for Intel and later redistributes it. An outright denial on 12/4 is the modal path.
- cvsg-increment 0.01: the SG is already the respondent and has filed a BIO.
- summary-disposition-route 0.60 (conditional on any grant): most of my grant mass comes through
  a hold-and-GVR behind Intel rather than plenary review here.
- dissent-from-denial 0.10: Gorsuch has written skeptically about IPR and agency power over
  patents (Thryv, Oil States). I don't know whether anyone wrote on the VirtaMove denial; I did
  not retrieve its order text.

## Uncertainty / where to discount me
- I don't know VirtaMove's exact grounds. A mandamus-specific vehicle problem would cut the same
  way here, but if Justices wrote about waiting for a better vehicle, Intel benefits rather than
  Tesla.
- My reading of the reschedule is inference. It could equally be a routine reschedule before a
  plain denial.
- `big_case_score` 0.55: important to patent practice and to agency-reviewability doctrine, but
  technical.
