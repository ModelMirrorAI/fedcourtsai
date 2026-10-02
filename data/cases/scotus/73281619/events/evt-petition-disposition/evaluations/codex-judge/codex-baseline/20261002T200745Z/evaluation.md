# Evaluation: codex-baseline

## Outcome and quantitative score

This cert-stage evaluation scores the blinded prediction from run
`20260918T174135Z` against the supplied outcome: `granted`, `actual_granted = 1`,
plenary route, resolved October 1, 2026. The provisioned October 1 snapshot
records a grant limited to Question 1. The predicted label `denied` is not an
exact match, so correctness is **0**. P(grant) = 0.30 gives
**Brier = (0.30 - 1)^2 = 0.49**. A minority-probability grant occurring is not,
by itself, evidence that the underlying analysis was unsound.

## Baseline

The prediction's own frozen context supplies Term 2025 and band `elevated`
under `sal-v4`. The committed `metrics/statpack.md` table uses that same
version, so `risk_set` is the appropriate basis. I pool the bracketed reached
rates over all rendered rows strictly before Term 2025: 2017–2024. The table
renders 10 of 10 Terms, 2017–2026; there is no hidden-window divergence to flag.

The percentage/weighted-resolved pairs used are 17.5%/400, 15.9%/347,
13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336,
respectively for 2017 through 2024. Their resolved-weighted average is
**484.386 / 2,810 = 0.172379359430605**. This uses the rounded percentages
printed in the required Markdown surface; 484.386 is not an exact grant count.
The candidate reports an unrounded JSON-based numerator of 484 and rate
0.1722419929. That tiny precision difference is not a reasoning defect; this
evaluation consistently uses the rendered table rather than copying a
candidate's calculation. These are the committed pack's denial-reweighted
live/historical-slice estimates, not a fresh corpus measurement; I made no
corpus query.

The baseline Brier is 0.6849559246964957. Hence
**skill = 1 - 0.49 / 0.6849559246964957 = 0.2846255031415062**.
The forecast improves on this baseline for the observed grant despite missing
the modal label. This is a cell-level comparison, not a population claim.

## Reasoning quality: 0.86

The rationale is strong on source discipline and procedural interpretation.
It distinguishes the parties' accounts from independently verified facts,
explains that the reply and full lower-court record were not read, and separates
two distributions from two completed post-briefing considerations. The recorded
May 14 response request between the May 12 distribution and later completed
briefing supports its caution about mechanically labeling this an ordinary
relist. Its treatment of amicus participation as attention rather than
independent proof of legal merit is appropriately restrained.

The doctrinal analysis separates substantial burden, equal-terms comparators,
invited error, preservation, and the threshold statutory-coverage objection.
The opposition's printed pages 27–28 and 35–36 support identifying those
objections. The rationale does not simply adopt the opposition's assertion of
an independent state-law jurisdictional bar, and it acknowledges the petition's
contrary account of preservation and the character of the legal question.
Its narrow Livingston check is described as a check on the argument, not a
matched empirical sample. The upward adjustment from the frozen-band prior is
explicitly judgmental and supported by identified attention and legal-issue
signals.

The principal limitations are the uncertain strength of the asserted split,
the unread reply, and the absence of an empirically grounded mapping from the
identified signals to the particular 30% figure. The analysis could more fully
separate the risk associated with Question 2 from the possibility of granting
Question 1 alone. The recorded limited grant makes that possibility salient,
but supplies no explanation of how the Justices weighed the competing vehicle
arguments. The quality score rewards disciplined reasoning, not agreement
with an inferred rationale for the actual order.

## Leakage and scope

The log and frozen context identify a forward prediction on September 18,
before the October 1 resolution. Of 34 logged calls, 31 results are captured
and three web rows are unobserved (coverage 0.9117647058823529). Those rows
target general Justice Department RLUIPA material, not this petition's
disposition. The retrieval note also describes a general Holt search. The
older Livingston citation lookup and Holt excerpt are precedent research,
not retrieval of this case's outcome. No logged query or reasoning indicates
access to the disposing order or a mis-provisioned decided case.

The candidate says the web requests returned no visible content; the
unobserved markers cannot independently establish emptiness or failure. I rely
instead on their scope, the forward chronology, and the rationale. Outcome
material is not shown as retrieved, influence is `not_applicable`, and
`leakage_suspected` is false.

Only `reasoning.md` receives the qualitative score. The forecast document was
read but remains unscored, quantitative claim scores are left to the harness,
and neither vote accuracy nor semantic grades applies at cert. The optional
independent stakes assessment is omitted.
