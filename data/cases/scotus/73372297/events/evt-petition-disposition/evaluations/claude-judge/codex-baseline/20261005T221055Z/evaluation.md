# Evaluation — codex-baseline — scotus/73372297 / evt-petition-disposition

## The cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`, opened 2026-05-20).
Outcome: `actual_disposition: denied`, `actual_granted: 0`, resolved 2026-10-05
after the September 28, 2026 conference, one distribution, no CVSG, no noted
dissent. No `record/opinion/` slot is staged; a cert cell declares no semantic
set, so no `semantic_grades` block is written.

## What the prediction got right

- `predicted_disposition: denied` → `correct = 1`.
- `probability = 0.004` → `brier_score = 0.004² = 0.000016`.
- The forecast (denial after the September 28 conference, zero further
  distributions, no CVSG, no writing) matched the realized docket. The claims
  block and the forecast document are not scored here.

## Segment base rate and skill

The prediction froze `band: baseline` under `salience_version: sal-v4`, matching
the statpack table heading, so the basis is `risk_set` and the figure is the
bracketed `reached` rate pooled over the rendered Terms strictly before 2025
(2017–2024, everything the pack holds within the ten-Term lookback):

| quantity | value |
| --- | --- |
| pooled weighted resolved (n) | 11,580 |
| `segment_base_rate` | 0.051209 |
| `brier_skill_score` | 1 − 0.000016 / 0.051209² = 0.99390 |

The candidate computed the identical figure (593 / 11,580) from the same
`statpack.json` fields. No version mismatch, no rendered-window divergence.

## Reasoning quality: 0.82

What drove the score up:

- The anchor is exact and correctly scoped: it pools the sal-v4 `baseline`
  risk-set figures over 2017–2024, excludes the 2025 and 2026 rows by name, and
  explains why the terminal-band figures (0.6%–1.8%) are the wrong prior for a
  live petition. That is the cleanest statement of the risk-set/terminal
  distinction of the three candidates.
- It is explicit that the relist, CVSG, and originating-circuit cuts are pooled
  descriptive marginals and refuses to multiply them. Good discipline.
- The case analysis is sound and verified against the decided snapshot: paid
  petition, private petitioner, Federal Circuit origin, waiver on June 17, one
  distribution on June 24, and the petition's own disclosure that the lower
  courts rested on an untimely request for review. It treats the petition's
  accusations as allegations, not facts, and flags that the appendix was not
  provisioned so the deadline's exact basis is unverified. That is the right
  epistemic posture.
- It states its corpus-freshness limits (committed statpack as of September 16,
  snapshot creation date September 15) rather than asserting currency.

What held it back:

- It declines to lower the number "merely because the litigant is
  self-represented". As a stance against prejudging a litigant it is
  defensible, but as forecasting it sets aside the single strongest observable
  predictor of denial on this docket without saying what evidence would have
  licensed using it. The number still lands at 0.004 because the other factors
  carry it, which suggests the stated principle did little work.
- The Rule 10 excursion (two failed web opens, a failed `pdftotext`, then an
  in-memory read of the 2026 rules PDF) adds nothing a cert analyst needs
  stated; Rule 10's content is not in doubt, and the time would have been
  better spent on the petition's "The Appeal" section, which it did read.
- `reasoning.md` carries process chatter (a read-only cache path, a tool that
  returned no visible content) that belongs in `retrieval.md` or a tooling
  note, and the prose is longer than its argument.
- The significance score of 0.18 reads high for a petition that supplies no
  vehicle for the program-level questions it invokes. That score is not part of
  this grade; I note it only because the rationale for it ("compensation
  procedure and privacy can matter beyond one claimant") is the one place the
  reasoning credits the petition's framing more than the record supports.

## Leakage

`mode: forward`. The log carries 32 calls (coverage 0.84). The five
`web-search` rows are `unobserved`, so each is graded on its query: a search
for Rule 10 language on supremecourt.gov and opens of the Court's rules PDF and
rules-guidance page. None names this case, its caption, its docket number, or
its parties. The captured shell rows show curl fetches of the same official
rules page and PDF and an in-memory `pypdf` read of Rule 10, nothing more
outward. No corpus query and no CourtListener call. The prediction was created
2026-09-16 on the 2026-09-16 snapshot, and the reasoning states that no
disposition or subsequent history was retrieved; nothing in the log
contradicts that. No sign of a decided case provisioned forward.
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
`leakage_suspected = false`.

## Stakes

My own read: `evaluator_score = 0.02`. One claimant's Vaccine Act damages
dispute, affirmed below on timeliness in a nonprecedential order, with no legal
question through which the Court could reach the policy debate the petition
cites.
