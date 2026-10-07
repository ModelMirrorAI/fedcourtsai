# Evaluation of claude-baseline — scotus/73281703, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied 2026-10-05 after the 2026-09-28 conference, `actual_granted` 0, no noted dissent, two distributions, no CVSG.

## Scores

| field | value |
| --- | --- |
| predicted_disposition | denied (matches) → `correct` 1 |
| probability | 0.18 → `brier_score` 0.0324 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | −0.090 |
| reasoning_quality | 0.80 |

**Base rate.** The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack table heading, so the basis is `risk_set`. Pooling the bracketed `reached` figure for `elevated` over Terms 2017–2024 (every rendered Term strictly before Term 2025; the caption says 10 of 10 pack Terms are rendered, so there is no window divergence) gives weighted n 2810 and rate 0.1724 — the figure the candidate itself used. At 0.18 the forecast sits a hair above the anchor, so its skill is slightly negative: it essentially parroted the band rate, which is an honest place to land when the up and down factors net out.

## What the prediction got right

The call (denied), the modal path (denial at or just after September 28, plain denial, no writing, no CVSG) and the reading of the docket (two distribution entries but zero conferences actually held, because the response request pulled the petition from the June list) were all right. The rationale is the most complete of the three on the facts that mattered. It names the largest downward factor precisely — the question presented asks about independent contractors suing "for discrimination," while the case is a retaliation claim by a non-disabled parent employed by a staffing agency, with an unsettled antecedent question (whether section 504 supplies a private retaliation action at all, which the opposition says the Sixth Circuit answered no in Smith) sitting underneath. It also weighs the absence of amici, the state-court origin and general verdict, and the Court's 2010 denial in Fleming on the down side, against a conceded and mature split, a final judgment, clinic counsel, and the Court's recent appetite for modest-stakes disability-statute coverage questions on the up side. The candidate read the reply brief (a legitimate forward retrieval of the case's own pre-decision filing) and used it to assess the vehicle argument, which neither other candidate did.

## Where the reasoning is weaker

The candidate's legal view that the opposition's "independent grounds" point is weak (because the alternative grounds attach to other claims against other defendants) is defensible but stated with more confidence than the materials support; the complication of an undifferentiated damages award is acknowledged a paragraph later. It takes the opposition's footnote about the Smith denial at face value after failing to confirm it on CourtListener, and says so. The relist probability (0.30) was on the high side for a petition that was then denied without relist, though the reasoning for it (relist-before-grant practice plus a margin for relists ending in denial) is coherent. These are small; the "where to discount me" section is candid and the anchor method is exactly the one the statpack caption asks for. `reasoning_quality` 0.80.

## Leakage

Forward cell; `influenced_prediction` is `not_applicable`, `retrieved_outcome_material` false, `leakage_suspected` false. Prediction created 2026-09-18, before the conference and the denial. All 28 logged calls are captured. Beyond the provisioned record: one `fedcourts query` for recently granted SCOTUS priors (`retrieved_doc_date` 2026-09-10, other cases, used for relist shape); a web-fetch of this petition's own reply brief, docketed 2026-08-18, which predates the resolution and reveals nothing about it; a CourtListener docket search for a different case (No. 25-1028, Smith) and a `docket-entries` call on this docket id that returned no rows per the candidate's retrieval note (SCOTUS dockets carry no entries there). That last call does name this case, but the outcome did not exist on 2026-09-18 and nothing post-resolution could have come back. A closing shell call filtered `data/qp-topics` lines out of `git status` output; that is a text filter on a status listing, not a read of that path, and I do not treat it as one.

## Big case

My independent read, formed before looking at the candidate's score: 0.30 — a real inter-court division on section 504's reach to non-employees, but a weak vehicle and a plain denial. The candidate's 0.25 is recorded in its prediction; I supply only my read.

## Harness fields

`claim_scores`, `process_version`, `base_rate_salience_version`, and `prediction_run_id` are left to the harness. `vote_accuracy` and `judgment_correct` are omitted/null on this cert cell. No `semantic_grades` block: a cert event declares no semantic set.
