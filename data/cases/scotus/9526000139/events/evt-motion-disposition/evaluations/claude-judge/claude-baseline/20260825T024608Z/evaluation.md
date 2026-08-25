# Evaluation — claude-baseline, evt-motion-disposition (scotus/9526000139)

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

- **`correct` = 1.** Predicted `denied`; actual `denied`.
- **`brier_score` = 0.09** — (0.30 − 0)².
- **`reasoning_quality` = 0.9.**

## What drove the reasoning grade

The strongest reasoning of the three candidates, and the best-resolved
number. The candidate anchored on the correct strictly-prior statpack pool
(225/30, 13.3%), carried the section's own caveats (right-censored escalation
signals, the scored population sitting higher on the escalation ladder), and
then decomposed the outcome space explicitly: outright denial ~40%, partial
relief ~27% resolving denial-first, unqualified grant ~30%, withdrawn ~2%.
Every element that mattered to the realized outcome is present and correctly
weighted: the *unqualified*-grant framing of the scored claim, the
denial-first resolver on mixed orders, the post-CASA scope argument as the
applicants' strongest route, Purcell equities running *against* the stay in
this posture, and — the channel that actually resolved the cell — the
explicit residual "that relief issues only on the government's parallel
application" (26A124). That is precisely what happened: the Court granted the
stay on 26A124 and denied this application as moot. The prose also offers
honest sensitivity bounds (0.20–0.45) with the assumption that moves the
number named. This is what sound forward reasoning on an emergency
application looks like.

Held just below the top: the realized path (companion grant mooting this
application) was carried as a "small residual" rather than a weighted branch,
and given the SG's parallel application was known and two days older, a
sharper analysis might have put real mass on the moot-denial route
specifically. That is hindsight-adjacent, so it costs little.

The forecast document (referral 0.92 — realized; amici rising — realized, two
briefs; disposition mid-to-late August — realized 2026-08-24; separate
writings with Sotomayor/Kagan/Jackson dissents if granted — matches the
companion order's lineup) was read for context only and not scored.

## Leakage

Forward mode, genuinely unresolved at prediction (created 2026-08-20;
resolved 2026-08-24). The log shows two web searches and one corpus query; no
`retrieved_doc_date` at or after resolution; nothing touches
`data/qp-topics/`. The candidate's own retrieval note discloses that one
search result was dated 2026-08-12 (post-cutoff, still pre-resolution),
headlined parallel litigation, and was not opened — an honest disclosure that
counts *for* the cell's integrity. `influenced_prediction` =
`not_applicable`.

## Not written, and why

- `segment_base_rate`, `brier_skill_score`, `base_rate_basis` — harness's on
  an interim cell.
- `vote_accuracy` — never scored off a merits stage.
- `judgment_correct` — null; no judgment axis on an interim cell.
- `semantic_grades` — no block: an interim event declares no semantic set.
- `claim_scores` — harness-computed (`interim-v1`).
