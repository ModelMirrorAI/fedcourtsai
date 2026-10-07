# Evaluation: codex-baseline — Francis v. Allstate Insurance Co. (scotus/73246321, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list
after the September 28 Long Conference, on a single distribution, with no noted
dissent (`actual_disposition: denied`, `actual_granted: 0`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band
  `baseline` under `sal-v4`, matching the statpack table's heading, so the
  bracketed `reached` figure applies, pooled resolved-weighted over the
  rendered Terms strictly before Term 2025 (OT2017–OT2024, n = 11,580): 5.12%.
  The caption renders 10 of 10 Terms, so no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.990.

No votes are scored on a cert cell; `vote_accuracy` is omitted. No semantic
set is declared on a cert event, so there is no `semantic_grades` block.

## Reasoning quality: 0.87

A careful, well-bounded rationale that is a near peer of claude-baseline's, with
one distinctive strength and a few dilutions.

What it got right:

- **Anchor computed correctly and scoped correctly.** It pooled the displayed
  baseline `reached` rows for Terms 2017–2024 to about 5.12% over n = 11,580,
  excluded Terms 2025 and 2026, and said what the figure is and is not (a
  private-petitioner risk-set rate, not the terminal rate, not a government
  rate). It also noted that the terminal relist and CVSG cuts describe
  population shape rather than increments from this petition's state — an
  accurate reading of what those tables can support.
- **Checked the one cited authority.** It read *Haines v. Kerner* through
  CourtListener and correctly characterized it as a pleading-construction
  holding about a prisoner's federal civil-rights complaint, which does not
  itself say state civil appellate deadlines yield to pro se status. That is
  real legal work the other candidates did not do, and it goes to exactly why
  question three fails.
- **Right discount for the right reason.** It states that pro se status alone
  is not the discount; the missing ingredient is a demonstrated cert-worthy
  issue and a clean vehicle. It also reads the respondent's extension-then-
  waiver correctly (an extension is not a judicial request for a response).
- **Epistemic hygiene.** It treats the petition's statement of the case as the
  petitioner's description rather than verified findings, declines to infer
  untimeliness in this Court from the filed/docketed date gap, and labels the
  unknown procedural defect a vehicle uncertainty rather than an established
  jurisdictional bar because the appendix was not provisioned.

Where I discount:

- It stops short of naming the adequate-and-independent-state-ground problem
  as the operative reason review is unavailable, treating it only as something
  it "cannot establish" without the orders. The petition's own statement that
  the appeal was dismissed as untimely is enough to put that doctrine at the
  center of the analysis, and claude-baseline does so.
- A paragraph on tool failures (uv cache, unusable web results) belongs in the
  tooling report rather than the rationale; it dilutes the legal reasoning
  without changing it.
- The stakes read of 0.18 is reasoned ("broader access-to-courts
  implications"), but the rationale's own account of the record — no systemic
  showing, no conflict — undercuts it. This bears on the big-case dimension
  rather than `reasoning_quality` and is noted, not penalized here.

The forecast document and the claims block were read for context only and are
not scored here.

## Leakage: not applicable (forward)

The prediction was created 2026-09-16, before the September 28 conference, so
the outcome did not exist to be retrieved. The captured log (24 calls, result
capture 0.92) shows provisioned inputs, the statpack, two web searches recorded
as `unobserved` (graded on their queries: Supreme Court Rule 10 and the *Haines*
citation — general authority, not this case), and CourtListener lookups confined
to *Haines v. Kerner* (1972). No query reaches this docket or its disposition,
nothing under `data/qp-topics/` was read, and the rationale states it neither
sought nor encountered the disposition. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big-case read: 0.02

An individual's insurance dispute lost on a Georgia procedural default, pro se,
respondent waived, denied on the first conference with no separate writing.
Nothing here reaches beyond the parties. (The predictors' own scores were
visible in the staged `prediction.json` before I recorded this; the read is
mine, but I note the exposure.)
