# Evaluation — claude-baseline — evt-order-response-requested-disposition

## The cell and the outcome

This is an **interim** cell: disposition of stay application 26A124 (*Trump v.
California*), forecast after Justice Jackson called for a response on the
filing date. The Court **granted** the application on 2026-08-24 — an
unqualified full-Court stay of the district-court injunction pending appeal
and any cert petition, per curiam, with dissents from Justices Sotomayor
(joined by Justice Kagan) and Jackson. `actual_disposition` = `granted`,
`actual_granted` = 1.

## Scores

- **correct = 0.** The candidate predicted `denied`.
- **brier_score = 0.49** ((0.30 − 1)²).
- **Baseline and skill are the harness's on an interim cell.** I write neither
  `segment_base_rate` nor `brier_skill_score`; `stamp-cell` pools the
  substantive-application grant rate over application Terms strictly before
  Term 2026. From the committed statpack that pool is Terms 2025 + 2024:
  30/225 ≈ 13.3%, clearing the registered 50-resolution floor, so I expect a
  stamped rate rather than a null; if it comes back null anyway, the rendered
  interim table is what could not support it. `base_rate_basis` stays null
  structurally — no band population exists for an application, and the frozen
  `context.band` is null (the normal interim shape).
- **No vote_accuracy** — not a merits cell (and no per-Justice votes were
  predicted). **No semantic_grades** — no semantic set is declared off
  merits. `claim_scores` is the harness's.

## Reasoning quality: 0.68

The richest analysis of the three candidates, and most of it is exemplary
craft:

- Correct base-rate work — the strictly-prior 13.3% pool, the floor check,
  and the right cautions (unconditioned pool, right-censored escalation
  columns read as shape only).
- The most complete factual reconstruction from the docket text alone: the
  parties, the First Circuit posture, the briefing calendar, the escalation
  ladder, and the singular/plural amicus-counter defect (frozen 6 vs. 13
  visible; I verified the split against the committed snapshot). The
  resolver-consistency reasoning on the amicus-increment claim was exactly
  the right way to price a claim whose conditioning state is contaminated.
- The conditional forecast was strikingly good on the parts the record now
  shows: it named full-Court referral before disposition (referral entered
  2026-08-24), a reasoned order with separate writings after the unusually
  long post-briefing gap, and — conditional on a grant — dissents from at
  least the three Democratic appointees, which is the realized lineup.

Judged against the outcome, the number is where it went wrong, and the file
itself shows why: it identified that government emergency applications
succeeded at a majority rate over OT2024–2025 and that this application sat
at the very top of the escalation ladder, then discounted its own strongest
signal to 0.30 on three counterweights that the realized order rejected —
the partial-stay collapse (the grant was unqualified), the merits-weakness
read, and a Purcell framing that treated the injunction as the status quo
where the Court evidently treated the executive order's operation as the
baseline being disturbed. Sound method, well-documented self-discounting,
but the final weighing ran against its own evidence; that is what separates
it from codex-baseline's 0.44 despite the deeper analysis.

## Leakage: none (forward)

Mode `forward`, created 2026-08-16, resolution 2026-08-24. I checked the
mis-provisioning exception: no post-resolution `retrieved_doc_date`, no query
for the disposition, and the reasoning treats the case as pending. The
companion-context searches (the First Circuit docket) are legitimate forward
signal. `influenced_prediction` = `not_applicable`.
