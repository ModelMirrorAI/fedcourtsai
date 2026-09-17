# Rationale for the numbers

**Cell state.** Forward-mode cert cell, `moment: distribution`. Snapshot
`2026-09-15.json`: docketed April 9, 2026; BIO filed June 10; reply June 23;
one distribution, for the September 28, 2026 Long Conference. Five amicus
briefs at the cert stage (Small Property Owners of SF Institute and Owners
Counsel of America; Pacific Legal Foundation; Professors Ely, Mahoney, and
Saxer; Leo Lech and other prior SWAT-damage plaintiffs; Chief Thomas
Tiderington, a law-enforcement voice). Context freezes `band: baseline`,
`salience_version: sal-v4`, `distribution_count: 1`, `cvsg_date: null`,
`term: 2025`. I read all three provisioned documents: the questions
presented, the 47-page petition, and the 45-page BIO (none flagged
`empty_text`).

**Anchor.** The statpack's segment table is computed under sal-v4, matching
the context, and carries a `baseline` column. Pooling the bracketed `reached`
baseline figures over Terms strictly before OT2025 (OT2017 through OT2024,
the whole rendered window), weighted by the reported `n`, gives about 5.1%
(range 4.5% to 5.9% across those Terms, n roughly 11,600 pooled). That is the
yardstick the evaluator will score this cell against. Other cuts read for
shape: relist bucket 0 grants at 1.2% and bucket 1 at 8.2%; no-CVSG at 4.0%;
CA9 origin at 2.1% granted plus 1.1% GVR.

**Why 0.28, well above the anchor.** Every case-specific signal available at
the cert stage points up, and several are strong:

- *Five cert-stage amicus briefs* on a paid petition, including a law
  professors' brief and PLF. The statpack carries no amicus cut, but in my
  judgement this volume alone places the petition in the top few percent of
  the paid docket, where grant rates run well into double digits.
- *A companion petition* (Hadley, No. 25-1158, CA7) filed the same day by the
  same counsel and distributed for the same conference. The pair lets the
  Court address both the police-power and the necessity theories at once.
- *Two Justices already on record.* Sotomayor's statement in Baker, joined by
  Gorsuch, called the question important and divisive and asked for
  percolation. Since then CA9 has published a lengthy history-based opinion
  (158 F.4th 1033) with Judge Friedland concurring on a different theory, CA7
  reaffirmed Johnson in Hadley, and CA11 decided Alford. Thomas is a reliable
  third vote on Takings Clause text and history. The question is whether a
  fourth Justice (Alito, Barrett, Kavanaugh, or Jackson on innocent-owner
  equities) joins.
- *Vehicle quality is high.* Stipulated judgment, reasonableness of the police
  conduct conceded, a published opinion squarely resting on the necessity
  exception, and Institute for Justice as counsel of record. The BIO's vehicle
  arguments (no coherent theory; a state-law property-interest point it admits
  was not raised below) are weak.

**Why not higher.** The BIO's strongest point is real: no circuit has held an
innocent owner entitled to compensation on SWAT facts. CA5 (Baker), CA6
(Slaybaugh), CA7, CA10 (Lech), the Federal Circuit, and now CA9 all deny it,
by different routes. The asserted split is doctrinal, not in results, and the
Eleventh Circuit case the petition leans on (Alford) is a COVID beach-closure
case the BIO fairly distinguishes. The Court has denied three petitions on
this pattern in five years (Lech 2020, Baker 2024, Slaybaugh April 2025), the
last without a noted writing as far as I recall. A Court that wanted an
outcome split before intervening still lacks one. I weight these prior
denials heavily; they are why I sit under one-in-three rather than near even.

**Relist increment (0.55).** From one distribution. Grants at this Court are
almost always preceded by at least one relist, so P(relist) is bounded below
by roughly P(grant); on the denial branch I put a relist (for a separate
writing or a hold for Hadley) near 35 to 40 percent given the amicus volume
and the Baker precedent of a statement. 0.28 + 0.72 × 0.37 ≈ 0.55.

**CVSG increment (0.10).** A federal interest exists (a Marshals task force
led the operation; federal agencies face the same claims), which is why this
is not lower, but no CVSG issued in any of the three prior petitions on these
facts and the Court has treated the question as one of constitutional
history it can decide itself.

**Summary-disposition route (0.04, conditional on grant).** No intervening
decision to GVR against; a plenary grant is the only plausible grant.

**Dissent from denial (0.45, conditional on denial).** Baker drew a statement
from Sotomayor joined by Gorsuch; Slaybaugh, as far as I recall, drew none.
After percolation the Court itself asked for, a denial is somewhat more
likely to draw a dissent or renewed statement than a typical one, but silent
denials of this pattern have also happened.

**Big case score (0.55).** Nationally covered issue, a coordinated litigation
campaign, an open doctrinal question about the Takings Clause's exceptions.
Not a blockbuster: one small business, roughly $60,000, one city.

**Retrieval and its limits.** Forward mode, so I checked the case's own docket
state on CourtListener (not terminated, no cert dates, last modified June 24,
2026) and confirmed via web search that it and Hadley are both distributed
for September 28, 2026: not decided, not mis-provisioned. CourtListener's
SCOTUS dockets carry no docket entries and null cert dates, so I could not
read the relist histories of Baker or Slaybaugh from it; my statements about
those denials (dates, the Sotomayor statement, the absence of a Slaybaugh
writing) come from the petition, one web search, and my own recollection, and
the relist-history part is the least verified input here. Corpus lookups: a
known-case citation query returned nothing (the corpus carries citations on
only 200 of its SCOTUS rows), and a recent-grants query returned a mixed list
of 2020s grants and substantive applications that gave no case-specific
signal. I did not read any prior predictions in this event directory.

**Where to discount me.** The number is a large upward departure from a 5%
anchor on judgment about amicus volume, companion petitions, and vote counting
that the statpack does not measure. If the reader believes the Court will wait
for a true outcome split, 0.15 is a defensible number; if the reader thinks
the Baker statement was an invitation now answered, 0.40 is.
