# Evaluation: codex-baseline — scotus/73303792, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), forward
mode. Outcome: petition **denied** on 2026-10-05 at its first and only
distribution (conference of 2026-09-28), no separate writing, no CVSG.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `denied` vs `denied`, exact label match |
| `brier_score` | 0.000036 | (0.006 − 0)² |
| `segment_base_rate` | 0.05121 | baseline band, sal-v4, risk-set pool (below) |
| `base_rate_basis` | `risk_set` | frozen `context.band` + `context.salience_version` both present |
| `brier_skill_score` | 0.9863 | 1 − 0.000036 / (0.05121 − 0)² |
| `reasoning_quality` | 0.88 | below |

**Base rate.** The prediction's frozen context carries `band: baseline` and
`salience_version: sal-v4`; the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the bracketed `reached` figures are the right
population. Pooling resolved-weighted over every rendered Term strictly before
Term 2025 (OT2017–OT2024, eight rows) gives 593 / 11,580 = 0.05121. The
candidate computed exactly this figure from `statpack.json` and said so. The
table renders 10 of 10 Terms, so the rendered window is the pack's whole window
and no divergence from the shipped lookback needs flagging.

## What the prediction got right and wrong

Right on everything the cell scores: denial, at 0.6%, earning nearly all the
available skill against the band. The outcome was the routine first-conference
denial with no writing that the rationale described as the base case.

## Reasoning quality (0.88)

This is the most careful of the three rationales, and the one that does
something the others do not: it tests the petition's central cert hook against
the source. The petition places VanderKodde v. Mary Jane M. Elliott (6th Cir.
2020) on the expansive side of a Rooker-Feldman split; the candidate pulled the
opinion through CourtListener and found that its majority applies an
injury-source inquiry that distinguishes injury from a state judgment from
injury attributable to other conduct, which undercuts the petition's account of
its own circuit's rule. That is a substantive reason to discount the split, not
a surface signal, and the candidate states its limits correctly (it does not
prove every asserted conflict nonexistent).

The rest is sound: the anchor is pooled exactly and attributed; QP 2 is
recognised as two contested applications rather than a rule conflict; the
alternative grounds below are treated as a vehicle risk rather than an assumed
bar, given the missing appendix; and the candidate explicitly declines to stack
overlapping penalties (waiver, counsel status, unpublished disposition, no
amici), which is the right discipline and the thing claude-baseline's otherwise
strong rationale lacks. The information-boundary paragraphs are a little
long for what they add, and the rationale could have said more plainly that
judicial immunity would likely dispose of most claims regardless of
Rooker-Feldman, a point claude-baseline made well. Those are the gap to a higher
score.

## Leakage

Mode `forward`; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The prediction was created
2026-09-16 against the same-day snapshot (last entry the June 17
distribution); the denial came on October 5, so the case was open and the cell
was not mis-provisioned. The captured log (coverage 0.906) shows the
provisioned inputs, prompt, schemas, and statpack pooling; three CourtListener
calls for the 2020 VanderKodde opinion, another case's authority; and three
web calls for the Court's Rules, all unobserved and therefore graded on their
queries, which name no case. No query reaches this petition's own docket or
disposition, no `retrieved_doc_date` is on or after resolution, and nothing
touches `data/qp-topics/`. The candidate's own retrieval note describes the
same calls and discloses that the web calls returned nothing usable.

## Big case

My independent read is 0.03 (see `evaluation.json`): a pro se custody-related
civil-rights suit against immune judicial officers, affirmed without opinion
and denied without comment. Nothing turns on it beyond the parties.
