# Evaluation — codex-baseline — scotus/9526000203 evt-brief-response-disposition

## Stage and ownership of the numbers

This is an **interim** cell (stay application 26A203). The outcome is
`granted` (`actual_granted` = 1), resolved 2026-08-31 by the full Court after
referral, over a dissent by the Chief Justice joined by Justices Sotomayor,
Kagan, and Jackson. On this stage `segment_base_rate` and `brier_skill_score`
are the harness's (stamped from the committed statpack's interim section;
`base_rate_basis` stays null structurally), and `claim_scores` is computed in
code. At this evaluation's pack vintage the strictly-prior pool (application
Terms 2025 + 2024) is 296 resolved / 31 granted ≈ 10.5%, above the 50-resolved
floor, so a stamped rate should exist. `vote_accuracy` is omitted — never
scored off the merits stage.

## Accuracy

Called `granted` at **0.68** — right side, the most conservative of the three
candidates. `correct` = 1; Brier = (0.68 − 1)² = **0.1024**. My elicited
values; the harness restamps both.

## Reasoning quality: 0.92

The best-sourced rationale of the three, and the strongest on the
considerations that cut against its own call:

- **Anchor discipline.** It pooled the strictly-prior substantive slice
  (quoting the pack as committed at run time: 30/225, 13.3%), correctly
  labeled it an unconditioned rate rather than a response-filed rate, and
  carried the escalation-ladder selection caveat.
- **Primary-source depth.** Rather than working from docket descriptions, it
  located and read the August 7 D.C. Circuit opinion itself (working around a
  text-less canonical copy via a duplicate indexed copy — disclosed candidly),
  and characterized both the majority's grounds (congressional control over
  White House construction, likely absence of statutory authority for the
  ballroom) and Judge Rao's dissent (standing, statutory authority, the
  security equities) accurately.
- **Engagement with the contrary case.** Uniquely among the candidates, it
  weighed the injunction's tailoring — the carve-outs for underground and
  protective work that partially accommodate the claimed security harm — as a
  concrete reason the estimate should sit "well below certainty", which is a
  sound reason its 0.68 sat below claude-baseline's 0.72.
- **Measurement care.** Its handling of the frozen-context amicus anomaly
  (`amicus_briefs: 0` frozen against six visible filings) was exactly right:
  it stated the discrepancy, priced the increment claim against the frozen
  zero, and separated the measurement question from the substantive one. The
  resolved outcome (`amicus_briefs: 7`) bore that reading out.
- The forecast document's structure also resolved well: referral called at
  0.96 (it happened), an unqualified stay more likely than not (granted),
  timing "before or just after" the D.C. Circuit's hold expired (the Chief
  Justice's interim stay came August 21, the full-Court grant August 31).

The small residue against a higher grade: the rationale is somewhat lighter
than claude-baseline's on why the pooled 13.3% understates a government-filed
contested application specifically (it asserts the applicant-class adjustment
more than it evidences it), and its uncertainty discussion, while honest, is
not quantified into a range.

## Leakage: none (forward)

Mode `forward`, genuinely open at prediction time (predicted 2026-08-20,
resolved 2026-08-31). The log shows consistent self-discipline: every
CourtListener search carries a `filed_before: 2026-08-19` filter, and the
document reads are the pre-decision CADC materials (the April 17 stay order,
the August 7 judgment). The log's uncaptured rows are engine-echo duplicates
of captured wrapper calls (each MCP row repeats a captured `shell` call's
parameters), graded on their queries per the capture rule; none seeks outcome
material, and the reasoning states it did not retrieve or encounter the
disposition — consistent with the log. `influenced_prediction` =
`not_applicable`.

## Semantic grades

None — an interim event declares no semantic set.
