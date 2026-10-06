# Evaluation — codex-baseline — scotus/73392441 evt-petition-disposition

## Cell

Cert-stage petition event (`stage: cert`, `moment: distribution`), forward mode. Outcome: certiorari **denied** on 2026-10-05 after a single distribution (for the September 28, 2026 conference), no CVSG, no noted dissent. `actual_granted = 0`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition: denied` == `actual_disposition: denied` |
| `brier_score` | 0.000064 | (0.008 − 0)² |
| `segment_base_rate` | 0.051209 | baseline band, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 (593 / 11,580) |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| `brier_skill_score` | 0.975595 | 1 − 0.000064 / 0.051209² |
| `reasoning_quality` | 0.88 | see below |

Base-rate detail: the prediction's frozen context carries both `band` and `salience_version`, and the committed `metrics/statpack.md` *Segment base rate by salience band (sal-v4)* heading matches, so the `risk_set` basis applies. The table caption renders 10 of 10 Terms, so the rendered window is the whole pack; the Terms strictly before the case's Term 2025 are OT2017–OT2024. The pooled rate from the unrounded `statpack.json` prefix fields is 593 / 11,580 = 0.051209, the same computation this candidate performed. No window divergence to flag.

`vote_accuracy` omitted (cert stage, never scored). `judgment_correct` null. No `semantic_grades` block: no semantic set is declared on a cert event and the prediction carries none.

## What the prediction got right

The disposition, the timing (early October order list), no further distribution, no CVSG, no separate writing. The highest probability of the three at 0.008, so marginally the weakest Brier, though all three are within a hair of one another.

## Reasoning quality — 0.88

The most rigorously sourced analysis of the three.

- **Information set stated precisely.** The document opens by saying exactly what was read, what was absent (no BIO, no appendix), what that absence does and does not prove, and that the outcome was not sought. It correctly notes that the event record at prediction time carried no explicit stage or moment; I confirmed that the committed `event.yaml` acquired its `stage` and `moment` fields only when the outcome was recorded, so this was an accurate reading of the record, not a misread.
- **Anchor computed exactly and read correctly.** 593 / 11,580 from the unrounded statpack fields over the right Terms, correctly identified as the risk-set figure rather than the terminal one, and correctly described as a starting point. The other statpack cuts are used only as shape checks and are correctly described as terminal and right-censored rather than as transition probabilities.
- **Legal analysis is sharp and verified.** The Seventh Amendment point is grounded in Bombolis, 241 U.S. 211, retrieved and read rather than recalled, which is the right authority. The Rule 10 point was checked against the Court's current rules. The observation that the action sought equitable relief, so a jury entitlement would be doubtful even in federal court, is a point the other candidates missed and is correct. The absence of a developed split is correctly distinguished from the petition's second Washington example of the same alleged practice.
- **Calibrated self-description.** The 0.8% is labeled a judgmental forecast, not a fitted rate; the limitations section names the one-sided record as the main uncertainty.

Deductions:

- A fair share of the document is tooling narrative (web-tool failures, PDF extraction attempts, uv cache settings, statpack commit vintage). None of it is wrong and the provenance discipline is welcome, but it dilutes a legal-analysis document.
- The probability is the highest of the three and the reasoning's own weight of evidence would support going lower; the "affirmative consideration" that keeps it at 0.8% (a clear procedural violation if the record showed one) is given more room than the petition's own characterization warrants, given that the candidate itself notes the premise is unverified.
- The 30% summary-route conditional is argued thinly, but that is a claims-block matter and does not enter this score.

## Leakage

`mode: forward`. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Forward cell; prediction created 2026-09-17, well before the 2026-10-05 denial. Coverage 0.88; the four unobserved rows are hosted web searches/opens whose queries target Supreme Court Rule 10 and the Seventh Amendment's reach, none naming this case. Captured calls: local reads of the record and statpack, CourtListener lookups of Bombolis (241 U.S. 211) and its 'state courts' passages, and a fetch of the Court's current rules PDF. One shell find names data/qp-topics/ only as a -not -path exclusion while locating AGENTS.md; it prints no qp-topics content and reveals no membership, so it is not a read of that tree. No outcome material surfaced. The candidate's `retrieval.md` is a faithful account of the captured log, including the failed tool attempts. The prediction predates the conference and the denial, so the forward routing was correct.

## Big-case read

My independent read, formed before reading the candidate's score: 0.05. Independent read formed before looking at the candidates' scores: a private deed-of-trust reformation dispute from an unpublished Washington Court of Appeals decision after discretionary state review was denied; the questions presented recast one summary judgment ruling as a Due Process and Seventh Amendment attack on summary judgment itself. No response was called for, one distribution, denied without noted dissent. Stakes for anyone beyond the parties are negligible. The candidate's 0.25 is the highest of the three; its rationale explicitly separates stakes from grant likelihood and credits the national reach a constitutional limit on summary judgment would have. I weigh that framing less, since the Court was never going to reach it through this vehicle, but the read is defensible.
