# Evaluation: claude-baseline — scotus/73281630, evt-petition-disposition

## Cell

Cert-stage petition event (No. 25-1143, D.A. v. Tri County Area Schools), forward
mode. The petition was denied on 2026-10-05 after the September 28 long conference,
with no noted dissent from denial. The candidate predicted `denied` at P(grant) 0.20.

## Scores

- `correct` = 1: `denied` matches `actual_disposition`.
- `brier_score` = (0.20 − 0)² = 0.04.
- `segment_base_rate` = 0.1722, basis `risk_set`. The prediction froze `band:
  elevated` under `salience_version: sal-v4`, Term 2025, and the statpack's segment
  table heading names sal-v4, so the bracketed *reached* figure applies. Pooled
  resolved-weighted over every rendered Term strictly before OT2025 (OT2017–OT2024,
  eight rows, n = 400, 347, 334, 397, 342, 300, 354, 336): 484 / 2,810 = 0.1722. The
  caption renders 10 of 10 Terms, so the rendered window is the pack's whole window
  and no lookback divergence needs flagging; the in-code ten-Term lookback reaches
  back to OT2015 but only OT2017 onward exists in the pack, so both pool the same
  eight Terms. The candidate pooled the same eight rows and quoted the same figure.
- `brier_skill_score` = 1 − 0.04 / (0.1722)² = −0.35. Closest of the three to the
  baseline, still below it: a few points above the band rate on a denied petition.

## Reasoning quality: 0.82

The strongest rationale on this cell. It anchors correctly and, unusually, says what
the salience scorer's lattice already prices (relist count, CVSG, circuit, caption
class) so that its adjustments are confined to features the band does not carry: the
call for a response after waiver and the four repeat-player amici. It read the
petition and the brief in opposition in full. Its discounts are concrete and each one
is borne out by the record or by what happened: the two distributions mean the Court
had not yet voted once; the split is effectively one circuit on the framing question
once Chandler is read as a pleading-stage aside; the students' admission that they
understood the slogan's meaning makes the QP's "not plainly profane" premise
contestable; the older student has likely graduated and the damages claims face
qualified immunity, a discount not a bar because the injunctive claim keeps the
younger student's case live; and the Court's May 2025 denial in L.M. v. Middleborough
over an Alito–Thomas dissent is a directly comparable revealed preference that
predates the snapshot. That last point is the single most informative piece of
analysis any candidate produced, and it was found by a web search the candidate
disclosed. The uncertainties section is candid about over-reading the CFR and about
the corpus topic query returning nothing.

Why not higher: the landing point still sat above the anchor on a petition that
drew no vote to grant and no writing, so the upward factors were over-weighted
somewhat, though less than either peer. A few characterizations rest on general
knowledge rather than the record ("the current Court's speech docket has been
receptive," the Justices "most likely to be interested"), stated with more
confidence than they can bear. These are small faults in an otherwise disciplined
rationale.

The forecast document and the claims block are not graded here; the harness scores
the claims in code.

## Leakage

Forward cell, so the default is `not_applicable`, and I checked it rather than
stamping it. The prediction was created 2026-09-16 from the 2026-09-15 snapshot and
the petition was not acted on until 2026-10-05, so no disposition existed to
retrieve. The captured log has 22 calls, all captured (coverage 1.0): local reads of
the record, petition, BIO, statpack and docs/salience.md; two `fedcourts query`
calls (a topic filter that returned nothing, and a list of recent grants with
`retrieved_doc_date` 2026-09-10, not this case); and two web searches. One targeted
L.M. v. Middleborough (decided May 2025), legitimate pre-snapshot signal. The other
searched this case's own caption and docket number, 25-1143. That is the ordinary
forward shape rather than a breach: the petition was undecided on 2026-09-16, the
disclosed results (FIRE's case page, amicus commentary, the CA6 opinion and amicus
PDFs) all predate the snapshot, and the candidate reported that nothing about a
disposition appeared, which is what the timeline requires. The candidate disclosed
both searches in `retrieval.md` and `reasoning.md`, a point for the cell's
integrity. Nothing under `data/qp-topics/` (the one `file-read` of an engine
tool-results path is its own persisted shell output). `retrieved_outcome_material`
false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My independent read is 0.45 (see `evaluation.json`). A real doctrinal question for
every public-school student on a nationally recognizable slogan, with a divided
published opinion below and strong counsel on both sides, but incremental rather
than structural, and it ended in a quiet denial with no writing. Disclosure: the
predictor's `big_case_score` is in the staged `prediction.json` and was visible
before I recorded mine; I did not adjust toward it.
