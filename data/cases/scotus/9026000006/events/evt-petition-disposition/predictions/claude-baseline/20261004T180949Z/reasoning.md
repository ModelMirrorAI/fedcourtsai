# Rationale for the numbers

**P(grant) = 0.007.**

*Anchor.* The cell's frozen conditioning (`record/context.json`) is a
`forward` cert cell, moment `distribution`, band `baseline` under `sal-v4`,
one distribution, no CVSG, Term 2026. The statpack's "Segment base rate by
salience band (sal-v4)" table matches the context's salience version and
carries a `baseline` column, so that is the anchor. Pooling the bracketed
`reached` figure over every Term the table renders strictly before OT2026
(OT2017 through OT2025, weighted by the bracketed n) gives a baseline-band
risk-set grant rate of about 5.0% (n ≈ 12,720). The relist-count cut's
relist-0 row (granted 1.2%, GVR 0.5%) is the rate among petitions that ended
undistributed-again, which is a terminal figure, not the forward hazard, so I
read it only for shape.

*Adjustments, all downward.* This petition has essentially every feature the
denied end of the baseline band shares and none of the features that move a
petition up the ladder:

- **No conflict.** The petition (8 pages of argument in a 103-page filing
  that is mostly appendix) asserts no circuit split, no conflict with a
  decision of this Court, and no conflict with a state court of last resort.
  The BIO (pp. 7–9) cites decisions from the First, Second, Fourth, Sixth,
  Seventh, Eighth, Ninth, Tenth, and Eleventh Circuits applying the same
  actual-or-constructive-knowledge requirement, plus Third Circuit district
  authority, and the petition does not dispute that no court has adopted its
  reading. A petition whose only ground is that the decision below is wrong is
  error correction, and the Court almost never grants on that basis.
- **Vehicle problems.** The BIO argues the QP was not preserved in the district
  court JMOL motion (raised first on appeal; the Fifth Circuit declined to
  reach waiver because it rejected the argument on the merits). The jury was
  also instructed on the "deliberately prevents the employer from acquiring
  knowledge" ground, which the petition does not challenge and which would
  independently sustain the verdict. Either would let the judgment stand
  regardless of the QP's answer.
- **Posture.** A unanimous published Fifth Circuit panel affirming a unanimous
  jury verdict after a full trial, with rehearing en banc denied without a
  recorded dissent. Review would require re-weighing trial facts.
- **Petitioner profile.** A private petitioner earning $550,000–$627,000 a year
  in commissions who, per the BIO, had earlier called the misclassification
  theory "hogwash." That is not the FLSA plaintiff a Court inclined to revisit
  the knowledge rule would choose.
- **Counsel and presentation.** Petitioner's counsel is a Houston appellate
  boutique, not a repeat Supreme Court practitioner; the petition's brevity and
  the absence of any Rule 10 argument confirm the error-correction character.

What keeps the number above zero: the textual point is clean enough ("employ"
includes "to suffer or permit"; the statute says nothing about knowledge) that
a Justice interested in reading the FLSA's definitions literally could in
principle notice it, and the Fifth Circuit opinion is published and short, so
the Court would have little to work around. That is worth a fraction of a
point, not more. I land at 0.007, roughly one-seventh of the band's risk-set
rate and below the relist-0 terminal grant rate, which I think is right for a
paid petition with no conflict, a waiver problem, and an alternative ground.

**Claims.**

- `disposition` 0.007: identical to the top-level probability, as required.
- `relist-increment` 0.10: the record shows one distribution. In the paid
  scored segment roughly a quarter of petitions end with at least one more
  distribution, but that share is carried by petitions with conflicts, hold
  candidates, and statements respecting denial. I could identify no pending
  merits case this could be held for (the CourtListener docket scan that would
  have confirmed this was throttled; see below), so the residual is mostly a
  reschedule. 0.10.
- `cvsg-increment` 0.01: no federal party, no conflict; CVSGs run near 1% of
  the paid segment even in the terminal cut and this petition has none of the
  features that draw one.
- `summary-disposition-route` 0.15 (conditional on a grant): no intervening
  decision to GVR in light of; summary reversal of a uniform circuit rule is
  implausible. The conditional sits above zero only for an intervening
  decision I cannot foresee. The baseline is the prior Terms' cert-order share
  of grants, which runs well above this; I am deliberately below it because a
  GVR needs a trigger this case lacks.
- `dissent-from-denial` 0.02 (conditional on a denial): see the forecast
  document. A bare denial.

**Big case score 0.08.** Stakes, not odds: an individual's overtime claim on a
rule every circuit applies identically. A grant would make the question
significant for FLSA practice, but the case as it stands is small.

**Inputs used.** Snapshot `record/snapshots/2026-10-04.json` (five docket
entries: petition filed 6/26/2026, extension to 8/31, BIO filed 8/31,
distributed 9/16 for the 10/9/2026 conference); `record/context.json`;
`questions-presented.txt` (the single QP); `petition.txt` (the full argument
and the Fifth Circuit opinion in the appendix, the document marked `truncated`
but the truncation falls inside the appendix after the opinion begins);
`brief-in-opposition.txt` (read in full). No document carried `empty_text`.

**Retrieval and its limits.** Two `fedcourts query` pulls against the corpus
service returned recent resolved SCOTUS rows, mostly September 2026
applications, which was not informative on shape for a paid cert petition; I
anchored on the statpack rather than on those rows. One CourtListener MCP
lookup confirmed the Fifth Circuit opinion (No. 24-50127, filed 2026-02-06) is
published. Two further MCP searches, one sweeping other circuits for any
decision treating "suffer or permit" without a knowledge requirement and one
scanning the OT2025–OT2026 SCOTUS docket for a pending FLSA case that could
make this a hold, were refused with an upstream rate-limit error (HTTP 429,
about 19 minutes until reset). Per the prompt I did not wait; the cell rests on
the provisioned inputs and the statpack. The two unverified points are (a)
whether any circuit has adopted the petitioner's reading, where I rely on the
BIO's survey and the petition's own silence, and (b) whether a hold candidate
exists, where I rely on my own knowledge of the Court's current docket.

**Where to discount me.** If a merits case on FLSA "hours worked" or the
knowledge rule is pending this Term that I failed to identify, the relist
probability is too low and the petition could be held; the grant probability
would still be near zero because a hold resolves as a GVR or denial, not a
plenary grant. Corpus freshness: the snapshot and documents carry a
`fetched_at` / `snapshot_date` of 2026-10-04, today, so the docket state is
current as of this run.
