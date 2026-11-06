# Reasoning — scotus/9026000157 (No. 26-157), evt-petition-disposition

**P(grant, any form) = 0.16. Call: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-11-05.json` (forward mode, no cutoff).
- `record/context.json`: band `baseline` (sal-v7), distribution_count 1, no CVSG, term 2026,
  `cert_anchor.rate` = 0.0515 (baseline reached rate, 10 prior Terms).
- `record/documents/`: questions-presented.txt, petition.txt, appendix.txt (no BIO yet; none has been filed).
- `record/same-question.json`: empty list (no petition above the 0.5 similarity threshold).
- `metrics/statpack.md`: relist-count, CVSG and amicus-count cuts for the paid scored segment, and the sal-v7 band table.

## Docket state
Paid petition from the Nevada Supreme Court (published opinion, 586 P.3d 858, resolving an original
writ petition). The respondents waived (Aug 21). Three amicus briefs support the petitioner: the Anglican
Church in North America, the Roman Catholic Archbishop of Las Vegas, and former EEOC General Counsel.
It was distributed for the 10/9/2026 conference, and on Sep 22 the Court requested a response before that
conference. The response is now due Nov 23, 2026 after an extension. So the petition has one distribution
and will be redistributed once the BIO arrives.

## Anchor and adjustments
- Anchor: the baseline band's reached rate, ≈5.2% (`cert_anchor`). The private-petitioner caption makes
  `baseline` the right class floor.
- Up: a **called-for response** after a waiver means at least one Justice wanted a response. Most such
  petitions are still denied, but the rate is several times the band's. Three amicus briefs put the petition in the
  `2+` amicus bucket (n=1446 resolved; granted 18.2% + gvr 4.5%). That is a marginal cut that overlaps with the response
  request, so I do not stack it fully. The QP is a split the court below **acknowledged** (it names the
  2d/8th/9th/D.C. Circuits and several state high courts against the 5th/6th/11th Circuits and others, as the
  petition characterizes it). It is a published state high court decision with experienced Supreme Court
  counsel (Sidley). Church autonomy is an area where Justices Alito, Thomas and Gorsuch have repeatedly signaled interest.
- Down: by the petition's own account, the Court **recently denied O'Connell, No. 25-849**, which raised the neutral-principles
  question. The petition distinguishes it on vehicle grounds (a federal interlocutory appeal and a threshold
  jurisdictional problem), but the denial shows the Court is not eager. The posture is effectively interlocutory, since
  the trial-court case proceeds after the writ ruling. The petition argues finality under Atlantic Richfield v. Christian and Cox
  Broadcasting, and that argument is respectable, but the BIO will likely press it. The underlying dispute
  (a Sikh society's bylaws and elections) is small, and the Court may wait for a cleaner federal vehicle. No BIO is
  on the record yet, so I cannot weigh the opposition's split or vehicle rebuttal.
- Net: about 0.16. That is above the amicus-bucket grant-only rate's midpoint for a response-requested petition, discounted for
  the recent O'Connell denial and the finality question.

## Claims
- relist-increment 0.96: the response is due Nov 23, and the petition will almost certainly be redistributed after it
  (or after the reply).
- cvsg-increment 0.03: there is no federal party or federal statute. The United States has occasionally weighed in on
  religion-clause questions, but a CVSG on a state-court church-autonomy case is rare.
- summary-disposition-route 0.08: if the Court takes the case, plenary review is the likely route. A summary reversal is conceivable
  but unlikely on an open split, and I know of no intervening merits decision that would prompt a GVR.
- dissent-from-denial 0.30: this is a topic where Alito (often joined by Thomas/Gorsuch) has written respecting denials
  (e.g., in church-autonomy and religious-employer petitions). Whether one comes depends on whether O'Connell already drew
  one, which I do not know.

## Uncertainty
I did not see the O'Connell denial's text or any statement accompanying it. The claimed split and
the O'Connell characterization come from the petitioner's brief only. A reader should discount the
upward adjustments if the BIO shows a weaker split or a real finality problem.
