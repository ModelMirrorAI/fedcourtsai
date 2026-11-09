# Reasoning: P(disturbed) = 0.79, judgment = reversed

## Inputs and moment
This is a merits cell at `moment: grant` in forward mode. Cert was granted on 2026-11-06 after four
distributions (conferences of 9/28, 10/9, 10/16 and 11/6). The snapshot read was `record/snapshots/2026-11-07.json`.
I read these provisioned documents: the questions presented, the BIO (its table of contents and the
Hill/Section 105(a)/vehicle arguments), respondents' Rule 15.8 supplemental brief, the Fourth Circuit's opinion
(`decision-below.txt`, published, Niemeyer joined by Harris, King dissenting) and `lower-court-docket.txt`
(no en banc petition). The petition (truncated) and cert reply I used only for framing. No merits briefs were
on disk, which is correct for a grant-moment cell, and I retrieved none. No argument exists yet. The context
band ("high") is a cert construct, and I disregarded it as the prompt directs.

## Anchor
The grant falls in OT2026, so the window is grant Terms 2016–2025. The statpack's merits section publishes an
`excluded` count, so it is quotable. OT2016 has no row, which leaves Terms 2017–2025: disturbed 395 of 560
parsed, which is **70.5%**. The pool clears the 30-judgment floor. Coverage is complete for 2017–2024, but
OT2025 is 26 parsed of 53 granted, mostly pendency, and its quicker dispositions may bias it.

## Adjustments (up to 0.79)
- **Doctrine strongly favors petitioner.** The Court has enforced arbitration against every claimed statutory
  conflict (Epic, CompuCredit, Italian Colors, McMahon itself). The Fourth Circuit's ground is an
  "inherent conflict" with the Code's "policies and purposes," which this textualist majority has disfavored.
  The panel majority itself called the question close ("substantial arguments on both sides"), and there is a
  dissent below and a split with the Second Circuit's Hill. That kind of conflict typically ends in reversal.
- **Up from the grant itself.** The Court granted over a pointed vehicle objection after relisting the petition.
- **Down for risk.** First, the 105(a) contempt framing gives the Court an off-ramp: it could affirm in part,
  or vacate narrowly. Second, the complaint was dismissed with leave to amend, a DIG risk I put at about 5%
  (a DIG counts as undisturbed). Third, bankruptcy cases sometimes produce unusual coalitions (e.g.,
  Gorsuch in Harrington v. Purdue).
- Net: about 0.79. I am fairly confident in the direction and less so about whether the label is reversed
  or vacated. That uncertainty doesn't affect the binary.

## Votes
I checked the per-Justice votes section for Terms 2020–2025 (before OT2026). Every sitting Justice voted to
disturb in most plain judgments (roughly 49–77% per Term). That isn't discriminating here, so the lineup
rests on arbitration-specific history. Sotomayor and Jackson are the likeliest dissenters. Kagan is uncertain
(she dissented in Epic and Lamps Plus but wrote Viking River). I put her in the majority at about 55%.

## Uncertainty
The biggest risk is a narrow outcome on Section 105(a) or the pleadings: affirmance, or a mixed judgment. I
did no CourtListener MCP or web retrieval, and made one corpus query, which only returned recent grants.
