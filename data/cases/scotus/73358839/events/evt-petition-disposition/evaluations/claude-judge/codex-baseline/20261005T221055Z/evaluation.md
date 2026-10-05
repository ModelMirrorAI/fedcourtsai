# Evaluation of codex-baseline — scotus/73358839, evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition for certiorari before judgment (No. 25-1290, Texas Top Cop Shop v. Blanche) was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent or statement. `actual_disposition = denied`, `actual_granted = 0`.

- `correct = 1`: predicted `denied`, outcome `denied`.
- `brier_score = (0.08 - 0)^2 = 0.0064`.
- `segment_base_rate = 0.172379`, basis `risk_set`. The prediction froze `band = elevated` under `salience_version = sal-v4`, and the statpack's "Segment base rate by salience band" heading names sal-v4, so the bracketed `reached` figures apply. Pooled resolved-weighted over every rendered Term strictly before the case's docket Term (2025): OT2017–OT2024, denominators 400, 347, 334, 397, 342, 300, 354, 336 (n = 2,810), numerator ≈ 484.39 grant-equivalents from the rounded published rates. The caption says the table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no divergence from the in-code ten-Term lookback arises (the two pre-2017 Terms the lookback would admit are simply absent from the pack, which shortens the sample rather than changing it).
- `brier_skill_score = 1 - 0.0064 / (0.172379 - 0)^2 = 0.7846`. Well above the band baseline.
- `vote_accuracy` omitted (cert stage; never scored). `judgment_correct` null. No semantic set is declared on a cert cell, so no `semantic_grades` block.
- `claim_scores` is the harness's; not written.

## Reasoning quality: 0.84

What the rationale got right, and why it earns a high mark:

- **Correct anchor, correctly pooled.** It derived the same 17.24% pooled reached-elevated rate from the same eight prior Terms I used, excluded the case's own Term and the empty 2026 row, and said plainly that the figure is built from rounded percentages. It kept the harness's frozen band rather than re-deriving it.
- **Read the docket accurately.** It saw that the two distribution entries are not two conference considerations (a June 5 reschedule preceded the first conference), and discounted the relist signal accordingly. That is the right reading and the statpack warns of exactly this.
- **Identified the decisive posture.** Cert before judgment under Rule 11, an appeal in abeyance below, a companion petition (NSBU, No. 25-1201) that gives the Court a cleaner vehicle, the government's response waiver, and the interim domestic-company exemption lowering urgency. Each is a real reason the Court would pass on this petition, and the Court did.
- **Scrupulous about provenance.** It separated what the provisioned record supports from what it could not verify (it did not know whether rulemaking had changed after the petition, and said so), and it reported its two failed web attempts rather than inventing a Rule 11 citation.
- **Calibrated adjustment.** Moving from 17% to 8% for a tag-along cert-before-judgment petition is a defensible size of move, with offsetting factors (two constitutional questions, 25 state amici, earlier emergency-docket involvement) weighed explicitly.

Where it falls short of the top:

- It did not learn that FinCEN had already finalized the domestic-entity exemption in August 2026, which was public and knowable in a forward cell and bears directly on the mootness objection the government was pressing in the companion. The rationale gestures at the complication but treats it as an unverified possibility.
- It did not check the companion's status at all, though its own analysis makes the companion the hinge of the forecast. A single docket lookup would have grounded "another vehicle exists" in current fact.

Neither gap led it astray here, but a rationale this careful about what it did not know could have closed those gaps cheaply.

## Leakage

Mode `forward`. The log shows 28 calls: the prompt, schemas, the provisioned snapshot and petition text, the statpack, and two unobserved web-search rows whose queries are generic Rule 11 lookups naming no case. No `retrieved_doc_date` on or after 2026-10-05, no query for this docket beyond the provisioned record, and no `data/qp-topics/` read. The prediction's own snapshot date (2026-09-18) shows the petition pending for the 9/28 conference, so the case was genuinely open when predicted. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. Note that the candidate's `flags.json` is not staged, so this rests on the log and the reasoning, not on the absence of a disclosure.

## Big case

My independent read is 0.55 (see the JSON notes). I record that the staged `prediction.json` exposes each candidate's `big_case_score`, so I had seen the predictor's number before writing mine; I formed the read from the case itself and the outcome, but the anchoring risk the prompt describes was not fully avoidable here.
