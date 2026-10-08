# Evaluation of claude-baseline — scotus/73500236, evt-petition-disposition

## Outcome and scoring

Cert-stage forward cell. The petition in *Colorado Bondshares v. Marin Metropolitan District* (No. 25-1334) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent (`actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.012 → **brier_score = 0.000144**.
- Base rate: the prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the basis is **`risk_set`**. Pooling the bracketed `reached` figure for `baseline`, resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the pack's), gives **segment_base_rate = 0.0512** (n = 11,580). The pipeline pooler returns the same figure, so no window divergence.
- **brier_skill_score = 0.945** against the always-5.12% baseline.

## Reasoning quality: 0.90

The strongest of the three analyses.

- **Anchor right, and read correctly.** The candidate matched the band to the table's version, pooled the bracketed figure over 2017–2024 by `n`, and reported about 5.1% over roughly 11,600 — the in-code figure. It also explained what the risk-set denominator means (everyone who passed through `baseline`), which shows it understood the pairing rather than copying a number.
- **The decisive legal point is named.** The petition itself quotes the Colorado court resting on Colorado due-process jurisprudence (Bloom v. City of Fort Collins); the candidate identified this as an adequate-and-independent-state-ground problem and explained why the Court rarely looks past a state court's own characterization at the cert stage. It also correctly observed that question 2's federal authorities are 1870s–80s federal common-law decisions that do not bind a state court, so the federal question there is thin. This is exactly the analysis a careful cert-pool memo would lead with, and it is the reason a denial here was very nearly certain regardless of the stakes.
- **Posture read accurately.** Unpublished decision under C.A.R. 35(e), state supreme court denied review, both respondents waived, no amici despite the petition's claim of nationwide financing consequences, fact-bound Penn Central posture. The relist, CVSG, summary-route and dissent claims each got a short, coherent argument; the summary-route reasoning (no intervening decision to GVR against) is right.
- **Honest about limits.** It said the account of the decision below is the petition's adversarial characterization, that no BIO exists, and that corpus retrieval added nothing case-specific. It stated the one scenario (a call for response at the Long Conference) that would move it and by how much.
- **Weaknesses.** The counsel-of-record signal is weak and only lightly hedged. The "I would be surprised by anything above 0.03" statement sits oddly beside a 0.85 `confidence` field without explanation. A shape figure ("Term-2025 est. grant rate 2.6%") is quoted from the pack without saying which cut it came from. None of these affects the core analysis.

The forecast document and the claims block were read for context only and are not scored here.

## Leakage

`mode: forward`, `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Created 2026-09-17, denied 2026-10-05: the case was open. All 21 calls captured. The two CourtListener searches were for the caption (returning the 2014–2018 Landmark Towers decisions, newest doc date 2018-05-31) and for docket 25-1334 (no results, as the SCOTUS docket is not in RECAP). The newest `retrieved_doc_date` anywhere in the log is 2025-02-11, before the petition was filed. No `data/qp-topics/` read. Querying the case's own docket is ordinary forward retrieval on an open case, and it returned nothing anyway. The candidate's `flags.json` is not staged; `retrieval.md` is consistent with the log.

## Big case

My independent read is 0.12: a private municipal-bond dispute on an unpublished Colorado decision, denied without comment at the first conference. The candidate's 0.15 is close; the agreement is graded at leaderboard time, not here.
