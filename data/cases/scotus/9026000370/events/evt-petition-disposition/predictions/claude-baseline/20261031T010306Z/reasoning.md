# Reasoning — Nielsen Co. (US) v. Cumulus Media New Holdings, No. 26-370

**P(grant) = 0.12.**

## Inputs read
- Snapshot `record/snapshots/2026-10-31.json`: paid petition docketed Sept 17, 2026 from CA2 (No. 26-88, decided July 13, 2026; rehearing denied Aug 18, 2026). Respondent Cumulus **waived** its response (Oct 19). Two amicus briefs supporting the petitioner (Washington Legal Foundation; Law and Economics Scholars / ICLE), both filed Oct 19. One distribution, for the Nov 13, 2026 conference. No CVSG, no call for a response.
- `record/context.json`: forward mode, band `baseline` (sal-v4), distribution_count 1, `cert_anchor.rate` = 0.0509 (10-Term pooled reached rate).
- `questions-presented.txt`, `petition.txt`, and the appendix (truncated, but the CA2 opinion is there). No BIO, because the respondent waived.
- `same-question.json`: no matching petitions.

## Anchor and adjustments
- **Anchor:** the frozen `baseline` reached rate, 5.1%.
- **Up:** The QP is a clean doctrinal question: is above-cost bundled/standalone pricing actionable as a "constructive tie" under Section 2? The petition frames it as the well-known split between LePage's (3d Cir. en banc) and Cascade Health v. PeaceHealth (9th Cir.) plus the Sixth Circuit, with the Second Circuit now on LePage's side. The opinion below is published (reported in F.4th) and came after rehearing en banc was denied. It also sits uneasily with linkLine, Brooke Group and Weyerhaeuser, which are the Court's price-cost cases. Counsel is elite (Gibson Dunn), and two amici filed at the petition stage. In the statpack's paid segment, the 2+ amicus bucket runs about 18% granted plus 4.5% GVR (n=1,446 resolved), against 2% in the 0 bucket.
- **Down:** The posture is interlocutory: an affirmed preliminary injunction with merits proceedings still to come below. That is a classic vehicle objection. The Court denied cert on this same split in 3M v. LePage's (2004), after the SG recommended denial. The waiver means the Court has not yet heard from the other side, so the likely next step is a call for a response, not a grant. A private-party antitrust dispute often draws a CVSG before the Court acts, which pushes any grant out of the near term but does not lower its eventual chance.
- On balance I land at about 2.4× the anchor, 0.12. I am not going higher because of the vehicle problem and the 2004 denial.

## Increments
- **Relist (0.62):** Most of this is P(the Court calls for a response). With a waiver, an acknowledged split, published reasoning and two amici, I put that at roughly 55–65%. A call for a response forces redistribution after the BIO. A reschedule adds a little more.
- **CVSG (0.15):** This is an antitrust question where the United States (DOJ/FTC) has a strong enforcement interest, and the Court CVSG'd the prior LePage's petition. But a CVSG almost always follows a filed response, which gates it.
- **Summary route | grant (0.04):** No intervening decision makes a GVR plausible. A summary reversal on a contested split is unlikely.
- **Dissent from denial | denial (0.06):** A statement respecting denial noting the interlocutory posture is possible but uncommon.

## Uncertainty
I have not seen any opposition. The respondent's vehicle arguments, if a response is called for, are the main unknown. I took the split characterization from the petition alone. I did not independently verify the Sixth Circuit case the petition cites. The appendix text is truncated.
