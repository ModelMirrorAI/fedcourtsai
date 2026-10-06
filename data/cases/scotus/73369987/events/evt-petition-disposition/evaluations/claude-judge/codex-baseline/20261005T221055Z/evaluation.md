# Evaluation of codex-baseline — scotus/73369987, evt-petition-disposition

## Outcome and scores

The petition (No. 25-1296, Robinson v. Freeman) was distributed once, for the
September 28, 2026 long conference, and denied on October 5, 2026 with no
noted dissent and no response ever called for. Cert stage, `cert` on the event.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction
  froze `band: baseline` with `salience_version: sal-v4`, matching the
  statpack segment table's heading, so the bracketed `reached` figures apply,
  pooled resolved-weighted over OT2017–OT2024 (n = 11,580; the table renders
  all 10 Terms the pack holds, so no window divergence): 0.0512. The
  candidate's own pooling from the JSON companion (593 / 11,580 = 5.12%) is
  the same number at higher precision.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.9905.

## Reasoning quality: 0.85

A careful, well-bounded analysis. The anchor is exactly right, computed from
the statpack's JSON companion with the version match and the private-party
risk set stated explicitly, and the candidate correctly declines to treat the
terminal relist and CVSG cuts as forward hazards. The information boundary
section is a model of its kind: it names what was and was not read, that
every description of the lower proceedings is the petitioner's account, and
that the prior petitions (19-356, 23-1244) are pre-existing history disclosed
in the petition rather than this event's outcome.

The downward case is substantively sound: no demonstrated judicial conflict
(the Kentucky comparison is a policy difference, not a split), an unpublished
and procedurally tangled vehicle, a possible alternative state procedural
ground, the distance between Meyer, Kolender and Dimaya and the remedy sought,
and a shrinking remedial horizon as the children age out. The CourtListener
check on Dimaya was narrow and used only to characterise a cited authority.

Two things hold it just below claude-baseline. First, it expressly declines to
discount for self-representation ("not a mechanically estimated discount for
self-representation"), when pro se status is among the most reliable
cert-stage predictors on this docket; the number ends up in the right place
anyway, but the reasoning gives up a real signal on principle. Second, the
document is longer than its content requires and spends several paragraphs
on method disclaimers that do not move the forecast. The forecast document and
the claims block were read for context only and are not scored here.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`; the prediction was written on
September 17, 2026, before the September 28 conference and the October 5
denial. Of 34 calls, 29 are captured. The five unobserved calls are a web
search and four page opens aimed at the Supreme Court Rules (Rule 10 and the
Rules of the Court PDFs); graded on their queries, none names this case, its
parties, or its docket number. The two captured CourtListener calls fetch and
search Sessions v. Dimaya, 584 U.S. 148, a cited authority. No
`retrieved_doc_date` is on or after 2026-10-05, no query reaches this
petition's disposition, and nothing touches `data/qp-topics/`. The reasoning
states it did not retrieve a later docket or the disposition.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false. The case was genuinely open
when provisioned.

## Big case: 0.05 (my independent read, formed before reading the candidate's)

A pro se challenge to Colorado's parenting-time factors, unpublished below, no
response, no amicus, denied without comment. The abstract question would be
large if ever decided; this vehicle decided nothing and drew no attention.
