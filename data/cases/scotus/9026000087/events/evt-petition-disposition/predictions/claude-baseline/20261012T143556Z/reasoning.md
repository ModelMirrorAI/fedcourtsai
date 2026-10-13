# Rationale — P(grant) = 0.004

**Inputs read:** snapshot `2026-10-12.json`, `context.json` (mode `forward`, band `baseline`
under `sal-v4`, distribution_count 1, no CVSG), event.yaml (`stage: cert`, `moment:
distribution`), and the provisioned `questions-presented.txt`, `petition.txt`,
`brief-in-opposition.txt`, `appendix.txt` (all with text extracted, none truncated).

**Anchor.** The statpack's per-Term "Segment base rate by salience band (sal-v4)" table matches
my context's salience version. I pooled the bracketed `reached` figure for `baseline` over every
Term strictly before 2026 (2017–2025). That comes to roughly 640 grants in about 12,900
weighted petitions, so **≈5%**. I recomputed the pool from the table's rates and `n`s, so the
figure is approximate.

**Why I go far below the anchor.** The baseline class is the whole paid private-petitioner
population, including petitions filed by experienced Supreme Court counsel. This petition has
almost every negative marker at once:
- **Pro se.** The petitioner appears in person (`IsCounselofRecord: false`). Pro se paid
  petitions are granted far less often than counseled ones.
- **Unpublished summary-calendar affirmance.** CA5 No. 24-30642, per curiam, "not designated
  for publication." Rehearing en banc was denied, and no judge asked for a poll.
- **Fact-bound, state-law case.** The underlying dispute is first-party hurricane insurance
  coverage (Laura/Delta) under Louisiana law: a loss valuation and a roof exclusion. The federal
  question is the application of discovery sanctions to one record.
- **Preservation.** The BIO argues that none of the three QPs was raised to or decided by the
  Fifth Circuit. If that holds, the case is a vehicle problem on top of everything else.
- **Weak split.** The claimed split (6th/10th/2nd Circuits on willfulness findings) mixes
  dismissal-sanction standards with Rule 37(c)(1) exclusion. The BIO calls it manufactured,
  and in my judgment the circuits do not actually conflict on these facts.
- **No signal in the BIO.** The respondents filed the BIO on their own (no call for response),
  which is common for represented respondents. It says nothing about the Court's interest.

**Other claims.** relist-increment 0.03. A single relist of a petition like this is rare, but
an administrative reschedule is possible. cvsg-increment 0.002, since no federal interest is
involved. summary-disposition-route 0.3, conditional on a grant: the only realistic grant here
is a summary disposition, but a grant this unlikely is too strange to model well.
dissent-from-denial 0.005.

**Uncertainty and discounting.** The main risk is that I am under-reading the sanctions issue.
Case-dispositive exclusion without findings does recur, but this record and this advocate make
it an unattractive vehicle. One oddity: the petition's docket entry is dated Sep 06 2025 but the
case was docketed July 21, 2026. That fits a petition that was filed and later corrected or
resubmitted, and I treated it as a docketing artifact, not a signal. I did not retrieve anything
beyond the provisioned inputs and the committed statpack.
