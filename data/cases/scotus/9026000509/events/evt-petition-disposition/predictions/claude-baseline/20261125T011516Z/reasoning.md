# Reasoning

**P(grant) = 0.004.**

**Inputs read.** Snapshot `2026-11-25.json`, `context.json`, `questions-presented.txt`, the opening of `appendix.txt` (the table of appendices and the Fifth Circuit's rehearing order and judgment headers) and `documents.json`. I read the questions presented in full but did not read the petition body or the district court orders in full. `same-question.json` lists no matching petitions. No brief in opposition exists; one respondent (Teamsters Local 745) waived, and TForce Freight has filed nothing.

**Anchor.** The context freezes band `baseline` (sal-v9) with `cert_anchor.rate` 0.052 and the no-amicus line at 0.027. Note that the statpack's rendered band table is headed sal-v8 while my context says sal-v9; I used the frozen `cert_anchor` and did not pool the table myself. The anchor is the rate among paid petitions that ever reached the baseline band, including those that later relisted or drew a CVSG.

**Adjustments, all downward.**
- The petitioner is self-represented (the snapshot lists him as his own attorney, contact details withheld). Paid pro se petitions are granted at a far lower rate than counselled ones; I am working from general knowledge here, not a committed cut.
- The four questions are pure error correction: whether summary judgment was proper on this record, whether the district court ruled on all retaliation counts, whether an extension to answer was properly granted, and which limitations period applies to one section 1981 count. No circuit split is alleged in the questions.
- The Fifth Circuit panel (Clement, Southwick, Oldham) disposed of the appeal by per curiam judgment and no judge requested an en banc poll, per the appendix.
- A respondent waived and the petition was distributed without the Court requesting a response, with zero amicus briefs.

**Why not lower.** The limitations question (two versus four years for a section 1981 retaliation claim under 28 U.S.C. § 1658) could, if the courts below plainly erred, draw a call for a response and conceivably a GVR-style correction. I did not read the district court's limitations analysis, so I cannot rule that out; this is the main place to discount me. I put about 3% on a further distribution, almost all of it through a call for a response.

**Conditional claims.** `summary-disposition-route` 0.6: conditional on a grant, a fact-bound pro se petition is more likely disposed of in the cert order than argued; this is judgement, with CA5's GVR share in the statpack's originating-court table (gvr 2.3% against granted 1.6%) pointing the same way. `dissent-from-denial` 0.004: nothing here invites a writing.

**Retrieval.** One corpus query returned recent denied rows unrelated to this case and did not move the number. No CourtListener or web lookups.
