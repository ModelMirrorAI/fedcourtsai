# Evaluation: gemini-baseline — scotus/73281630, evt-petition-disposition

## Cell

Cert-stage petition event (No. 25-1143, D.A. v. Tri County Area Schools), forward
mode. The petition was denied on 2026-10-05 after the September 28 long conference,
with no noted dissent from denial. The candidate predicted `denied` at P(grant) 0.25.

## Scores

- `correct` = 1: `denied` matches `actual_disposition`.
- `brier_score` = (0.25 − 0)² = 0.0625.
- `segment_base_rate` = 0.1722, basis `risk_set`. The prediction froze `band:
  elevated` under `salience_version: sal-v4`, Term 2025, and the statpack's segment
  table heading names sal-v4, so the bracketed *reached* figure applies. Pooled
  resolved-weighted over every rendered Term strictly before OT2025 (OT2017–OT2024,
  eight rows, n = 400, 347, 334, 397, 342, 300, 354, 336): 484 / 2,810 = 0.1722. The
  caption renders 10 of 10 Terms, so the rendered window is the pack's whole window
  and no lookback divergence needs flagging; the in-code ten-Term lookback reaches
  back to OT2015 but only OT2017 onward exists in the pack, so both pool the same
  eight Terms.
- `brier_skill_score` = 1 − 0.0625 / (0.1722)² = −1.11. The forecast was on the right
  side of 0.5 but, like every candidate on this cell, sat above the band baseline on a
  petition that was denied, so a naive forecaster parroting the 17.2% rate beat it.

## Reasoning quality: 0.55

What the rationale gets right: it names the correct anchor (about 17% for the
elevated risk set pooled over the prior Terms), it reads the two distributions
correctly as functionally one conference with full briefing rather than a relist,
and it identifies the two genuine attention signals in the record (the Court's call
for a response after the respondents waived, and four cert-stage amici). The
discount it applies, that long-conference petitions are mostly denied and the split
may read as fact-bound, is the right direction and is what happened.

What holds it down: the analysis is thin relative to what was provisioned. The log
shows it read the questions presented and the snapshot but not the petition or the
brief in opposition, and the rationale shows it. It takes the petition's framing of
the circuit split at face value and never engages the BIO's strongest points, which
the other candidates found decisive in the same direction: that only the en banc
Third Circuit has adopted the plainly-lewd framework, that the students admitted
understanding the slogan's vulgar meaning (undercutting the QP's premise), and the
qualified-immunity and graduation vehicle issues. It mentions Mahanoy as evidence the
Court takes student-speech cases, without noting that Mahanoy was the first such
merits case in fourteen years or the May 2025 denial in L.M. v. Middleborough, both
of which point the other way. The upward move from 17% to 25% rests on the CFR and
amici alone, with no attempt to weigh the countervailing record. Sound but shallow:
right conclusion, under-argued.

The forecast document and the claims block are not graded here; the harness scores
the claims in code.

## Leakage

Forward cell, so the default is `not_applicable`, and I checked it rather than
stamping it. The prediction was created 2026-09-16 from the 2026-09-15 snapshot and
the petition was not acted on until 2026-10-05, so no disposition existed to
retrieve. The captured log has 26 calls, all `unobserved` (coverage 0.0, the engine's
standing shape, so each call is graded on its query): reads of AGENTS.md, the
prompt, the provisioned record, the statpack, and schemas, plus one free-text corpus
query for student-speech precedent that the retrieval note says failed. No web
search, no MCP call, nothing naming this case past the snapshot, nothing under
`data/qp-topics/`. `retrieved_outcome_material` false, `influenced_prediction`
`not_applicable`, `leakage_suspected` false. The candidate's own `flags.json` is not
staged, so the absence of any disclosure there is not evidence either way; the
grade rests on the log and the reasoning.

## Big case

My independent read is 0.45 (see `evaluation.json`). A real doctrinal question for
every public-school student on a nationally recognizable slogan, with a divided
published opinion below and strong counsel on both sides, but incremental rather
than structural, and it ended in a quiet denial with no writing. Disclosure: the
predictor's `big_case_score` is in the staged `prediction.json` and was visible
before I recorded mine; I did not adjust toward it.
