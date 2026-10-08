# Evaluation of gemini-baseline — scotus/73500236, evt-petition-disposition

## Outcome and scoring

Cert-stage forward cell. The petition in *Colorado Bondshares v. Marin Metropolitan District* (No. 25-1334) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.015 → **brier_score = 0.000225**.
- Base rate: the prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the basis is **`risk_set`**. Pooling the bracketed `reached` figure for `baseline`, resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms), gives **segment_base_rate = 0.0512** (n = 11,580). The pipeline pooler returns the same figure, so no window divergence.
- **brier_skill_score = 0.914** against the always-5.12% baseline.

## Reasoning quality: 0.50

The number landed well, but the document behind it is thin and its anchor is mis-pooled.

- **Anchor handled wrongly.** The candidate pooled the `baseline` bracketed rate over "2021–2025" and reported "around 5.5%". Two problems: the window includes Term 2025, which is this case's own Term (the prompt's rule is strictly-prior Terms, and the table's own note says the case's Term row already contains the case), and it ignores the rendered Terms 2017–2020 without saying why. The correct pool is 2017–2024 at 5.1%. In a forward cell including the own Term is a method error rather than leakage, and the resulting number is close, but it shows the base-rate rule was not read carefully.
- **One real argument, overstated.** The core of the rationale is the respondents' waivers: "The Supreme Court rarely grants certiorari without first requesting a response." That is accurate as Court practice and is a legitimate negative signal, but the candidate treats it almost as the whole case. The waiver plus a single distribution is the posture of thousands of denied paid petitions; it does not by itself distinguish this one.
- **The strongest legal point is missed.** The petition quotes the Colorado court grounding its holding in Colorado due-process jurisprudence. The candidate gestures at this ("decided on state-law grounds with a Due Process gloss") but does not name the adequate-and-independent-state-ground problem, does not note that the decision below is unpublished, does not discuss question 2's thin federal basis, and offers no vehicle analysis. It asserts "no indication of a circuit split" without engaging the petition's own "first impression" framing, which is what actually tells you there is no split.
- **No sourcing or limits.** No page cites, no statement that the account of the decision below is the petitioner's advocacy, no acknowledgment that no BIO exists. The relist claim (5%) is justified only as petitions that "might catch a clerk's eye", and the summary-route claim is not discussed in `reasoning.md` at all.

The disposition call and the direction of every adjustment were right, and the probability is defensible, which keeps this at the midpoint rather than below it. The forecast document and the claims block were read for context only and are not scored here.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Created 2026-09-17, denied 2026-10-05: the case was open. Every one of the 27 calls carries an `unobserved` marker (`result_capture_coverage` 0.0), which is this engine's standing shape and not a defect, so each call was graded on its query. All queries are reads of the provisioned record, prompts, schemas and statpack, plus writes of the candidate's own outputs. No web, corpus or CourtListener call; no `data/qp-topics/` read. `retrieval.md` ("No retrieval beyond the provisioned inputs") is consistent with the log. The candidate's `flags.json` is not staged, so the `none`-equivalent judgment rests on the log and reasoning, not on the absence of a disclosure.

## Big case

My independent read is 0.12: a private municipal-bond dispute on an unpublished Colorado decision, denied without comment at the first conference. The candidate's 0.10 is close; the agreement is graded at leaderboard time, not here.
