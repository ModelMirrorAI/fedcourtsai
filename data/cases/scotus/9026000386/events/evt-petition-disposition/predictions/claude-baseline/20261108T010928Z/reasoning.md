# Reasoning — scotus/9026000386 (No. 26-386), Lowery v. Cheboygan Area Schools

**P(grant) = 0.003.**

## Inputs
- Snapshot `record/snapshots/2026-11-08.json` (forward mode, no cutoff). Paid petition filed Jun 26 2026, docketed Sep 22 2026. The State/UIA respondents filed a waiver of response on Oct 22 2026. The petition was distributed once, on Nov 4 2026, for the 12/4/2026 conference. No call for a response, no CVSG, no amicus briefs.
- `questions-presented.txt`, `petition.txt` and `appendix.txt` (none empty or OCR-derived). The petitioner is pro se. He was a school bus driver who was denied summer unemployment benefits under Michigan's "reasonable assurance" between-terms provision, MCL 421.27(i)(2). His QPs ask whether that provision "dismantled" the federal 1970 Employment Security Amendments (P.L. 91-373), whether a 1984 state amendment "corrected" it, and whether the defendants violated *Reed v. Reed*.
- The appendix holds the Sixth Circuit's unpublished order (Norris, Bloomekatz, Hermandorfer). It affirmed dismissal of the § 1983 complaint and later denied panel rehearing. `lower-court-docket.txt` shows no en banc petition and no opinion on CourtListener.
- No brief in opposition exists because the respondents waived.

## Anchor and adjustment
- `cert_anchor.rate` = 0.0515 for band `baseline` (sal-v8). That rate covers the whole paid baseline population, and much of that population is counseled petitions.
- I adjust far below the anchor for these reasons:
  - The petitioner is pro se and the briefing is poorly drafted.
  - The decision below is an unpublished, unanimous order.
  - No circuit split is alleged.
  - The questions are framed as attacks on the validity of state law, while federal law (FUTA, 26 U.S.C. § 3304(a)(6)(A)) itself requires the between-terms denial for non-professional school employees who have reasonable assurance.
  - The respondents waived, and the Court has not called for a response. The Court essentially never grants a paid petition without first calling for a response.
- For comparison, the statpack's relist-0 bucket (paid scored segment) is 1.3% granted. This petition sits well below the median petition in that bucket.
- I put a residual 0.3% on a surprise. The likely route for any grant would be a GVR or summary disposition, so `summary-disposition-route` = 0.3.

## Increments
- **relist-increment, 0.03.** It would come mainly from a call for a response, which seems very unlikely here, or from a reschedule.
- **cvsg-increment, 0.002.**
- **dissent-from-denial, 0.004.**

## Uncertainty
Little. The main tail risk is a clerical reschedule before the conference, which would count toward the relist increment.
