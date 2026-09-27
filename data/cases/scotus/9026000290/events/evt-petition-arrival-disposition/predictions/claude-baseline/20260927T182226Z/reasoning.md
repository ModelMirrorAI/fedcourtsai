# Rationale for the numbers

**P(grant) = 0.004.**

## What I read

- `record/snapshots/2026-09-04.json`: paid petition docketed September 3, 2026 (No. 26-290), Term 2026; one docket entry (petition filed, response due October 5, 2026); lower court Court of Appeal of California, First Appellate District (A175551), decided February 9, 2026, with California Supreme Court review denied March 25, 2026. The petitioner is counsel of record for herself — a pro se filer.
- `record/context.json`: `mode: forward`, `band: baseline` under `sal-v4`, `distribution_count: 0`, no CVSG, `signals_observable: true`, `cutoff 2026-09-04` under a `date` cut.
- `record/documents/questions-presented.txt` and `petition.txt` (56 pages, text extracted, not truncated; no brief in opposition exists yet). The petition challenges San Francisco code-enforcement inspections of a front-yard fence and trellis. The state trial court sustained a demurrer to a seventh amended complaint; the Court of Appeal denied a writ petition in a summary order (App. 2, a single page); the California Supreme Court denied review. A parallel federal action was resolved against petitioner on the pleadings in 2023.

## Anchor

The context's band is `baseline` and its `salience_version` (`sal-v4`) matches the statpack's "Segment base rate by salience band (sal-v4)" table, so the anchor is the `baseline` column's bracketed `reached` figure pooled over the nine prior Terms the table renders (OT2017–OT2025, OT2026's row being empty). Pooling the reached rates by their n gives roughly 5.0% over about 12,700 weighted petitions. That is the private-caption class floor for a paid petition at arrival, and it is what the evaluator scores this cell against. I did not use the relist-count cut's relist-0 figure (1.2% granted), per the prompt's warning that it describes petitions that ended undistributed.

## Adjustments, all downward

1. **Pro se filer.** The 5% class floor pools every paid private petition, counseled and pro se. Pro se paid petitions are granted at a small fraction of that rate; this is the single largest adjustment.
2. **No split; the "conflict" is among the Court's own cases.** The QPs ask the Court to choose between Ciraolo/Dow/Marshall and Katz/Kyllo/Horton/Boyd. That is not a lower-court conflict, and the two lines are reconcilable under existing doctrine (observation from a public vantage of an unenclosed yard is not a search). The petition's "conflicting views" section cites a Ninth Circuit case (Bonivert) and Camara but describes no actual disagreement among courts on the question.
3. **Vehicle.** A summary state writ denial with no reasoned opinion; a demurrer to a seventh amended complaint; the named respondent is a state court; many of the "provisions involved" (18 U.S.C. §§ 242, 1964; §§ 1981, 1982, 1985; state bar and evidence codes) are unrelated to the QPs. The Court would have nothing to review and no lower-court reasoning to correct.
4. **Stakes.** One homeowner's fence and trellis permits. `big_case_score` 0.03.

I stop at 0.004 rather than lower because the class floor is the scored yardstick and a small residual covers coding surprises (a mis-parsed disposition, an unexpected GVR).

## Other claims

- `relist-increment` 0.95: from zero distributions, essentially every docketed paid petition is distributed at least once; the residual covers dismissal or withdrawal before conference.
- `cvsg-increment` 0.003: no federal interest.
- `summary-disposition-route` 0.55 (conditional on grant): the statpack's grant family splits about 47% GVR / 53% plenary overall; given this record is an implausible plenary vehicle, I lean slightly toward the cert-order route conditional on a grant. This number rides on a condition I put at 0.4%.
- `dissent-from-denial` 0.01: no Justice's known interests are engaged.

## Uncertainty and where to discount me

The main uncertainty is not the outcome but the yardstick: the baseline floor does not separate pro se from counseled paid petitions, so my number sits well below the scored baseline by design. I did not use the CourtListener MCP server; the state-court writ posture means CourtListener would carry little beyond the prior federal action, and the provisioned petition was sufficient. Two `fedcourts query` calls returned recent-era SCOTUS priors (see `retrieval.md`); they were not informative for this case and did not move the number. The snapshot's `LowerCourt` field names the Court of Appeal while the petition's cover says the Supreme Court of California; the petition's own jurisdictional statement confirms the Court of Appeal's order is the judgment under review, so nothing turns on it.
