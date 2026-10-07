# Evaluation: claude-baseline — scotus/73291758, evt-petition-disposition

Cert-stage cell (event stage `cert`, moment `distribution`). Outcome: petition
**denied** 2026-10-05 after a single distribution for the 2026-09-28 long
conference, `actual_granted` 0, no noted dissent, no response ever requested.

## Quantitative

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.004 − 0)² = 0.000016.
- `segment_base_rate` = 0.0512 (`base_rate_basis` `risk_set`). Frozen
  `band: baseline`, `salience_version: sal-v4`; the statpack's segment table
  heading is "(sal-v4)", so the versions match. Pooled the bracketed `reached`
  figure weighted by `n` over OT2017–OT2024, every rendered Term strictly before
  Term 2025 (caption: 10 of 10 Terms rendered, no window divergence):
  593 / 11,580 = 0.05120; the unrounded JSON agrees at 0.05121.
- `brier_skill_score` = 1 − 0.000016 / 0.0512² = 0.9939.
- `vote_accuracy` omitted (cert cell).

## Reasoning quality: 0.85

A careful and correct rationale. The anchor is the right one and is computed
the way the evaluator computes it (bracketed reached, baseline band, OT2017–24,
~5.1%, n≈11,580), with the terminal cuts used only as corroboration and
labelled as such. The docket reading is exact: no brief in opposition *and* no
waiver docketed, distributed once after the response deadline lapsed — which is
what the record shows.

The legal analysis identifies the decisive points and draws them correctly:
the petition's own account that the constitutional claims were held forfeited
on appeal, and the adequate-and-independent-state-ground consequence; the lack
of any Sixth Amendment footing for an ineffective-assistance theory in a civil
protective-order case; the state-court origin; and a specific reason the GVR
share of the anchor does not transfer (Rahimi predates the state decisions and
was available to them, so it is not an intervening decision). The forfeiture
reading is held appropriately — the appellate order was not provisioned and
the rationale says so, with a stated direction for how the number would move
if that premise failed.

Minor deductions: the rationale leans on the petition's self-account of the
proceedings below without flagging that the petition is an interested pro se
narrative (codex-baseline is more explicit on that); and the stated reason for
putting the summary-route conditional above the population share is a bit
quick. Neither affects the soundness of the headline analysis.

## Leakage

Forward cell; `influenced_prediction` `not_applicable`, `retrieved_outcome_material`
false, `leakage_suspected` false. Log coverage 1.0, 25 calls. The one lookup of
this case's own docket is a forward-mode check that returned the filing date
(retrieved_doc_date 2026-05-04), a null termination date, and a last
modification of 2026-06-17 — i.e. it confirmed the case was open. The remaining
external calls looked for the Illinois decision below (nothing on
CourtListener) and ran one corpus query that returned no comparables. Nothing
dated at or after the 2026-10-05 denial was retrieved or sought. The
candidate's own `retrieval.md` and reasoning disclose the same.

## Big case

My independent read is 0.03 (see `big_case.notes`): a private family
protective-order dispute with no institutional party, no split, and forfeited
federal claims; the silent denial is consistent with that.
