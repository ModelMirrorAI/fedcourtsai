# Evaluation — codex-baseline, evt-motion-disposition (scotus/9526000245)

## The cell and the outcome

This is an **interim**-stage cell (`event.yaml` stage: `interim`): application
26A245 for an injunction pending appeal, submitted to Justice Barrett on
2026-08-17 and docketed 2026-08-25. The outcome is `denied`,
`actual_granted = 0`, resolved 2026-08-27, with the interim ladder never
firing (`response_requested: false`, `referred_to_court: false`,
`amicus_briefs: 0`).

## Scores

- **`correct` = 1.** `predicted_disposition` = `denied` matches exactly.
  (Written per the contract; re-stamped in code.)
- **`brier_score` = 0.000025** — `(0.005 - 0)^2`. (Re-stamped in code on an
  interim cell.)
- **`segment_base_rate` and `brier_skill_score` are left null, and
  `base_rate_basis` stays null: interim cell**, so both are the harness's —
  `stamp-cell` pools the statpack interim section over application Terms
  strictly before OT2026. For the reader: the currently committed table pools
  OT2025 (16/178) + OT2024 (14/49) = 30/227 ≈ 13.2%, above the 50-resolved
  floor, so a non-null stamped rate is expected. `context.band` is null —
  the ordinary interim shape.
- **`vote_accuracy` omitted** — never scored off a merits stage; no votes
  predicted.
- **No `semantic_grades` block** — no semantic set declared on an interim
  event. **`claim_scores`** is the harness's (`interim-v1`); not filled here.

## Reasoning quality: 0.88

A rigorous, record-driven rationale, close behind claude-baseline's.

Strengths:

- **The deepest engagement with the actual dismissal order of any
  candidate.** It read the district court's July 28 Rule 4 order and argues
  from its specific grounds — improper joint form, the individual nature of
  habeas relief, total failure to exhaust Wisconsin remedies, futility of
  amendment, COA declined — which is precisely the material that makes an
  injunction pending appeal near-impossible under the governing standard.
- **Correct baseline discipline with the right caveat.** It pools the
  strictly-prior Terms (quoting 30/226 ≈ 13.3% from the pack as committed at
  its run date), notes the pool clears the floor, and — uniquely among the
  three — invokes the statpack's own registered caveat that the scored
  population sits higher on the escalation ladder than the pooled cohort,
  using it to justify the downward adjustment rather than as decoration.
- **Disciplined evidence handling**: the related dismissed civil action is
  used only "as a party-and-presentation signal, not as the content of this
  application"; the unread August 5 Seventh Circuit entry is flagged and its
  contents explicitly not inferred; the throttled opinion search is
  disclosed; and it states outright that no disposition of this application
  was used. That is model epistemic hygiene for a forward cell.
- The ladder claims (0.015 response, 0.06 referral, 0.003 amicus) are
  reasoned — referral priced above response for the right institutional
  reason (a Circuit Justice can refer without being persuaded) — and all
  resolved in its favor, as did the several-days timing call (two days).

What separates it from claude-baseline's 0.92: slightly less SCOTUS-side texture
— no analogue application anchoring the disposition and timing numbers, and
no discussion of what actually earns grants in this pool — so the step from
the 13.3% pool down to 0.005 rests a little more on the merits reading alone.
The unread application text carries the same acknowledged uncertainty as
claude-baseline's.

## Leakage

Forward mode, confirmed: the prediction is dated 2026-08-25, the denial
2026-08-27, so no outcome existed at prediction time. The log's captured
calls (coverage ≈ 0.66 — the unobserved rows are the MCP-side echoes of
shell-wrapped calls whose wrappers were captured; graded on their queries
where uncaptured) show exclusively pre-disposition lower-court retrieval:
district docket and entries (self-limited with `date_filed lte 2026-08-25`
filters — a notably clean habit even where nothing later existed), CA7
searches that returned nothing, the related civil docket, and statpack
reads. Its retrieval note states, and the log corroborates, that no search
sought this application's outcome. One trailing call carries harness
redaction markers (credential-shaped text removed at capture) — read as
removed text per the capture rules, not as outcome material. No
`data/qp-topics/` read. `influenced_prediction` = `not_applicable`,
`retrieved_outcome_material` = `false`.
