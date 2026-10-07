# Evaluation: claude-baseline — scotus/73303792, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), forward
mode. Outcome: petition **denied** on 2026-10-05 at its first and only
distribution (conference of 2026-09-28), no separate writing, no CVSG.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `denied` vs `denied`, exact label match |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | 0.05121 | baseline band, sal-v4, risk-set pool (below) |
| `base_rate_basis` | `risk_set` | frozen `context.band` + `context.salience_version` both present |
| `brier_skill_score` | 0.9905 | 1 − 0.000025 / (0.05121 − 0)² |
| `reasoning_quality` | 0.86 | below |

**Base rate.** The prediction's frozen context carries `band: baseline` and
`salience_version: sal-v4`; the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the bracketed `reached` figures are the right
population. Pooling resolved-weighted over every rendered Term strictly before
Term 2025 (OT2017–OT2024, eight rows) gives 593 / 11,580 = 0.05121, reproduced
from `statpack.json`'s `prefix_est_grant_rate` × `prefix_weighted_resolved`.
The table renders 10 of 10 Terms, so the rendered window is the pack's whole
window and the shipped ten-Term lookback (2015 ≤ T < 2025) excludes nothing
the pack holds; no window divergence to flag. The candidate anchored on this
same figure (it quotes "about 5.1%").

## What the prediction got right and wrong

Right on every count the cell scores: denial, at a probability far enough below
the band rate to earn nearly all the available skill. The outcome was a clean
first-conference denial with no writing, which is also what the candidate's
`reasoning.md` argued was the most likely shape (the forecast document itself
is not scored here).

## Reasoning quality (0.86)

The rationale is well-built. It names what it read, takes the right anchor
from the right table and pools it correctly, and then lists six case-specific
discounts in the order they matter: pro se paid filing; response waived and
never requested after a summer on the distribution list; nonprecedential
affirmance adopting the district court; judicial immunity as an independent
and unchallenged ground that makes the Rooker-Feldman question
non-outcome-determinative; a serial-litigant posture with a prior cert denial
on the same dispute; and thin, high-generality splits. Each of these is a real
and recognised cert-stage signal, and the immunity point in particular shows
the candidate read the petition rather than its caption. It is honest about
limits: OCR noise, the missing appendix, and two failed CourtListener searches
for the order below, each reported rather than glossed.

What keeps it short of the top: the pro se "order of magnitude" discount and
the waiver discount are asserted from general knowledge rather than tied to
anything in the pack or the record, and the candidate stacks all six discounts
without saying how much they overlap (pro se, waiver, unpublished order, and
no amici are largely one signal about the petition's weight, not four). The
landing point of 0.005 is defensible, but the path from 5.1% to 0.5% is stated
as a conclusion rather than reasoned as a reduction.

## Leakage

Mode `forward`; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The prediction was created
2026-09-16 against a same-day snapshot whose last entry was the June 17
distribution; the denial came on October 5, so the case was genuinely open and
the cell was not mis-provisioned. The captured log (coverage 1.0) shows the
provisioned inputs, the statpack, one corpus `query` for recent denied SCOTUS
rows unrelated to this case, and two CourtListener searches for the Sixth
Circuit order below (both empty). Nothing reaches this petition's own docket or
disposition and nothing touches `data/qp-topics/`.

One observation, recorded in `flags.json` as information and not as leakage:
one shell call globs a prior run's predictions directory under another case
and reads that cell's `prediction.json`, `tooling.json`, and `retrieval.md`,
evidently as a format template. That is another cell's output from an earlier
run, not outcome material about this case, and it does not bear on this grade.

## Big case

My independent read is 0.03 (see `evaluation.json`): the dispute is a pro se
custody-related civil-rights suit against immune judicial officers, affirmed
without opinion, denied without comment. Nothing turns on it beyond the
parties.
