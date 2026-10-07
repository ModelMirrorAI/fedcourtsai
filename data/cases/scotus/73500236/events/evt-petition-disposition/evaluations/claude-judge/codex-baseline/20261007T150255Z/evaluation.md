# Evaluation of codex-baseline — scotus/73500236, evt-petition-disposition

## Outcome and scoring

Cert-stage forward cell. The petition in *Colorado Bondshares v. Marin Metropolitan District* (No. 25-1334) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.02 → **brier_score = 0.0004**.
- Base rate: the prediction froze `band: baseline` under `salience_version: sal-v4`, and the committed statpack's "Segment base rate by salience band" table carries the same version heading, so the basis is **`risk_set`**. Pooling the bracketed `reached` figure for `baseline`, resolved-weighted over the rendered Terms strictly before the case's Term 2025 (2017–2024, the full window the pack holds — the caption shows 10 of 10 Terms), gives **segment_base_rate = 0.0512** (593 grant-equivalents over n = 11,580). The pipeline pooler (`prediction_base_rate`, lookback 10) returns the same figure, so there is no rendered-vs-in-code window divergence to flag.
- **brier_skill_score = 0.847** against the always-5.12% baseline.

## Reasoning quality: 0.85

What drove the score:

- **Anchor exactly right.** The candidate identified the sal-v4 `baseline` bracketed `reached` rate, pooled Terms 2017–2024 from the statpack JSON, and reported 5.1209% — identical to the in-code number. It explicitly declined the terminal rate and the respondent's caption class, which is the correct reading of the table's note.
- **Sound, sourced adjustments.** First-impression framing rather than a split; unpublished non-precedential Colorado Court of Appeals decision; a messy vehicle (prior recharacterization litigation, parcel sale, purchaser knowledge); both respondents waived with no call for a response. Each is tied to a petition page or the snapshot, and each is a real Rule 10 negative. The candidate correctly treated the waivers as a modest signal rather than proof, and kept a floor for the ~$30M stake and the restitution question.
- **Epistemic discipline.** It flagged that its account of the decision below comes from the petition's advocacy, that no BIO exists, that the snapshot is a vintage and not a live docket, and it stated the statpack's commit vintage rather than claiming corpus freshness. The Palazzolo check was a proportionate doctrinal probe and was explicitly confined to analogy.
- **Weaknesses.** The adjustment from 5.1% to 2% is reasonable but under-argued relative to the depth elsewhere; the independent-state-ground problem the petition itself discloses (the Colorado court grounding its holding in state due-process doctrine) is mentioned only glancingly as "vehicle complexity" when it is the single strongest reason this petition could not be granted as framed. The 12% relist figure is defended only loosely. Some of the document is procedural narration rather than analysis.

The forecast document and the claims block were read for context only and are not scored here.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The prediction was created 2026-09-17 and the denial came 2026-10-05, so the case was genuinely open. The log carries no `retrieved_doc_date` on or after resolution, no query naming this docket or caption, and no `data/qp-topics/` read. The three web calls are `unobserved` and were graded on their queries (Rule 10 guidance and Palazzolo), neither about this petition. The candidate's `flags.json` is not staged, so its own disclosures reached me only through `reasoning.md` and `retrieval.md`; both say it did not seek the disposition, and the log is consistent with that.

## Big case

My independent read is 0.12: a private municipal-bond dispute turning on an unpublished Colorado decision, denied without comment at the first conference. The candidate's 0.40 is higher than mine; the predictor's score is graded by rank-agreement at leaderboard time, not here.
