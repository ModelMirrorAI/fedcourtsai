# Rationale — P(disturbed) 0.89, judgment `reversed`

**Anchor.** The committed statpack's "The merits docket (granted cases)"
section publishes an `excluded` count, so its pooled rate is quotable and is
the baseline my Brier skill is scored against. My grant Term is 2025 (the
grant order is dated June 15, 2026 — OT2025; taken from the event's
`opened_at`, not the docket number, though here both give Term 2025). The
ten-Term window is grant Terms 2015–2024; the pack holds parsed judgments for
2017–2024, so the shown window is my window. Pooled: disturbed 359 / parsed
515 = **69.7%** (well above the 30-parsed floor: 2024: 50/73, 2023: 34/55,
2022: 49/72, 2021: 46/65, 2020: 57/69, 2019: 42/54, 2018: 50/75, 2017: 31/52).
Coverage caveat quoted per the contract: the rate covers the parsed slice only
(539 of 607 granted, 67 excluded pool-guard rows), and the nearest Terms'
parsed counts are pendency-censored toward quicker dispositions.

**Adjustments up from 0.70 to 0.89.**

1. *Petitioner identity and posture.* The petitioner is the United States
   (Solicitor General Sauer for ICE/DHS officials), seeking review of an
   adverse constitutional holding. The Court essentially never grants an SG
   petition in this posture to affirm; the government's win rate as petitioner
   sits well above the pooled disturbed rate.
2. *Precedent trajectory.* Every recent detention/bond-hearing case in this
   line ended in reversal of the lower court: Jennings (2018), Preap (2019),
   Arteaga-Martinez (2022), Aleman Gonzalez (2022). Jennings reserved exactly
   this question, and the current majority has shown no appetite for implying
   procedural rights for § 1226(c) detainees.
3. *The mootness route also disturbs.* The Court directed briefing on whether
   G.M.'s case is moot. A mootness holding yields a Munsingwear-type vacatur of
   the CA2 judgment — `vacated`, which counts as disturbed — so the two most
   probable resolution paths (merits reversal, mootness vacatur) both land on
   the disturbed side. The undisturbed outcomes require either an affirmance
   (the Court constitutionalizing bond hearings, sharply against its revealed
   preferences) or a DIG.

**Residual on the other side (why not higher).** A DIG is a real if small
possibility: the grant was limited to one of the two consolidated cases
precisely because of mootness trouble, respondents' counsel pressed mootness
hard before the grant, and if G.M.'s posture deteriorates further the Court
could dismiss rather than vacate (a DIG leaves the judgment standing). I hold
~5% there, ~6% on affirmance, negligible mass on an equally divided Court (no
apparent recusal). Net: 0.89.

**Label choice.** `reversed` over `vacated` is the closer call. My rough
split: merits reversal ~0.56, vacatur (mootness Munsingwear, or
vacate-and-remand on a narrower ground) ~0.33, affirmance ~0.06, DIG ~0.05.
The Court set the case for argument on the QPs rather than GVR'ing or
summarily vacating, which says it wants to decide the reserved Jennings
question; that makes outright reversal the modal single label.

**Cert-stage signals not used.** `record/context.json` carries `band: "high"`
and `distribution_count: 3`; those score the petition's grant likelihood,
which is settled history on this stage, so I did not anchor on the salience
band table (no flag owed — a rule of the stage).

**Evidence base.** Forward-mode cell; the judgment does not exist yet
(argument is set for October 13, 2026). I worked from the provisioned
snapshot and the provisioned cert-stage documents — the SG's petition (38 pp,
full text), the ACLU's brief in opposition (43 pp, full text), and the QP
extract — all fetched clean (`empty_text: false`, no truncation). The docket
shows the petitioners' merits brief filed July 30, 2026 and three amicus
briefs (America First Legal, FAIR, Iowa + 26 states — all supporting the
government side), but I did not retrieve any merits-brief text: this is
substantially a docket-skeleton-plus-cert-papers forecast, and the reader
should know that. My one corpus retrieval (a citation-filter query for priors
sharing Jennings's cite) returned no rows — the citation column is sparse — so
the precedent trajectory above comes from general legal knowledge of these
well-known decisions, not from retrieved corpus rows; discount it accordingly.

**Main uncertainties.** (1) Mootness: I cannot see the merits-stage mootness
briefing, and my ~25% vacatur weight is a judgment call from the docket
posture (suggestion of mootness rejected under Rule 15.4, the Court adding the
question sua sponte). (2) Breadth: the Court may reverse only on QP2 (the
burden) and leave the duration trigger open — that would still resolve as
`reversed` but would undercut my `ground-breadth` proposition. (3) The vote
block is banked, not scored today; the 6–3 lineup is the modal merits split
and would misfire if the case resolves 9–0 on mootness.
