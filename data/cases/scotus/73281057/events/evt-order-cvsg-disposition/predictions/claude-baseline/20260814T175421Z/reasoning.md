# Rationale for the numbers

## The cell

CVSG-moment cert cell (`moment: cvsg`, stage cert), forward mode. Frozen
conditioning from `record/context.json`: band **high** (sal-v2),
`distribution_count` 2, `cvsg_date` 2026-06-22, term 2025. I anchored on the
frozen band per the contract, not on a band I derived myself.

## Anchors

1. **Salience band, bracketed `reached` rate.** From the statpack's "Segment
   base rate by salience band (sal-v2)" table, pooling the `high` band's
   bracketed `reached` figures over Terms strictly before this case's own
   (2017–2024; the case is Term 2025): weighted by the bracketed n's, the
   pooled rate is **~40.3%** (426.99/1059). That is the risk-set rate a live
   petition that has reached the high band actually faces, and the yardstick
   the evaluator scores this cell against.
2. **CVSG cut (paid scored segment):** granted 30.1% + gvr 5.5% ≈ **35.6%**
   grant-family among petitions that ended CVSG'd (denied 62.0%). Terminal
   rather than as-at, so I treat it as corroborating shape, not a second
   independent anchor.

The two figures bracket roughly 36–40%. One reading caution I hold against
myself: the band table is captioned "grant rate," and I read it as the grant
family consistent with the statpack's own advice to read the grant family as
one number; if it excludes GVRs the anchor is slightly understated, which
would push my number up, not down.

## Adjustments — final P(any grant) = 0.42

Up from the anchor, modestly:

- **Trajectory quality within the band.** The State waived; the Court
  requested a response (Mar 30); after the BIO and reply, the CVSG issued
  from only the second conference, less than four months after docketing.
  That is the fast, deliberate shape of a petition the Court is taking
  seriously, stronger than the average high-band member.
- **Presentation.** Published, divided Ninth Circuit panel (Bea dissent on
  the First Amendment question); petition by a major trade association with
  elite Supreme Court counsel (Arnold & Porter; a Clement & Murphy amicus);
  claimed conflicts with the Second Circuit (Amestoy), the D.C. Circuit
  (NAM), and the First Circuit en banc (Philip Morris v. Reilly) on the
  takings side.
- **Stakes.** Many states have adopted drug-price transparency regimes, and
  the QP1 framework question (what scrutiny governs compelled
  product-specific disclosures after NIFLA) is one several sitting Justices
  have flagged — the petition is built around Kavanaugh's American Meat
  Institute concurrence.

Back down, materially:

- **Vehicle problems the BIO develops well.** This is a facial,
  pre-enforcement challenge — the BIO invokes exactly the Moody v. NetChoice
  concern about facial First Amendment challenges, and raises a genuine
  ripeness question on the takings claim that a granting Court would have to
  decide first. These are the classic hooks for an SG "deny" recommendation,
  and the SG's recommendation largely determines the outcome from here.
- **The splits are contestable.** The BIO plausibly recasts the panel's
  holding as a fact-bound Bolger application rather than a new categorical
  test, and distinguishes the cited out-of-circuit cases as not involving
  disclosures to regulators about pricing. There is no square post-NIFLA
  circuit split on government reporting requirements.
- **The federal government's own equities cut both ways.** The United States
  runs extensive mandatory-disclosure regimes; a broad petitioner-side rule
  is not obviously in the SG's institutional interest, whatever the
  administration's view of state transparency laws.

Net: slightly above the pooled band anchor. **0.42**, with `granted = 0` and
`predicted_disposition = denied` because denial remains the modal single
outcome (~0.55 after small dismissed/withdrawn mass).

## Claims

- `disposition` **0.42** — same belief as the top-level probability.
- `relist-increment` **0.97** — the snapshot shows **two** distributions; a
  CVSG'd petition is redistributed after the SG files, so at least one more
  distribution is near-certain (residual mass: withdrawal/dismissal before
  the SG files).
- `cvsg-increment` **0.02** — the docket already shows the CVSG
  (2026-06-22), so this claim is vacuous for this cell and the harness masks
  it; stated per the contract, and a second invitation essentially never
  issues.

## Uncertainties, and where to discount me

- Everything routes through the unknown SG recommendation; my 0.42 embeds
  roughly a 45% chance the SG recommends grant in whole or part and
  substantial Court-follows-SG conditionals in both directions. A reader with
  better information about the current SG's posture toward state
  transparency laws should move the number accordingly.
- The band-table reading caution above (grant vs grant-family).
- Corpus retrieval added nothing case-specific: a citation-filter query came
  back empty (the note line confirmed sparse citation coverage), and a
  recent-grants query surfaced mostly application dockets. The prediction
  rests on the provisioned snapshot, the three provisioned documents (QPs,
  petition, BIO — all with extractable text, none truncated), and the
  committed statpack.
