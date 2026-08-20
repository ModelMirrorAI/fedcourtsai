# Rationale — claude-baseline on scotus/73500252 (evt-petition-disposition)

**P(grant family) = 0.55.** Forward-mode cert cell at `moment: distribution`;
snapshot of 2026-08-20 (fresh — it carries the August 19 reply and
redistribution entries), band `elevated` under sal-v3, distribution_count 2,
no CVSG, Term 2025.

## Anchor

The statpack's per-Term "Segment base rate by salience band (sal-v3)" table,
`elevated` column, bracketed `reached` figures pooled over Terms strictly
before this case's (OT2017–OT2024, all eight rendered prior Terms): weighted
by the bracketed denominators this pools to roughly **20%** (n ≈ 3,419) —
the rate a live elevated-band paid petition faces, and the yardstick this
cell is scored against. The salience version matches the frozen context's
(`sal-v3`), so the band table is the right anchor.

## Adjustments up (large, cumulatively ~2.7x the anchor)

1. **The Court has already engaged this exact case and question.** It CVSG'd
   Flagstar's prior petition (No. 22-349), granted the companion *Cantero*,
   and GVR'd this case in June 2024. The QP was certworthy once; the remand
   failed to produce uniformity.
2. **A mature, acknowledged circuit split, post-remand.** Second Circuit
   (*Cantero III*, May 5, 2026: preempted) against the First (*Conti*, 2025)
   and Ninth (this case: not preempted), with a further methodological split —
   the Ninth Circuit, over Judge R. Nelson's dissent, declined to perform the
   comparative analysis *Cantero* directed, on remand of this very case. The
   BIO does not deny the split; it argues transience.
3. **The federal regulator is on petitioner's side and wants uniformity.** The
   OCC filed below urging preemption and finalized a rule codifying that view
   (91 Fed. Reg. 29350, effective June 19, 2026).
4. **The Court called for a response** on June 15, 2026 after respondents
   waived — an affirmative act of attention preceding the split's completion.
5. **Cert-stage amici**: Bank Policy Institute, ABA, Chamber of Commerce, and
   MBA (filed through Sullivan & Cromwell).
6. **Vehicle quality is conceded on both sides.** Final judgment, a
   summary-judgment record on "significant interference," experienced counsel;
   the SG in 2023 called Flagstar's case the better vehicle among the same
   three, and the BIO itself concedes this is "a sound vehicle" if any
   petition is granted.

## Adjustments down (real, and why I stop at 0.55)

1. **The transience argument is the BIO's best card.** The OCC's rule preempts
   prospectively, so the split governs only the retrospective liability of
   three already-pending cases; the Court denied *Lusnak* (2018) and *Conti*
   (early 2026, pre-split) on this question. If the Court thinks the rule
   moots the future, denial is cheap. I discount this because the rule's own
   validity is contested (12 U.S.C. § 25b(c) substantial-evidence challenges
   are previewed in the BIO), five-year review makes it unstable, and the
   methodological question — what *Cantero*'s comparative analysis requires —
   reaches far beyond IOE laws.
2. **A competing vehicle exists.** The *Cantero III* plaintiffs' petition is
   pending; if the Court grants that one instead and ultimately holds against
   preemption, this petition is denied, not GVR'd. The grant-family paths
   through a companion grant are partly, not fully, offsetting.
3. **Base-rate humility.** Even strong-looking elevated-band petitions mostly
   die; the reached-rate anchor already conditions on being distributed, and
   the signals above overlap with what put the case in `elevated` in the
   first place.

Net: roughly 0.40 plenary grant of this petition + 0.11 hold-then-GVR via a
companion merits decision + 0.03 other summary routes ≈ **0.55 grant family**;
`predicted_disposition: granted` as the modal single route, `granted: 1`.

## Claims

- `disposition` 0.55 — restates the top-level probability.
- `relist-increment` 0.78 — from the frozen state of two distributions. Nearly
  every grant path adds a distribution (relist-before-grant practice, or the
  eventual post-hold distribution), and a split-acknowledged petition with a
  requested response that is denied anyway is still often relisted once; only
  a clean first-look denial at the long conference resolves this false.
- `cvsg-increment` 0.05 — the SG already answered a CVSG in this case's prior
  round and the OCC has since ruled; a second invitation is very unlikely.
- `summary-disposition-route` 0.20 (conditional on grant) — dominated by
  hold-then-GVR if *Cantero III* is the granted vehicle; summary reversal
  possible but unlikely on a fact-inflected standard the Court itself declined
  to apply summarily in 2024.
- `dissent-from-denial` 0.15 (conditional on denial) — banking preemption
  denials rarely draw writings, but a completed split over the application of
  a two-year-old precedent, with the regulator's rule in tension with two
  circuits, gives an above-baseline chance of a statement or dissent.

## Uncertainties and discounts

- I could not verify the *Cantero III* petition's docketing or conference
  calendar live: CourtListener's docket search returned no SCOTUS dockets for
  "Cantero" (the search index does not appear to cover scraped SCOTUS
  dockets), so the companion-petition landscape rests on the BIO's July 30,
  2026 representations. If *Cantero III*'s petition is set for the same long
  conference, the hold/coordination probability shifts among grant-family
  routes but moves the family total little.
- Both `fedcourts query` attempts against the corpus service timed out
  (180s ReadTimeout each), so no corpus priors inform this cell; the
  base-rate anchor is the committed statpack only (its band table is exactly
  the scored yardstick, so the loss is mainly of analogous-case color, not of
  the anchor). Per the prompt's freshness rule: no claim here is concluded
  from corpus state; the committed statpack is the only corpus-derived input.
- The two "distributions" are not two conference considerations: the first
  (June 25 conference) was superseded by the June 15 response request, so the
  petition has in fact never been conferenced. The frozen
  `distribution_count: 2` governs the increment claim regardless; I flag the
  reading so the relist number is interpreted from the right state.
- My main substantive uncertainty is how much weight the Court gives the
  respondents' transience theory. If a maintainer reads this cell against a
  later denial, that is the likeliest reason I was high.
