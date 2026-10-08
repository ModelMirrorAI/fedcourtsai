# Evaluation of codex-baseline — scotus/9026000121, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`), Term
2026 by docket number (No. 26-121). Outcome: petition **denied** on
2026-10-05 after a single distribution for the September 28, 2026 conference,
with no noted dissent. Forward mode. No `record/opinion/` slot, the ordinary
state on a cert cell; no semantic set is declared, so no `semantic_grades`
block is written.

**Scores.**

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.000144 | (0.012 − 0)² |
| `segment_base_rate` | 0.0501 | `baseline` band, bracketed `reached` figures, Terms 2017–2025 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4` |
| `brier_skill_score` | 0.9427 | 1 − 0.000144 / 0.0501² |
| `reasoning_quality` | 0.82 | below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Baseline.** The frozen context carries `band: baseline` under `sal-v4`,
matching the statpack table's heading, so the risk-set basis applies. The
`baseline` column's bracketed `reached` rates, weighted by their bracketed
`n`, pooled over the rendered Terms strictly before 2026 (2017 through 2025),
give 0.0501 over a weighted n of 12,720. This is the same figure the candidate
itself computed (0.05010888 over n=12,720), by the same method, and it agrees
with the harness's pooling rule, which I checked against the in-code helper.
The caption renders 10 of 10 Terms, so there is no window divergence to flag.

**What the prediction got right.** The disposition, with a probability
(0.012) about a quarter of the band anchor. The highest probability of the
three candidates, so the weakest Brier and skill on this cell, but still far
better than the baseline, and the gap to the other two is within the range
honest judgment allows on a petition of this shape.

**Reasoning quality (0.82).** This is the most carefully constructed rationale
of the three. It opens by stating its information set precisely, including
what it did not have (no opposition, no appendix text) and the epistemic status
of everything it relies on (facts attributed to the petition's account, not
independently inspected). It states the anchor, the pooling, the weighting,
the exclusion of the case's own Term, and the reason not to substitute the
terminal rate. It surveys the wider statpack cuts and correctly declines to use
them as anchors because they describe terminal states. Then it argues the
discount with reasons that are specific to this record and checkable against
the provisioned petition:

- The federal theory rests on unresolved predicate facts: the petition's own
  reproduction of the appellate decision says the LinkedIn material did not
  fix when the new employment began, and the November 17, 2023 agreement
  against the December 14, 2023 order is not itself proof of concurrent
  practice. The petition confirms both dates and the LinkedIn basis.
- Caperton treats constitutionally compelled recusal as exceptional and
  distinct from broader conduct rules; the candidate checked this against the
  opinion text through CourtListener and cites the majority rather than the
  dissent, which is good practice.
- No developed conflict; the petition pitches first impression.
- Question 2 is a state-law fee ruling, a weak independent ground.
- Procedural complexity (unreported intermediate decision, state high court
  grant on a different question then dismissal, mandate and reconsideration
  disputes), correctly treated as uncertainty rather than as a bar the
  candidate presumes to resolve.
- Weak attention signals, correctly described as non-dispositive.

The nonzero residual is justified in terms a reader can audit (the
underlying employment documents might support a cleaner question; a limited
remand is possible).

Two things keep it just below claude-baseline. First, it treats the response
waiver more lightly than the record warrants: the waiver-then-no-call pattern
is the single most informative pre-decision signal for a paid petition at
first distribution, because the Court calls for a response before it grants,
and the rationale lists it among signals that "give little reason to lift"
rather than as an affirmative reason to discount. Second, it does not make the
GVR point about Question 2 (the Court does not GVR on a state court's
intervening decision), which is the cleanest reason that question adds
nothing. The rationale's length also slightly outruns its content; the
epistemic hedging is admirable but some of it restates the same caveat. None
of this is an error, and the resulting number is a defensible reading of the
same evidence.

**Leakage.** Forward cell; the log records `mode: forward` with
`result_capture_coverage` 0.926 (25 of 27 calls captured). The two
`unobserved` rows are a web-search call carrying two queries, one for Rule 10
on supremecourt.gov and one for Caperton's judicial-disqualification standard,
and a page-open of the Cornell LII copy of Rule 10. Graded on their queries,
neither names this petition, its number, its caption, or its outcome, and the
candidate's retrieval.md says both returned no usable content. The captured
calls are provisioned reads (prompt, schemas, event, context, snapshot,
documents, petition slices, statpack sections, and only the top-level keys of
statpack.json), a CourtListener citation lookup for 556 U.S. 868 and a
`search_document` on that 2009 opinion. No `fedcourts query` call was made. No
document date on or after the 2026-10-05 resolution, nothing under
`data/qp-topics/`, and the rationale states it neither sought nor learned the
outcome, consistent with the log. The prediction's snapshot (2026-10-04)
predates the denial, so this is not a mis-provisioned decided case.
`retrieved_outcome_material` false, `influenced_prediction` `not_applicable`.

**Big case.** My own read is 0.05: a private Maryland fee dispute whose
Caperton hook turns on an unresolved fact, denied silently on the first
conference, with no reaction. The candidate's 0.24 reads the hypothetical
national reach of a ruling on recalled judges into the stakes of this petition;
I weight the petition as filed and decided. As noted on the companion
write-ups, the predictors' `big_case_score` values were visible in the staged
`prediction.json` I read for the probabilities, so my read is independent in
substance but was not formed strictly before seeing theirs.

**Not scored here.** The `claims` block and `predicted_reasoning.md` are the
harness's and were read for context only; `vote_accuracy` is omitted on a cert
cell by rule.
