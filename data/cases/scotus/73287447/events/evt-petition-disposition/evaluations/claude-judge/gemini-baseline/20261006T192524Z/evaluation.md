# Evaluation: gemini-baseline — scotus/73287447, evt-petition-disposition

**Cell type:** cert stage (`event.yaml` stage `cert`, moment `distribution`), forward mode. Outcome: petition **denied** on 2026-10-05 (`actual_granted` = 0, no noted dissent from denial, `distribution_count` 2, no CVSG).

## Quantitative

| field | value |
| --- | --- |
| predicted_disposition / actual | `denied` / `denied` → `correct` = 1 |
| probability | 0.35 |
| brier_score | 0.1225 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | -3.1216 |

**Base rate.** The prediction's frozen `context` carries `band: elevated` **and** `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" table is headed `sal-v4`, so the `risk_set` basis applies. I pooled the bracketed `reached` figure for `elevated` over every rendered Term strictly before this case's Term (2025), i.e. OT2017–OT2024, resolved-weighted: 484.4 / 2810 ≈ 0.1724. The table renders 10 of 10 Terms, so the rendered window is the whole pack and there is no lookback divergence to flag. The baseline's Brier against a denial is 0.1724² ≈ 0.0297.

## Leakage

Forward cell. The prediction was written 2026-09-18 from the 2026-09-17 snapshot; the petition was then distributed for the 2026-09-28 conference and was not decided until 2026-10-05, so the case was genuinely open and ordinary retrieval could not leak an outcome that did not exist. Its log (31 calls) has capture coverage 0.0 — every marker-carrying call is `unobserved`, which is an engine's standing shape and not a defect — so each call is graded on its query. The two external calls were a CourtListener search for the Second Circuit opinion by caption and a text search for "standing" within that opinion (decided December 2025, before the petition). No query sought this petition's disposition or anything dated after the prediction. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read, 0.35 (see `big_case.notes`): a real but narrow antitrust-standing question, interlocutory, no amici, denied silently.

## Reasoning quality: 0.35

**What it got right.** The anchor is correctly located: it names the sal-v4 `elevated` band and quotes the bracketed reached figure for OT2024 (17.9%) with a note that pooling historically runs slightly lower, which is the right table and the right figure. It correctly identifies the response request after a waiver as a signal of interest, and the Second Circuit dissent as a factor. It retrieved the opinion below and checked the split language in it.

**Where it falls short.** The document then doubles the anchor to 0.35 on the strength of "a clean, well-developed circuit split" without testing that characterization against the brief in opposition. The retrieval log shows no read of `petition.txt` or `brief-in-opposition.txt` — only the QP, the snapshot, and the documents manifest — so the petition's framing of the split is taken as given, and the BIO's central answer (both comparator circuits disclaimed a categorical rule and named a prior course of dealing as the distinguishing fact) is never engaged. The interlocutory posture, which the BIO leads with and which is the most common reason a split-presenting petition is denied, is not mentioned. "Elite Supreme Court practitioners" and "major corporate entities" are weak cert signals and are given weight here. The response request is counted as a reason to go above the band even though the band already encodes it. The single stated uncertainty (percolation) is the right one but is not resolved or weighed. The rationale is roughly 200 words with no reasoning offered for the four non-headline claim numbers, and `big_case_rationale` is null in the JSON with the 0.70 stakes read justified by one sentence. Given the outcome — denial on first full consideration, no relist, no writing — a 0.35 number that rested on an unexamined "clean split" reads as anchored to the petition rather than to the record. The score reflects the thinness of the analysis more than the miss: the same gaps would have been present had the petition been granted.

Both the claims block and `predicted_reasoning.md` are unscored here per the contract.
