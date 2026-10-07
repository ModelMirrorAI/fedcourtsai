# Evaluation of claude-baseline — Patterson v. Michigan, No. 25-1263 (evt-petition-disposition)

**Stage:** cert (event.yaml `stage: cert`, `moment: distribution`). **Outcome:** petition denied on 2026-10-05 after a single distribution for the 2026-09-28 conference; no CVSG, no noted dissent. **Mode:** forward.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` denied = `actual_disposition` denied |
| brier_score | 0.000036 | (0.006 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, risk-set |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| brier_skill_score | 0.9863 | 1 − 0.000036 / 0.0512² |
| reasoning_quality | 0.86 | see below |

The base rate pools the bracketed `reached` baseline figures over the rendered Terms strictly before Term 2025 (2017–2024; the table renders every Term the pack holds, so no window divergence): 593 / 11,580 = 0.05121, recorded as 0.0512. `vote_accuracy` is omitted on a cert cell.

## What the prediction got right

Right disposition with a confidently low number. The anchor is chosen and pooled correctly (about 5.1%, n ≈ 11,580, over 2017–2024, with the sal-v4 version match stated), and the cross-checks from the same pack are labelled as cross-checks rather than substituted for the anchor. The five adjustments are the right ones and are stated tightly: interlocutory posture under § 1257 with no Cox exception argued; fact-bound questions and no reasoned decision below to review; no asserted split and a legislative-style ask; weak advocacy signals including the absent response; a single distribution to the long conference. Each is accurate against the petition and snapshot. The rationale also noticed the Feb 06 2026 docket-entry date against a petition signed May 2 and docketed May 7, and resolved it plausibly as a retained deficient-filing date, which is careful reading of the record. The CourtListener check that the docket was unterminated is the correct forward-mode hygiene and is disclosed.

## Where it is weaker

"This alone is close to dispositive" on the interlocutory point is stated a shade more strongly than the doctrine supports, though the next clause (none of the Cox exceptions is argued) earns most of it. The originating-court cross-check cites the Court of Appeals of Michigan bucket (zero grants in 89), while the snapshot lists the Jackson County Circuit Court as the lower court, so the bucket this case actually falls in is uncertain; the rationale treats it only as corroboration, so no harm follows. The `confidence: 0.9` field is unexplained in the rationale. The reasoning is marginally less verified than codex-baseline's (which read the Cox text) but more economical and reads the record at least as closely, so the two sit close together.

## Leakage

Forward cell. All 21 calls captured. One corpus query for 2020s granted rows returned unrelated priors, disclosed as unused. Two CourtListener calls on this docket returned `date_filed` 2026-05-07, `date_terminated` null, last modified 2026-06-24 (the distribution) and zero entry rows: a pending-status check, not outcome material, and the only `retrieved_doc_date` in the log is the filing date. A `git status` filter named `data/qp-topics` only to exclude its lines and read nothing under it. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My own read, formed before consulting the candidate's score, is 0.08. The candidate's 0.12 is close and rests on the same reasoning: wide stakes if a national THC threshold were ever announced, but not from this vehicle.
