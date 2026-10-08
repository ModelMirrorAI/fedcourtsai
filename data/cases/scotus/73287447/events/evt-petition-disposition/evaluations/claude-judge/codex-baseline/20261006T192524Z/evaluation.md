# Evaluation: codex-baseline — scotus/73287447, evt-petition-disposition

**Cell type:** cert stage (`event.yaml` stage `cert`, moment `distribution`), forward mode. Outcome: petition **denied** on 2026-10-05 (`actual_granted` = 0, no noted dissent from denial, `distribution_count` 2, no CVSG).

## Quantitative

| field | value |
| --- | --- |
| predicted_disposition / actual | `denied` / `denied` → `correct` = 1 |
| probability | 0.13 |
| brier_score | 0.0169 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | 0.4314 |

**Base rate.** The prediction's frozen `context` carries `band: elevated` **and** `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is headed `sal-v4`, so the `risk_set` basis applies. I pooled the bracketed `reached` figure for `elevated` over every rendered Term strictly before this case's Term (2025), i.e. OT2017–OT2024, resolved-weighted: 484.4 / 2810 ≈ 0.1724. The table renders 10 of 10 Terms, so the rendered window is the whole pack and there is no lookback divergence to flag. The baseline's Brier against a denial is 0.1724² ≈ 0.0297.

## Leakage

Forward cell. The prediction was written 2026-09-18 from the 2026-09-17 snapshot; the petition was then distributed for the 2026-09-28 conference and was not decided until 2026-10-05, so the case was genuinely open and ordinary retrieval could not leak an outcome that did not exist. Its log (40 calls, capture coverage 0.95) shows no lookup of this docket at all: the two uncaptured web searches queried the Ninth Circuit's City of Oakland opinion and the Tenth Circuit's Montreal Trading passage, and the four CourtListener calls fetched passages from those two pre-2022 opinions. The retrieval note states that no search sought this petition's disposition, and the log bears that out. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read, 0.35 (see `big_case.notes`): a real but narrow antitrust-standing question, interlocutory, no amici, denied silently.

## Reasoning quality: 0.85

**What it got right.** The anchor is computed correctly and reproducibly — 484 / 2,810 over the eight prior Terms, with the eight weighted denominators and numerators listed and the basis (risk-set, not terminal) named — and the document is explicit about its information boundary, including that the reply was not read and that the pack's vintage is a file-commit date rather than a corpus pull stamp. Its strongest move is going to primary sources on the split: it pulled the actual footnote in City of Oakland declining a bright-line non-purchaser rule and the Montreal Trading passage on prior dealings reducing speculation, and used them to test the BIO's characterization rather than take either side's word. That is exactly the check claude-baseline left to the briefs. The downward factors (fact-sensitive error correction rather than incompatible rules, interlocutory posture with contested factual questions, the two distributions overstating any relist signal) are the right ones and each is sourced to page ranges in the briefs or the snapshot. The upward factors are stated fairly, and the document is careful not to treat the DOJ's appellate participation as a CVSG or a current cert-stage view.

**Where it is weaker.** It did not retrieve the DOJ brief itself, so it did not reach claude-baseline's inference about what a CVSG would likely return; it notes this limit honestly. The document is long and spends some of its length on disclaimers (what the conditional claim numbers are not, the pack's freshness) that are correct but do not sharpen the forecast. The relist and CVSG terminal cuts are quoted but then, correctly, set aside as population shape rather than hazards. The final 0.13 is a judgmental step below the anchor and the document says so; the path the Court took (denial on the first full consideration, no writing) is consistent with it.

Both the claims block and `predicted_reasoning.md` are unscored here per the contract.
