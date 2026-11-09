# Reasoning — 26-297, Morrisey v. Jonathan R. (cert, distribution moment, forward)

**P(grant) = 0.30. Call: denied.**

## Anchor
`record/context.json` has the band frozen as `state` (sal-v8), with `distribution_count` 1, no CVSG,
and `cert_anchor.rate` 0.233 (the reached rate pooled over 10 prior Terms). The statpack's state
column, read as [reached] rates for OT2017–OT2025, runs from about 14% to 39%, which agrees with that figure. I start at 0.23.

## What the docket shows (snapshot 2026-11-09)
- Paid petition filed Sep 2, 2026, from a **published, divided** Fourth Circuit opinion (Floyd and
  Harris; Rushing concurred in the judgment in part and dissented in part), 178 F.4th 139.
- Respondents **waived** a response on Sep 29. The petition was distributed for the 11/6/2026 conference, and then the
  Court **requested a response** on Oct 19, now due **Dec 8, 2026** after a partial extension. No BIO is in the record yet.
- Three amicus filings on Oct 8: the WV Legislature's leaders (Paul Clement), **22 States** (South
  Carolina, Alaska and 20 others), and the ACLJ (motion for leave). By the statpack's counting rule that puts the petition in the 2+ amicus
  bucket (18.2% granted plus 4.5% GVR, as a marginal description).

## Adjustments
- **Up:** a called-for response after a waiver means at least one Justice wants the case looked at. The
  22-State amicus brief and Clement's involvement raise salience. Both QPs are framed for the
  current Court. QP1 (redressability and Article III limits on structural injunctions) draws directly on
  Horne v. Flores, Lewis v. Casey, and the Scalia and Alito *Plata* dissents. QP2 alleges a real split
  (7th/D.C. vs. 6th/9th) on whether Rule 23(f) bars review of a class-certification order
  that merged into the final judgment. A judge on the panel dissented in part. The petition says similar suits are pending in 34 States.
- **Down:** the **posture is interlocutory**. The Fourth Circuit reversed a standing dismissal and remanded,
  and no injunction has issued, so the Court can wait for a concrete remedial order. The Court already
  **denied** the State's earlier petition in this same litigation (No. 22-240, denied Oct 11, 2022,
  per the corpus row). QP1's "manager or policy planner" framing is new rather than a clean
  split; the petition's main out-of-circuit support is the Fifth Circuit's *Stukenberg*. Even Judge Rushing
  concurred in part of the reversal. A response request is a low bar, and most such petitions are still denied.
- Net: about 0.30, a moderate lift over the band anchor. The response request and the State coalition outweigh
  the interlocutory vehicle concern, but not by much.

## Other claims
- relist-increment 0.96: the record shows one distribution. Once the Dec 8 response (and any reply) is in, the petition
  will be redistributed almost mechanically, probably for a January 2027 conference.
- cvsg-increment 0.05: the parties are a State and private plaintiffs, and the federal interest is indirect. A CVSG is possible but unusual here.
- summary-disposition-route 0.06: no intervening decision would support a GVR, and a summary reversal on an interlocutory standing
  ruling is unlikely.
- dissent-from-denial 0.25: this is the kind of institutional-reform issue on which Justices Alito or Thomas have written.

## Inputs used and caveats
I read the petition (`petition.txt`, not truncated), the QPs, the decision below (`decision-below.txt`, truncated, which I used for
the panel line-up) and `lower-court-docket.txt` (no en banc petition). `appendix.txt` is truncated and I only checked
it against the petition. There is no BIO yet, so I have not seen respondents' vehicle and split arguments, and that
is my main uncertainty. `same-question.json` lists no matching petitions. I did no web or MCP retrieval.
