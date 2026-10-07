# Evaluation — claude-baseline, Winnemucca Indian Colony v. United States (scotus/73281654, evt-petition-disposition)

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 2`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.04` → **brier_score = 0.0016**.
- **segment_base_rate = 0.1722** on the `risk_set` basis: the prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack table's heading, so the bracketed `reached` figures apply. Pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the whole pack): weighted grants 484.0 over n = 2810, giving 0.17224 from the statpack JSON's exact per-Term fields. Baseline Brier 0.02967.
- **brier_skill_score = 1 − 0.0016 / 0.02967 = 0.9461.**
- `vote_accuracy`, `judgment_correct`: not applicable on a cert cell. `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.86

The strongest analysis of the three, from `reasoning.md` only:

- **Anchor done correctly and then diagnosed.** The candidate pooled the elevated band's `reached` figures over the eight rendered prior Terms (17.2%, n = 2810 — matches the exact figure), and then made the decisive structural observation: the elevated band here is an artifact of a call-for-response redistribution, so the petition "has been considered at zero conferences" and the relist-1 population the anchor prices is not the population this petition belongs to. That is exactly right on this docket, and it is the reason a well-reasoned number sits far below the band rate.
- **Accurate on the record.** It correctly reports the decision below as published (156 F.4th 1339, confirmed by a CourtListener search showing status Published), correctly separates the CFC's three grounds from the Federal Circuit's single affirmance ground, and correctly notes that §1500 and §2501 were not reached on appeal — so a win on the Winters question "changes nothing." The brief in opposition supports every one of those statements.
- **Fair to both sides.** The up-adjustments (CFR after a waiver, a full 29-page BIO, tribal-trust doctrine as an area the Court revisits, the 5–4 split in Navajo Nation) are stated and weighed rather than ignored, and the candidate explains why the BIO's reliance on alternative grounds cuts toward denial rather than up.
- **Explicit about its own weakest link.** It says the CFR-class grant rate it used comes from general knowledge, not a committed cut, and bounds how wrong that could make the number. That is the right disclosure for the one step the statpack cannot support.

Where it loses points: the 0.22 further-distribution figure is on the high side for the reasoning the candidate itself gives (a petition at its first real conference, fully briefed, with a weak vehicle); the "small-firm petition, no amici" point is a heuristic asserted rather than tied to a statpack cut; and the Navajo Nation dissenter speculation edges toward a lineup the record cannot support, though it is confined to the conditional writing branch. The core analysis was sound and the denial bore it out.

## Leakage

Forward cell: `retrieval_log.json` records `mode: forward`, coverage 1.0. Captured external calls: two `fedcourts query` calls (a citation lookup for 599 U.S. 555 that returned nothing; an era/disposition query returning unrelated granted priors, `retrieved_doc_date` 2025-02-11); a CourtListener docket-header call for this docket (`retrieved_doc_date` 2026-04-13, the filing date — the candidate reports `date_terminated: null`, i.e. the petition pending); a docket-entries call returning no entries; and opinion searches that found the Federal Circuit decision below (2025-10-16). The docket-header call is a status check on this case, but its captured result predates the event and confirmed pendency rather than revealing an outcome. No `retrieved_doc_date` on or after 2026-10-05. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely pending when predicted (created 2026-09-18, denied 2026-10-05).

## Big case

My independent read is 0.18 — see `big_case.notes` in `evaluation.json`.
