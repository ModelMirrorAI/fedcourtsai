# Evaluation of claude-baseline — scotus/73281412, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in No. 25-1128, Alexander v. Philip R. Taft Psy D and Associates, was **denied on October 5, 2026** after the September 28 long conference, with no noted dissent from denial and no further relist (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.10 − 0)² = **0.0100**.
- `segment_base_rate` = **0.1722**, basis `risk_set`. The prediction froze `band: elevated` under `salience_version: sal-v4`, which matches the heading of the statpack's "Segment base rate by salience band (sal-v4)" table. I pooled the bracketed `reached` figure for `elevated` over the Term rows strictly before Term 2025 (2017–2024, weighted n = 2,810; 484.0 weighted grants). The pack renders all ten of its Terms (2017–2026), so this window coincides with the in-code ten-Term lookback and there is no window divergence to flag.
- `brier_skill_score` = 1 − 0.0100 / (0.1722)² = **0.663**. The candidate beat the band baseline comfortably; its 0.10 was the lowest and best-calibrated number of the three on a denial.

No `vote_accuracy`, `judgment_correct`, or `semantic_grades`: this is a cert cell, so none applies. `claim_scores` is the harness's.

## Reasoning quality: 0.85

What drove the grade:

- **Correct anchor, correctly discounted.** The candidate located the sal-v4 elevated reached rate (17.2% over 2017–2024), identified it as the yardstick, and then gave a sound reason to sit below it: the second distribution was a redistribution after a call for response, not a relist following conference consideration. That is exactly right on this docket (distributed May 5, response requested May 12, redistributed July 29), and the statpack caption itself warns the distribution count is an upper bound on relists.
- **Real engagement with the merits of the cert question.** It read the petition and both briefs in opposition and drew specific, checkable points from them: QP 1 rests on a reading of one sentence ("includes" not "limited to"), QP 2 is the Fifth Circuit's standard Bell shorthand, QP 3 is an application of plausibility pleading, the Taft dismissal on deliberate indifference is unchallenged, qualified immunity and Monell are unresolved below. These are the vehicle problems that make an error-correction petition unattractive, and they were borne out by a clean denial.
- **Honest about what it did not know.** It flagged that the snapshot payload dated July 29 might not show a reply brief. A reply was in fact filed September 18 (after its snapshot), so the caveat was warranted. It also said its CFR-conditioned grant intuition came from general knowledge, not a statpack cut.
- **Balanced upward adjustments** (CFR after waiver, published dissent, Taylor v. Riojas comparison) with a stated range (0.04 to 0.20) that bracketed the question sensibly.

What held it back from higher:

- The 0.10 still sits above where the cited downward factors point. The candidate itself said a routine pleading-stage disagreement would be nearer 0.04, and most of its own analysis described exactly that case. The upward factors were given a bit more weight than the record supported.
- One minor overstatement: "petitions that draw a call for response are granted at several times the paid-docket rate" is plausible but, as the candidate concedes, unsourced from the pack.

The forecast document (`predicted_reasoning.md`) was read for context only and is not scored here.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`; `retrieved_outcome_material` = false; `leakage_suspected` = false. The prediction was made September 17, 2026, eighteen days before the denial, so the case was genuinely open. The captured log (coverage 1.0) shows a CourtListener docket lookup for 25-1128 returning `date_terminated` null and zero docket entries, and an opinion search for the Fifth Circuit decision dated 2025-07-10. Nothing retrieved postdates the resolution, nothing names the disposing order, and no `data/qp-topics/` path was read. The case was not mis-provisioned forward.

## Big case

My independent read is 0.28 (see `big_case.notes`). The candidate's own stakes score was visible in the staged `prediction.json` when I formed mine; my read rests on the record described in the notes.
