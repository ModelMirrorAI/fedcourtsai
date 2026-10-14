# Evaluation — gemini-baseline

P(grant) 0.90, predicted `granted`. Outcome `denied` → correct 0, Brier 0.81.

## Provisioning mismatch — read this first

The predictions and the outcome concern **different petitions**. All three candidates were provisioned (2026-08-21 snapshot, `snapshot_provenance: truncated`) with *Mara Nathan et al. v. Alamo Heights ISD* — a 314-page joint petition from the en banc Fifth Circuit on Texas S.B. 10 (classroom Ten Commandments displays), with a 26A15 extension application in its proceedings — and this event's `event.yaml` carries that title. The docket as it stands now (record snapshot 2026-10-13, `CaseNumber 26-221`) is *Theodore James Purdy, III v. Kansas*, a 140-page paid petition from the Kansas Court of Appeals on a Confrontation Clause question, filed Aug 17 2026. Kansas waived its response (Sep 8), the petition was distributed for the 10/9/2026 conference, and it was **denied on Oct 13 2026**. That denial is what `outcome.json` records (`denied`, `actual_granted` 0, one distribution, no noted dissent). The sibling event `evt-petition-disposition` on the same docket carries the Purdy title. Nothing in the docket I hold mentions Nathan, so the outcome tells us nothing about how the Nathan petition was resolved.

I scored mechanically against `outcome.json` as the contract requires: every candidate predicted `granted`, so `correct` = 0, and the Brier is (p − 0)². These numbers grade a forecast of one petition against the outcome of another. They should not be read as forecast skill until a maintainer settles which petition this docket id belongs to (see `flags.json`). `reasoning_quality` below grades the analysis of the petition the candidate was actually given, and does not lean on the Purdy outcome.

## Common fields

- Stage: cert (arrival moment). Mode: forward, with prediction-time cutoff 2026-08-21.
- Base rate: every candidate froze `band: baseline` (sal-v3), so the stamped segment base rate is the harness's risk-set anchor. I left `segment_base_rate`, `brier_skill_score` and `base_rate_basis` null.
- `vote_accuracy` omitted (cert stage). No `semantic_grades` (not a merits cell). `claim_scores` belongs to the harness.
- `big_case` omitted on purpose. Which case should be read for stakes — the Nathan petition the predictors saw (a nationally significant Establishment Clause / vertical stare decisis question) or the Purdy petition the docket now carries (a fact-bound state-court Confrontation Clause question whose respondent waived its response) — depends on how the mismatch is resolved. A read of either would feed noise into the rank agreement.
- Leakage: forward. The log shows no query for this docket's disposition, no document dated on or after 2026-10-13, and no `data/qp-topics/` read. Graded `not_applicable` and `leakage_suspected` false. The mismatch is a provisioning fault, not a decided case routed into a forward cell.

## Reasoning quality: 0.35

The analysis identifies the core cert hook correctly: a lower court treating *Stone v. Graham* as implicitly abrogated, which conflicts with *Rodriguez de Quijas*. It also anchors on the ~6.5% baseline. But the jump from 6.5% to 0.90 at the arrival moment rests on one paragraph. There is no BIO, no distribution, and no consideration of percolation, defensive denial, or the interlocutory posture beyond a passing "vehicle flaw". "Supreme Court intervention almost inevitable" overstates what can be known at docketing. The rationale is also thin on the record: it gives no circuit split detail, no stakes evidence, and no counter-scenarios. That is under-justification of an extreme number, whichever petition the outcome turns out to belong to.
