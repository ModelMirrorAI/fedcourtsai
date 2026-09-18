# Why 0.06

## Inputs read

- Snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names; forward mode, band `elevated` under `sal-v4`, distribution_count 2, no CVSG, Term 2025, paid docket).
- `record/documents/questions-presented.txt`, `petition.txt` (80 pages including the appendix; the argument section is about ten pages), and `brief-in-opposition.txt` (27 pages). `documents.json` shows none empty or truncated.
- `event.yaml`: kind petition, no stage recorded, so this is a cert-stage `distribution`-moment cell.
- Committed `metrics/statpack.md`: the modern-cert disposition, circuit, relist-count, CVSG, and salience-band sections, and the per-Term segment table under `sal-v4`.

## Anchor

The context freezes the band at `elevated`, and the segment table's heading is `sal-v4`, matching `salience_version`, so the band table is a valid anchor. Pooling the bracketed `reached` figures for `elevated` over the Terms strictly before OT2025 that the table renders (OT2017 through OT2024) gives about **17% (484 of 2,810 weighted)**. That is the population this petition sits in: paid petitions that were distributed at least twice. The terminal-band figure for `elevated` splits its grant family roughly two-thirds plenary grant and one-third GVR, so the plenary component of the anchor is on the order of 11%.

Two cautions about that anchor. First, this docket's two distributions are not a relist in the ordinary sense. The first distribution (for May 14) was cut short when the Court called for a response on May 11 after the City had waived; the second (July 29, for September 28) is the routine re-distribution once the brief in opposition came in. The band population treats both patterns alike, and I cannot separate them in the pack. A call for response is nonetheless a real positive signal, and it is the reason this petition reached `elevated` at all. Second, the September 28 conference has not happened, so from the Court's side this is the first conference with the petition fully briefed.

## Adjustments down, and why they dominate

- **No split, and the petition does not claim one.** All three questions ask the Court to clarify or refine Parker doctrine on "the facts of this case." The Fourth Circuit's opinion is unanimous, published, and rests on its own 2021 precedent in Western Star, which the petition does not cite or engage. The Court's only Parker merits cases since 2010 are Phoebe Putney (2013) and North Carolina Dental (2015), both brought by the FTC; a private-party Parker petition without a federal party and without a split is a weak class.
- **Vehicle problems the BIO documents persuasively.** The "heightened rigor" argument (QP 3) was not raised in either lower court. The petition never quotes the two South Carolina statutes, and section 5-7-145(B)(3) expressly contemplates an exclusive right to rent beach equipment on the beach, which makes this a poor case for arguing that displacement of competition was unforeseeable. The Local Government Antitrust Act bars damages, and the non-antitrust claims were abandoned below. The fourth argued issue corresponds to no question presented.
- **Petition quality and counsel.** The petition is short on argument, has drafting errors in the questions themselves, and was filed by a local firm with no apparent Supreme Court practice. The City retained experienced appellate counsel. Neither is dispositive, but both predict denial at the margin.
- **No amici.** A petition raising a genuinely live antitrust-federalism question would ordinarily draw at least one amicus at the cert stage; none has appeared in six months on the docket.
- **Fourth Circuit origin** grants at about 2.5% including GVRs, slightly below the modern-cert average, a small negative.

## Adjustments up

- **The call for response after waiver.** This is the one strong positive, and it is why I do not drop to the baseline-band floor. Somebody at the Court wanted to hear the City's side, most plausibly because the market-participant question has been left open since Omni (1991) and Phoebe Putney footnote 4, and some Justices are known to be interested in the reach of municipal antitrust immunity. The CFR is what puts the petition at `elevated`, so it is largely priced into the 17% anchor rather than an addition to it.

Netting these, I land at **0.06**: roughly a third of the pooled elevated anchor and about half of its plenary-grant component. That treats the CFR as real but the post-BIO picture as decisively unfavorable. A GVR is effectively excluded (no intervening decision), so the whole 0.06 is plenary grant.

## The other claims

- `relist-increment` 0.30. The relist-count cut shows about half of the petitions that reach two distributions go on to a third, but that pool mixes true relists with call-for-response redistributions like this one, and the hazard for a CFR petition facing a strong BIO is lower. I set it well above a cold petition's rate and well below the pooled shape.
- `cvsg-increment` 0.05. No federal party; the FTC's institutional interest in Parker keeps it off the floor.
- `summary-disposition-route` 0.05 conditional on grant. Nothing to GVR against; doctrinal question.
- `dissent-from-denial` 0.10. A CFR petition on an acknowledged open question is the profile that occasionally draws a statement respecting denial, but most such petitions still die silently.
- `big_case_score` 0.35. The doctrinal question would matter to municipal enterprises broadly; the parties, the idiosyncratic statute, and the likely narrowness of any ruling keep it in the middle of the range.

## Uncertainty and where to discount me

- I cannot see who called for the response or why. If the CFR came from a Justice actively looking for a market-participant vehicle, the probability is meaningfully higher than 0.06; if it was routine caution on a petition with a waived response, it is lower.
- The band anchor pools two distinct trajectories (relist vs. CFR redistribution) and I have adjusted for that by judgment rather than by a published cut.
- Retrieval was light by choice: one corpus `query` (not topic-specific, since the corpus carries no text filter on SCOTUS rows) and two CourtListener searches, one to confirm the Fourth Circuit opinion is published and one to confirm the Court's recent Parker merits docket. I did not look up this docket on CourtListener; the provisioned snapshot is dated today.
- I know of no outcome for this petition; the conference is eleven days away.
