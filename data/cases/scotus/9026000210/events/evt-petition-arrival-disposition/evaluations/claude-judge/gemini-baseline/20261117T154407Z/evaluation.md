# Evaluation — gemini-baseline, scotus/9026000210, evt-petition-arrival-disposition

**Stage:** cert (arrival moment). **Outcome:** petition denied on 2026-11-16, after a single distribution (conference of 2026-11-13), with no noted dissent or statement.

## Scores

- Predicted `granted` at P(grant) = 0.85; actual `denied`. `correct` = 0.
- `brier_score` = (0.85 − 0)² = 0.7225.
- `vote_accuracy` omitted (cert cell). The segment base rate, its basis and the skill score are the harness's to stamp and are left null; no semantic set is declared on a cert cell, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.25)

The rationale is thin and overconfident. It cites the federal-band anchor only as a loose range ("often between 50% and 80%") rather than pooling it, then moves *above* the top of that range on a single generalisation — that the Court "frequently grants certiorari when a lower court enjoins major federal executive actions" — and asserts the majority "will almost certainly want to review this injunction." The one feature of the case that most plausibly explains the denial, the preliminary-injunction (interlocutory) posture, appears only as a parenthetical aside in the dissent-from-denial line and is given no weight in the headline number. There is no discussion of the absence of a circuit split, of vehicle problems, or of the missing brief in opposition. One sentence about the record ("the Form Termination Class lacked standing/APA success") is garbled relative to the decision below. The analysis is directionally conventional for an SG petition, which keeps it off the floor, but nothing in it would have let a reader see the denial coming, and the upward adjustment was unsupported.

Base-rate figures were checked against the statpack build the candidate was placed against (`statpack-at`: build 02dd6a20fccc, landed 2026-08-19, no alternative build), not the currently committed pack.

## Predicted reasoning (`predicted_reasoning_quality` = 0.05)

Central claims: the grant itself (led with, stated as "highly likely"), one or two relists, plenary rather than summary treatment (conditional on a grant that never happened — neither credit nor penalty), and a dissent from denial "from several of the conservative justices" should the Court deny. The grant failed. The relist forecast failed: one distribution, denial on the next order list. The one conditional that the outcome did reach — the denial branch — also failed: the denial drew no noted dissent. The only borne-out item, no CVSG, is entailed by the Solicitor General being the petitioner and earns nothing. A specific forecast wrong in direction with its denial-branch call also wrong: 0.05.

## Leakage

Forward cell, run the day after docketing and about three months before the denial. Forward cell: predicted 2026-08-20, the day after docketing; the petition was denied 2026-11-16. Log: 21 calls, result capture coverage 0.0 (all unobserved, graded on queries): provisioned files, the statpack, a CourtListener search for 'Thakur' and a read of the Ninth Circuit opinion below (decided May 2026, predating the event). No retrieved_doc_date on or after resolution, no read under data/qp-topics/, no order or opinion resolving this petition cited, and the reasoning nowhere presupposes a result (it forecast the opposite). Confirmed genuinely unresolved at prediction time. `influenced_prediction` = `not_applicable`; `leakage_suspected` = false.

## Big case

My own read: 0.6. Solicitor General petition on whether the First Amendment bars viewpoint-based termination of competitive federal research grants; a classwide preliminary injunction against a flagship executive policy, with many parallel suits. The subject matter is nationally significant, but the Court denied review at the first conference with no noted dissent or statement, leaving an interlocutory Ninth Circuit ruling in place and deciding nothing; the question remains open for a later final-judgment vehicle. High-stakes subject, modest realized significance for this docket.
