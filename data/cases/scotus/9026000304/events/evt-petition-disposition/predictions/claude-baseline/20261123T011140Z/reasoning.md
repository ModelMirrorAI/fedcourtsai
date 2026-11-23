# Reasoning — United States v. Jackson, No. 26-304 (cert, distribution moment)

**P(grant) = 0.70.** Forward cell; snapshot `2026-11-23.json`.

## What I read
- Snapshot: paid petition by the Solicitor General, docketed Sept. 8, 2026, from the Ninth Circuit (judgment Aug. 17, 2026). Response extended once; BIO filed Nov. 2; reply filed Nov. 17; distributed once, for the Dec. 4, 2026 conference. No amicus briefs, no CVSG, no relist yet.
- `questions-presented.txt`, `petition.txt` (truncated in the appendix; I read the body's introduction and structure), `brief-in-opposition.txt`, `cert-reply.txt`. `lower-court-docket.txt` adds little (no opinion on CourtListener, no en banc petition found); I did not rely on it.
- `context.json`: band `federal` (sal-v8), `cert_anchor.rate` 0.731, amicus-line (arm `none`) 0.689.
- `same-question.json` lists 26-348 (score 1.0, pending). I checked it: the corpus row and the Court's live docket page show it is the government's parallel petition from the Second Circuit (*In re Grand Jury Subpoenas*, respondent the New York Attorney General's office), also fully briefed and distributed for the same Dec. 4 conference. It is a text-match row, not a Vide link, but the BIO here itself cites it as raising the same questions.

## Anchor and adjustments
- Anchor: the frozen federal-band reached rate, 0.73 (statpack per-Term range 48%–96%; OT2025 57%, n=28). The no-amicus reference line is 0.69.
- Up: the questions are of obvious institutional importance (the FVRA's first-assistant rule and total delegation of a vacant office's duties, applied to acting U.S. Attorneys but reaching every Senate-confirmed office at transitions); three courts of appeals (2d, 3d, 9th) have now rejected a practice the Executive and GAO have followed since 2001; the Ninth Circuit itself acknowledged tension with the Federal Circuit's *Arthrex* remand decision on delegation; the government filed two petitions and presses urgency. The Court usually takes cases where lower courts have invalidated a significant executive-branch practice at the Solicitor General's request.
- Down: on question 1 the circuits are unanimous against the government, and the claimed split on question 2 is contestable (the BIO says *Arthrex* construed a different provision). The BIO raises real vehicle points: collateral-order jurisdiction over a disqualification order, whether Ms. Chattah's acting service lapsed under § 3346 anyway, a pending nomination, and the fact that indictments were not dismissed. The government did not seek certiorari in *Giraud* (3d Cir.). The reply answers these adequately but not conclusively.
- Docket-specific risk: with two petitions on one question, the Court may grant only 26-348 and hold this one. A hold defers resolution and ends in either a GVR (a grant on the scored axis) or a denial depending on the merits outcome. I price roughly 10–15% on "the other petition is the vehicle and this one is held," and that mass is split between eventual grant-family and denial. Jackson was filed first, squarely presents both questions on a published opinion, and respondents themselves ask that both be granted and consolidated if either is, so I think a grant here (alone or consolidated) is the modal outcome.

Net: I end slightly below the anchor, at 0.70. The importance pushes up, the absence of a clean split on QP1 and the vehicle/hold risks push down by a bit more.

## Other claims
- `relist-increment` 0.72: the Court's ordinary practice is to relist once before granting, so most of the grant mass implies a further distribution; a straight grant on Dec. 4 (to fit the April sitting) is possible, and a straight denial would mean no relist. A hold would also show up as later distributions.
- `cvsg-increment` 0.005: the United States is the petitioner.
- `summary-disposition-route` 0.06 (conditional on grant): plenary review is the natural route; the residual is a hold-then-GVR path.
- `dissent-from-denial` 0.20 (conditional on denial): a denial of a Solicitor General petition on executive staffing could draw a noted dissent, but most denials carry none.
- `order-writers`: small numbers, weighted to Justices who most often write on cert orders.

## Uncertainty and discounts
- I did not read the Ninth Circuit opinion itself beyond what the parties say about it (the appendix is partly truncated).
- Possible mootness developments (Senate action on the nominee before Jan. 3, 2027; a change in the Nevada office's leadership) could change the picture; I cannot see them.
- I made no use of anyone else's forecast, and found no claim that this petition has been decided.
