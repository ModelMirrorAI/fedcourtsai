# Evaluation — gemini-baseline, evt-brief-response-disposition (scotus/9526000124)

## The cell and the scored numbers

This is an **interim** cell (`stage: interim`): the disposition of the
government's stay application in Trump v. California, forecast at the
response-filed moment. The realized outcome is **granted**
(`actual_granted: 1`, resolved 2026-08-24).

gemini-baseline predicted **denied** at probability **0.20**, so `correct = 0`
and `brier_score = (0.20 - 1)^2 = 0.64`.

The baseline and skill are the harness's on an interim cell: `stamp-cell`
pools the statpack's substantive interim grant rate over strictly-prior
application Terms (16/178 + 14/47 = 30/225 ≈ 13.3%, which clears the
50-resolved floor, so the stamped rate should be non-null) and writes
`segment_base_rate` and `brier_skill_score` itself; `base_rate_basis` is
structurally null. `claim_scores` (`interim-v1`) is the harness's. The frozen
`context.band` is null — the ordinary interim shape.

## What the prediction got right and wrong

Wrong on the scored axis: denial at 0.20 against a granted stay. The
procedural periphery held up — referral to the full Court at 0.95 (the
outcome records `referred_to_court: true`), quick disposition, and the
expectation of noted dissents on a contested emergency order — and its 0.20
edged claude-baseline's 0.15 by sitting slightly less far from the outcome, but
that is a difference in degree of the same wrong call.

## What drove `reasoning_quality` (0.4)

Structurally sound but shallow. It used the correct strictly-prior baseline
(30/225 ≈ 13.3%) and adjusted upward for the government-applicant conditional
and the case's profile, which is the right skeleton. But the case-specific
analysis is one paragraph of priors: Purcell as near-dispositive, denial as
status-quo-preserving, and a general sense that the executive order was
"legally suspect." It engaged none of the filings, missed the
justiciability/ripeness route the applicants actually pressed (which
codex-baseline surfaced from the same public record), and stated no account of
its residual uncertainty beyond the number itself. It also describes the
injunction as "nationwide" where the record before the other candidates —
and claude-baseline's more careful read — has it covering the 23 plaintiff
states and D.C.; a small error, but of the kind more retrieval would have
caught. The one web search it ran confirmed pendency and little else. Given
the outcome, a rationale that treats Purcell as the dominant signal without
testing the applicants' actual arguments is thin support for a 0.20.

## Leakage

`forward`, and genuinely so: snapshot 2026-08-16, resolution 2026-08-24. The
single web search's stated purpose and reported result was that the case
remained pending; the log's `result_capture_coverage` is 0.0, so its rows are
graded on their queries, and no query sought a disposition — which did not
exist at prediction time. `influenced_prediction = not_applicable`,
`leakage_suspected = false`. No sign of a mis-provisioned decided case.
