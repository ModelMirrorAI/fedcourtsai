# Evaluation: codex-baseline — scotus/73281630, evt-petition-disposition

## Cell

Cert-stage petition event (No. 25-1143, D.A. v. Tri County Area Schools), forward
mode. The petition was denied on 2026-10-05 after the September 28 long conference,
with no noted dissent from denial. The candidate predicted `denied` at P(grant) 0.32.

## Scores

- `correct` = 1: `denied` matches `actual_disposition`.
- `brier_score` = (0.32 − 0)² = 0.1024.
- `segment_base_rate` = 0.1722, basis `risk_set`. The prediction froze `band:
  elevated` under `salience_version: sal-v4`, Term 2025, and the statpack's segment
  table heading names sal-v4, so the bracketed *reached* figure applies. Pooled
  resolved-weighted over every rendered Term strictly before OT2025 (OT2017–OT2024,
  eight rows, n = 400, 347, 334, 397, 342, 300, 354, 336): 484 / 2,810 = 0.1722. The
  caption renders 10 of 10 Terms, so the rendered window is the pack's whole window
  and no lookback divergence needs flagging; the in-code ten-Term lookback reaches
  back to OT2015 but only OT2017 onward exists in the pack, so both pool the same
  eight Terms. The candidate computed this same figure itself from statpack.json.
- `brier_skill_score` = 1 − 0.1024 / (0.1722)² = −2.45. Highest probability of the
  three on a petition that was denied, so the furthest below the band baseline.

## Reasoning quality: 0.70

This is a careful, well-sourced rationale. It computes the correct risk-set anchor
to four digits and says why the terminal figure does not apply. It read the petition
and the brief in opposition with page citations and gives both sides their due: the
split section correctly notes the BIO's distinction between a methodological
disagreement and a demonstrated conflict in outcomes, the B.H. distinction
(ambiguous awareness bracelet versus a slogan the students admittedly understood as
profane), and the weakness of the Ninth Circuit Chandler citation. It handles the
qualified-immunity point exactly right, as a vehicle discount rather than a bar,
because injunctive relief against the district keeps the question live. It reads the
two distributions as administrative redistribution after the response rather than a
relist signal. It is honest about what it did not read (the reply, the amici, the
appendix) and about its external lookups failing.

Why not higher: the number does not follow from the analysis. The rationale's own
weighing lists one paragraph of upward factors (CFR, four amici, a divided published
opinion) against three of downward ones (thin split, contested premise, vehicle
problems, the distribution count overstating attention), and then nearly doubles the
anchor to 32%, the largest move of the three candidates. The denial was the outcome
its own reasoning best supported. It also misses the most informative recent signal,
the Court's May 2025 denial in L.M. v. Middleborough over a two-Justice dissent,
which another candidate found and used. Sound analysis, under-disciplined
translation into a probability.

The forecast document and the claims block are not graded here; the harness scores
the claims in code.

## Leakage

Forward cell, so the default is `not_applicable`, and I checked it rather than
stamping it. The prediction was created 2026-09-16 from the 2026-09-15 snapshot and
the petition was not acted on until 2026-10-05, so no disposition existed to
retrieve. The captured log has 31 calls with coverage 0.90: local reads of the
record, petition, BIO, statpack and schemas; three web-search rows (`unobserved`, so
graded on their queries) all aimed at Bethel v. Fraser, 478 U.S. 675, a 1986
precedent; and one CourtListener citation search for 725 F.3d 293 (B.H. v. Easton,
2013), captured, which returned HTTP 429 and no content. No query names this case's
caption or docket, nothing under `data/qp-topics/`. The reasoning and retrieval note
disclose the attempts and state no outcome material was encountered, and nothing in
the rationale presupposes the result. `retrieved_outcome_material` false,
`influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My independent read is 0.45 (see `evaluation.json`). A real doctrinal question for
every public-school student on a nationally recognizable slogan, with a divided
published opinion below and strong counsel on both sides, but incremental rather
than structural, and it ended in a quiet denial with no writing. Disclosure: the
predictor's `big_case_score` is in the staged `prediction.json` and was visible
before I recorded mine; I did not adjust toward it.
