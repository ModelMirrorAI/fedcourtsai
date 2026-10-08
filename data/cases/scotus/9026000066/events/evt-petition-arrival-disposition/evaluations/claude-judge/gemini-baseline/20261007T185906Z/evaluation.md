# Evaluation — gemini-baseline — scotus/9026000066, evt-petition-arrival-disposition

**Cell.** Cert stage, arrival moment, forward mode. The petition (pro se, from an
unpublished Arizona Court of Appeals memorandum affirming a divorce decree) was
distributed once, for the September 28, 2026 conference, and **denied** on
October 5, 2026 with no noted dissent. `actual_granted` = 0.

**Scores.**

| field | value | note |
| --- | --- | --- |
| `correct` | 1 | predicted `denied`, outcome `denied` |
| `brier_score` | 0.000001 | (0.001 − 0)² |
| `segment_base_rate` | omitted | salience-version mismatch, below |
| `brier_skill_score` | omitted | follows the rate |
| `base_rate_basis` | null | same |
| `reasoning_quality` | 0.60 | |

**Why the base rate is omitted.** The prediction froze `context.band` =
`baseline` under `context.salience_version` = `sal-v3`. The committed
`metrics/statpack.md` renders exactly one "Segment base rate by salience band"
table and its heading names `sal-v4`; no `sal-v3` table is rendered. A band
name only means something under the version that assigned it, so the table is
no baseline for this candidate's band, and the contract's only answer is to
omit the rate, the skill, and the basis together rather than relabel the number
`terminal`. Recorded in this cell's `flags.json`. The same applies to all
three candidates, so the omission does not differentiate them.

**What the prediction got right.** Everything on the disposition axis: a
denial, with an aggressive probability (0.001) that the outcome rewards. The
rationale correctly identifies the features that make this petition
near-hopeless — a pro se petitioner, a state family-law dispute, fact-bound
questions dressed as procedural due process, no circuit split or federal
interest, and a state-procedural-ground problem (the waiver holding). It
anchors on the right population figure for an arrival cell (the baseline
band's bracketed `reached` rate, roughly 6.5% under the version then in force)
before adjusting.

**What drove `reasoning_quality` = 0.60.** The analysis is sound but thin.
It is a single paragraph that names the correct factors without working any
of them: no statement of the pooled window or `n` behind the anchor, no
engagement with the first question's "not strictly or regularly followed"
prong (the only doctrinal hook the petition has, via *Lee v. Kemna*), and no
account of what would have to be true for the adjustment from ~6.5% to 0.1% to
be right. One imprecision: it lists "harmless error" alongside waiver as an
adequate and independent state ground, but a harmlessness holding is a
merits-type ruling rather than a procedural bar, so only the waiver footnote
belongs under that heading. The number is defensible for a pro se paid
petition from a state court but sits below any rate the statpack supports for
a named segment, and the rationale does not say why. Against two candidates
that showed their work on the same conclusion, this earns a clearly positive
but middling grade.

**Leakage.** Mode `forward`; the event was unresolved when the cell ran
(2026-08-16, against a one-entry docket). The log's 21 calls are all
`unobserved` (coverage 0.0, the engine's standing shape) and every call is a
read of the provisioned inputs, a statpack grep, or an output write; no web,
MCP, or corpus query, and `retrieval.md` says none. Nothing surfaces this
petition's disposition. `influenced_prediction` = `not_applicable`,
`leakage_suspected` = false.

**Big case.** My independent read, formed before looking at the candidate's
score: 0.02. A private dissolution dispute with no reach beyond the parties.
The candidate's own 0.0 is in the same place.

**Not graded here.** The `claims` block and `predicted_reasoning.md` are
outside this evaluation; the harness scores the claims in code. No
`semantic_grades` block: a cert cell declares no semantic set.
