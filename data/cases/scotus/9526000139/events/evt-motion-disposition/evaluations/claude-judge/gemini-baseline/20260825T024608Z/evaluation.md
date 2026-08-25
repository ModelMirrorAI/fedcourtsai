# Evaluation — gemini-baseline, evt-motion-disposition (scotus/9526000139)

## The cell and the outcome

Interim-stage cell (`event.yaml` stage: `interim`): stay application 26A139,
Alabama, et al. v. California, et al., seeking a stay of the D. Mass.
nationwide injunction against the President's election-administration
executive order. Outcome: `actual_disposition: denied`, `actual_granted: 0`,
resolved 2026-08-24 — the Court granted the full stay on the Solicitor
General's companion application 26A124 (per curiam; Sotomayor, joined by
Kagan, and Jackson dissenting) and denied this duplicative states'
application **as moot**. I read `actual_granted` as recorded.

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
the **harness's** (stamped from the committed statpack) and `base_rate_basis`
is structurally null — the interim pool is no salience-band product. The
committed statpack's interim table supports the strictly-prior pool (OT2024
47/14 + OT2025 178/16 = 225 resolved / 30 granted ≈ 13.3%, above the
50-resolved floor), so I expect a stamped rate rather than a null.
`claim_scores` is likewise the harness's (`interim-v1`).

## Scores

- **`correct` = 0.** Predicted `granted` (p = 0.65); actual `denied`.
- **`brier_score` = 0.4225** — (0.65 − 0)².
- **`reasoning_quality` = 0.45.**

## What drove the reasoning grade

The core substantive instinct was sound and was, in substance, vindicated:
the candidate reasoned that this Court would be willing to stay a nationwide
injunction against federal executive action on the emergency docket, and the
Court did exactly that — but on the Solicitor General's companion application
26A124, denying *this* application as moot. The analysis failed at the layer
this cell actually scores, in three connected ways:

1. **It never engaged with the event's semantics.** The scored claim is an
   *unqualified grant of this application*. Both sibling candidates worked
   through the denial-first reading of mixed relief and the risk that relief
   issues on the parallel application; this one mentions 26A124 only as a
   signal of "the gravity of the federal interest" — reading the companion as
   *upward* evidence when, for this specific application, it was the main
   route to an ungranted resolution. The prose even hedges "grant the stay
   (or grant it in part)" without noticing that a partial grant resolves as
   denied under the registered resolver.
2. **The probability sat far above what the reasoning supports.** From a
   13.3% strictly-prior baseline (correctly retrieved), the candidate moved
   to 0.65 on ideological-composition grounds alone, with no decomposition of
   relief shapes and only a one-sentence wave at Purcell ("the Court may view
   the district court's injunction itself as the disruptive action").
3. **A claim-contract misreading.** It set `response-requested-increment` to
   1.0 "because the event has already occurred" — the increment is vacuous
   once the rung fired pre-cutoff and the harness masks it, which both
   siblings recognized (0.01/0.02). No score consequence (the mask absorbs
   it), but it signals a thinner grasp of the declared claim set.

Real positives keep the grade near the middle rather than lower: correct
statpack pool with the floor implicitly cleared, genuine retrieval (a
CourtListener search and a web search, honestly logged), an explicit
statement that no outcome was found and the application appeared still
pending, and referral/amicus increments (0.9/0.95) that both resolved true.
The forecast document was read for context only and is not scored.

## Leakage

Forward mode, genuinely unresolved at prediction (created 2026-08-21;
resolved 2026-08-24). The log shows one CourtListener search for `26A139` and
one web search; searching for the application's current state is legitimate
forward retrieval, and the candidate's own note that it found no disposition
is consistent with none existing yet. No `retrieved_doc_date` at or after
resolution; nothing touches `data/qp-topics/`. `influenced_prediction` =
`not_applicable`.

## Not written, and why

- `segment_base_rate`, `brier_skill_score`, `base_rate_basis` — harness's on
  an interim cell.
- `vote_accuracy` — never scored off a merits stage.
- `judgment_correct` — null; no judgment axis on an interim cell.
- `semantic_grades` — no block: an interim event declares no semantic set.
- `claim_scores` — harness-computed (`interim-v1`).
