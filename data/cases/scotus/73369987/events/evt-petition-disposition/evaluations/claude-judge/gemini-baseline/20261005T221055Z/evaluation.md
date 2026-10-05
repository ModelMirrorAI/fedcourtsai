# Evaluation of gemini-baseline — scotus/73369987, evt-petition-disposition

## Outcome and scores

The petition (No. 25-1296, Robinson v. Freeman) was distributed once, for the
September 28, 2026 long conference, and denied on October 5, 2026 with no
noted dissent and no response ever called for. Cert stage, `cert` on the event.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0512, `base_rate_basis` = `risk_set`. The prediction
  froze `band: baseline` with `salience_version: sal-v4`, matching the
  statpack segment table's heading, so the bracketed `reached` figures apply,
  pooled resolved-weighted over OT2017–OT2024 (n = 11,580; the table renders
  all 10 Terms the pack holds, so no window divergence): 0.0512.
- `brier_skill_score` = 1 − 0.000001 / 0.0512² ≈ 0.9996.

## Reasoning quality: 0.55

A one-paragraph rationale that gets the direction and the anchor right and
stops there. The "roughly 5%" baseline figure is the correct reached-band
anchor, and the "~1.2%" for zero relists is a real figure from the statpack's
relist cut (the `granted` share of the 0-relist bucket; the grant-family share
including GVRs is 1.7%). The downward adjustments named are real and
relevant: pro se petitioner, a state custody matter with no constitutional
conflict, no cited division of authority.

The analysis is thin where the record offered more. It does not engage the
vehicle at all: nothing on the state procedural ground (the C.R.C.P. 7(b)(1)
particularity ruling), the appellate court's undeveloped-argument alternative,
the unpublished decision below, the elder child aging out, or the petitioner's
two prior denied petitions from the same dispute, all of which are in the
petition the candidate read. One inference is slightly off: it reads the
absence of a call for a response as a signal the petition "is not viewed as a
serious candidate," but at a first distribution with no response on file the
call for a response, if any, typically follows the conference; the absence
before it carries little information. The number itself, 0.001, is defensible
on this record, though the document gives less reason for it than the other
two candidates give for theirs. The forecast document and the claims block
were read for context only and are not scored here.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`; the prediction was written on
September 17, 2026, before the September 28 conference and the October 5
denial. Every one of the 22 calls is `unobserved` (coverage 0.0, the engine's
standing shape), so each is graded on its query: reads of the prompt,
AGENTS.md, the provisioned context, snapshot, event, documents manifest and
petition, three greps of the committed statpack, then the output writes and a
validate run. No web, corpus, or CourtListener call, no query naming this
petition's disposition, nothing under `data/qp-topics/`. The candidate's own
retrieval note says no retrieval beyond the provisioned inputs; with
`flags.json` not staged, that note and the log are what the grade rests on,
and the log's query set is consistent with it. `retrieved_outcome_material` =
false, `influenced_prediction` = `not_applicable`, `leakage_suspected` =
false. The case was genuinely open when provisioned.

One record-keeping note, not a grading matter: the prediction's `created_at`
equals the run id's timestamp (21:46:06Z) while the log's first call is at
23:01Z, so the stamp was copied from the run id rather than taken at write
time. Recorded in this cell's `flags.json` as an info-level data-quality note.

## Big case: 0.05 (my independent read, formed before reading the candidate's)

A pro se challenge to Colorado's parenting-time factors, unpublished below, no
response, no amicus, denied without comment. The abstract question would be
large if ever decided; this vehicle decided nothing and drew no attention.
