# Evaluation of codex-baseline — Redding v. Mullin, No. 25-1336 (evt-petition-disposition)

**Stage: cert.** Outcome: petition **denied** on 2026-10-05 after one distribution
(long conference of 9/28/2026), no CVSG, no noted dissent. The candidate
predicted `denied` at P(grant) = 0.015, so `correct` = 1 and Brier = 0.000225.

## Base rate and skill

The prediction froze `band: baseline` with `salience_version: sal-v4`, matching
the statpack's sal-v4 band table heading, so the basis is `risk_set`. Pooling
the bracketed `reached` figure for `baseline`, resolved-weighted, over OT2017
through OT2024 (every rendered Term strictly before Term 2025; the caption shows
10 of 10 Terms, so no lookback divergence) gives 0.0512 on n = 11,580. Brier
skill score = 1 − 0.000225 / 0.0512² ≈ 0.914. The candidate pooled the same
window from the statpack's JSON twin and reported 593 / 11,580 = 5.12%, which
agrees with the rendered table to rounding.

## Reasoning quality: 0.80

A careful, well-bounded rationale. It states its information boundary
explicitly (the September 17 snapshot, no refreshed docket, no outcome sought),
anchors on the right figure and the right window, and its substantive moves
are sound:

- It reads the Fourth Circuit opinion correctly for its two grounds and for
  the express good-faith finding, and draws the right vehicle inference.
- It checked Strife v. Aldine and A.J.T. v. Osseo through CourtListener and
  distinguished both accurately: Strife concerned an unjustified delay with
  qualification undisputed, and A.J.T. expressly declined the broader
  liability-standard question and predates the decision below, so it is no
  GVR hook.
- It correctly separates a request for a response from the represented
  federal respondent from a CVSG.

It is slightly less decisive than it could be on the SG waiver, which it calls
"modest negative evidence, not dispositive"; on a paid petition with no call
for a response, that undersells the strongest signal on the docket, though the
final number still lands in the right place. The prose is abstract in places
and some sentences hedge where the record supports a firmer statement. I do
not score the claims block or the forecast document.

## Leakage

Mode `forward`; prediction created 2026-09-17, resolution 2026-10-05. The log
(31 calls, capture coverage 0.94) carries two `unobserved` web-search rows,
graded on their queries, which target the A.J.T. opinion and its PDF on the
Court's site, both 2025 material; and four CourtListener lookups of Strife and
A.J.T., captured. No query names this petition's disposition, and the
candidate's retrieval.md discloses the same. `retrieved_outcome_material` =
false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.10: an individual federal-employment accommodation dispute
dismissed on the pleadings, no joined split, SG waiver, one-pass denial
without writing. The predictor's score was visible in its prediction.json
before I wrote mine, so my read rests on the record and outcome rather than
being formed in isolation; I note that for the panel.
