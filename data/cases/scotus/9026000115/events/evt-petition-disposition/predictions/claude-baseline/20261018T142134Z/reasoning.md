# Rationale — P(grant) = 0.004

**Inputs read:** snapshot `2026-10-18.json`, `context.json` (forward mode,
band `baseline` under sal-v4, distribution_count 1, no CVSG, Term 2026), the
provisioned `questions-presented.txt` and `petition.txt` (59 pages, not
truncated, text extracted). No brief in opposition exists: the respondent filed
a waiver on Aug 25, 2026.

**Anchor.** Statpack "Segment base rate by salience band (sal-v4)",
`baseline` column, bracketed `reached` figure, pooled over Terms 2017–2025
(strictly before my Term 2026): about **5.0%**, n-weighted over roughly 12.9k
petitions. The table's version matches my context's `salience_version`.

**Why I sit far below the anchor.** The baseline reached rate covers every
paid petition that ever sat in the weakest band, including those that later
relisted or drew a response requested by the Court. This petition has features
that, in my experience of the cert docket, put it in the bottom tail:

- **Response waived and no response called for.** The Court almost never
  grants a petition without first calling for a response, and the petition is
  already set for its first conference with only the waiver on file.
- **Unpublished per curiam affirmance** by the Fourth Circuit (appendix,
  "Affirmed by unpublished per curiam opinion").
- **Error correction.** The "Reasons for Granting" section argues that the
  courts below misapplied *Groff v. DeJoy* and summary-judgment standards. It
  alleges no circuit split. Two of the four QPs restate the other two against
  the district court instead of the court of appeals.
- **Small-firm counsel** with no visible Supreme Court practice, and no amici.

The topic (religious objections to COVID-19 vaccine mandates after *Groff*)
is live in the lower courts, and that is the only reason I don't go lower. I
also rely on the mechanical fact that the Court has to call for a response
before it can grant. That makes 0.4% generous rather than stingy.

**Claims.** relist-increment 0.04: essentially P(the Court calls for a
response), which would force a later conference. cvsg-increment 0.002: no
federal interest. summary-disposition-route 0.30 conditional on a grant: an
unpublished, fact-bound case that the Court took would plausibly be a GVR or a
summary disposition. dissent-from-denial 0.01.

**Uncertainty.** I relied on base-rate reasoning and the petition text. I did
not use CourtListener or corpus priors, so I didn't check whether similar
post-*Groff* vaccine petitions drew calls for a response. If the Court calls
for one before Nov 6, this forecast should rise by an order of magnitude.
