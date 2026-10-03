# Rationale

## Record and information boundary

This is a forward, cert-stage distribution cell. I read the provisioned
`record/snapshots/2026-10-03.json`, `record/context.json`, and the event definition.
The snapshot identifies paid docket 25-1154, an April 1, 2026 petition challenging
the Eighth Circuit's January 9, 2026 judgment in No. 24-2485. It shows exactly one
distribution, entered September 23 for the October 9, 2026 conference, and no
CVSG. Four response extensions precede a September 8 brief in opposition. These
are response extensions, not relists or four separate indications of Court
interest. The frozen band is `baseline`, version `sal-v4`, docket-number Term
2025. A federal respondent does not turn this private petition into a federal
petitioner's case.

No documents directory, petition text, questions-presented text, or opposition
text was provisioned. The docket establishes that an opposition was filed, not
what it argued. The paper-filing direction and petitioner's listing as his own
attorney do not establish the merits of his claims. I retrieved only the
pre-petition appellate opinion through CourtListener: *Abrahim Fofana v. Kristi
Noem*, No. 24-2485 (8th Cir. Jan. 9, 2026), opinion ID 11239048, especially
pages 2–7. No Supreme Court disposition, later docket, other predictor output,
or outcome-bearing labeling artifact was sought or encountered. I do not know
this petition's outcome.

## Anchor and adjustment

The committed `metrics/statpack.md`, under "Segment base rate by salience band
(sal-v4)," supplies the matching baseline-band **reached** rates. I pooled every
displayed Term strictly before 2025: 2017–2024. Weighting the displayed rates
by their displayed denominators gives approximately **5.12%**, with weighted
denominator **11,580**. This calculation uses rounded percentages, so it is not
an exact recovered grant count. The leading terminal-band percentages are not
the anchor; neither are the 2025 and 2026 rows. The pack's modern-cert section
supplies broader context, but it mixes fee classes and is not this cell's
selected-population prior.

The pack is the committed artifact available in this checkout, not a fresh
corpus query. Its inspected metadata does not state a build timestamp or the
underlying blob's newest pull/snapshot vintage. I make no claim that these
aggregate counts describe a freshly pulled corpus. The case-specific baseline
is the provisioned October 3 snapshot, whose payload creation date is October 2;
no case-level `last_pulled` value was supplied.

My **6% probability of any grant** is a modest increase from that anchor. The
appellate opinion exposes a consequential statutory issue rather than merely
an unfavorable fact finding. It holds that 8 U.S.C. § 1252(a)(2)(B)(ii) prevents
district-court review of eligibility determinations underlying discretionary
adjustment under § 1159(b). The panel expressly says the Supreme Court has not
resolved this question, citing *Bouarfa v. Mayorkas*, 604 U.S. 6, 19 (2024),
and extends the reasoning of *Patel v. Garland*, 596 U.S. 328 (2022), from
clause (i) to clause (ii). Those characterizations come from the appellate
opinion, not from separately retrieved copies of those precedents.

The difference between the two statutory clauses and the reach of judicial
review supply a plausible review-worthy question. Conversely, an unresolved
question is not itself an established circuit conflict. The retrieved opinion
does not identify a contrary appellate holding on this precise issue; its
discussion of *Bremer* concerns earlier Eighth Circuit language, not an
identified inter-circuit split. The panel treats its result as consistent with
existing Supreme Court reasoning. I have not verified a mature post-*Patel*
split, a supporting amicus campaign, or the actual petition's preservation and
vehicle arguments. Their absence from my evidence is uncertainty, not proof
that none exists. These limitations keep the upward adjustment small and make
denial the clear modal disposition. The 94% complement is all non-grant
outcomes, not an assertion that dismissal or withdrawal is impossible.

## Remaining claims and stakes

The statpack's paid-segment relist cut shows a large terminal zero-relist
population (10,489 cases) compared with one relist (2,537), two (485), and three
or more (486). Its no-CVSG population likewise dominates the CVSG population
(13,824 versus 173). These are terminal, pooled descriptive cuts, including
pending cases, not conditional forward hazards. I use their shape only.

- **Further distribution: 20%.** One initial distribution is already on the
  record. Zero further distributions is the modal forecast; if another occurs,
  one is more plausible than a long sequence. The potentially important
  jurisdictional issue supplies some prospect of closer consideration, but
  the extensions supply no relist evidence.
- **New CVSG: 0.3%.** The federal government is already a respondent and its
  Solicitor General is counsel of record; an opposition has been filed.
  An invitation for a separate government view is therefore especially
  unlikely. This is a judgment about this posture, not a fitted corpus rate.
- **Summary route conditional on grant: 15%.** No intervening authority
  requiring a GVR has been identified. A grant to resolve the disputed reach
  of clause (ii) would more likely lead to briefing and argument. This is a
  conditional probability, not 15% of all petition outcomes.
- **Separate writing conditional on denial: 5%.** The scope of judicial
  review could attract a statement, but I have no evidence supporting a
  specific Justice's announced interest. I predict no separate writing and
  do not infer an individual cert vote.

The **0.45 stakes score** reflects potential consequences for access to
judicial review of asylum-based adjustment eligibility, beyond the individual
terrorism-related inadmissibility dispute described on pages 2–3 of the
appellate opinion. It does not measure grant likelihood. Missing petition and
opposition texts limit confidence in the issue's precise breadth; that gap is
also recorded in `flags.json`.
