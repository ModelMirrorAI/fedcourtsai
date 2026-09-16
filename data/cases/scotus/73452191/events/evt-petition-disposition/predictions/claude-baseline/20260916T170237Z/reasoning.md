# Why 0.025

## Inputs read

- `record/snapshots/2026-09-15.json` (the provisioned baseline; `context.json` names `snapshot_date: 2026-09-15`).
- `record/context.json`: `mode: forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `cutoff: null`.
- `record/documents/documents.json`, `petition.txt` (29 pages, `empty_text: false`, not truncated) and `questions-presented.txt` (cleanly cut). No brief in opposition exists: the docket's July 7, 2026 entry is a **waiver** of the respondent's right to respond.
- `event.yaml`: kind `petition`, no `stage` or `moment` field, so it reads as a **cert-stage** cell at the **distribution** moment (event `evt-petition-disposition`).
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table.

## Anchor

The frozen band is `baseline` and the table's salience version (`sal-v4`) matches the context's, so the band table is the anchor. Pooling the **bracketed `reached`** figure for `baseline` over the rendered Terms strictly before this case's Term (OT2017 through OT2024, eight rows; the table renders ten Terms and OT2026 is empty):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled: **5.1%** (n = 11,580). That is the rate a paid petition that has reached the baseline band faces, and the yardstick my skill is scored against. The whole-segment cuts agree on shape: relist bucket 0 grants about 1.7% (granted + gvr), CVSG `none` about 6.3%, originating circuit `ca3` about 2.4% on the pooled (paid plus IFP) docket.

## Adjustments down (dominant)

1. **Forfeiture below.** By the petition's own account (pp. 9-10, 19-21), the Third Circuit held that the "judge as law-enforcement officer" theory "was not raised in the District Court and has therefore been forfeited," and the district court had recorded that plaintiffs "do not dispute that all acts taken by the Judicial Defendants were done in their judicial capacity." The Court does not take questions the lower courts held unpreserved, and the petition's answer (Singleton v. Wulff, and a preservation argument under a Third Circuit sentencing case) is weak. This is the single largest discount.
2. **Unpublished, non-precedential opinion** (App. 1a, "unreported"; CourtListener does not index it at all). The Court treats these as poor vehicles and the decision does not bind future Third Circuit panels, which undercuts the "three States without a remedy" framing.
3. **The split is softer than pleaded.** Gibson v. Goldston (4th Cir. 2023) and Rockett v. Eighmy (8th Cir. 2023) are real and recent (confirmed on CourtListener), but both involve a judge **personally** searching a home or **personally** jailing minors. King v. Love and Harper v. Merckle are 1980s cases with different facts. Here the judge is alleged to have **directed** sheriff's deputies to bring a contemnor to court in a pending case. That is much closer to Mireles v. Waco (1991), where ordering officers to bring an attorney before the court was held a judicial act even if carried out with excessive force. The petition tries to distinguish Mireles on the courthouse-versus-home line, but the Court is more likely to see Mireles as controlling than to see a conflict.
4. **Respondent waived, and no call for a response before distribution.** The waiver is the respondent's signal that the petition is not taken seriously; the Court's silence between the July 7 waiver and the July 15 distribution is a weaker but concordant signal. A CFR at or after the long conference remains possible and is priced into the relist claim, not the grant number.
5. **Unsympathetic posture and petition quality.** The underlying dispute is a landlord-tenant contempt fight in which the petitioner (a Pennsylvania attorney) was twice arrested for noncompliance; the petition has drafting errors (e.g., "summarily reverse as the judicial immunity") and rhetorical passages (Pitt the Elder) that read as a disgruntled-litigant filing rather than a repeat-advocate vehicle. Counsel is an experienced Washington lawyer but not a Supreme Court specialist.
6. **Plaintiff-side immunity petition.** Grants and summary reversals in section 1983 immunity cases skew heavily toward the government defendant; a plaintiff asking the Court to strip absolute immunity from a judge on a 12(b)(6) record is swimming upstream.

## Adjustments up (minor)

- Paid, counseled, timely, with a genuinely framed legal question and a Rule 12(b)(6) posture that makes the facts clean if the Court wanted them.
- Judicial immunity is a doctrine a few Justices have expressed interest in revisiting, and the Lo-Ji Sales line is under-developed at this Court.

Net: from 5.1% to **0.025**. I would put the honest range at 0.015 to 0.04; the forfeiture ruling alone justifies halving the anchor, and the Mireles problem takes most of the rest.

## Claims

- `disposition` 0.025: restates the above.
- `relist-increment` 0.15: from one distribution. About a quarter of baseline-reached petitions ever move to `elevated` (the elevated `reached` n over the baseline `reached` n runs 22% to 27% across recent Terms), which is roughly P(any further distribution) for the population. I discount to 0.15 because this docket's most plausible second distribution is a CFR-then-redistribute, and the forfeiture problem makes a CFR less likely than average; a reschedule out of the long conference is the residual.
- `cvsg-increment` 0.005: about 1.2% of the paid scored segment ever gets a CVSG and this case has no federal interest.
- `summary-disposition-route` 0.35 (conditional on grant): the cert-order share of the grant family runs 30% to 59% by Term in the statpack; I shade below the middle because there is no intervening decision to GVR against and plaintiff-side summary reversals in immunity cases are rare, while the petition's explicit alternative request and the 12(b)(6) posture keep the route live.
- `dissent-from-denial` 0.03 (conditional on denial): above the roughly 1% to 2% docket-wide rate because the doctrinal hook (Lo-Ji Sales, the functional test) is the kind Thomas or Gorsuch occasionally write on; well below anything higher because of forfeiture and facts.

## Big-case score

0.15. A judgment on judge-directed arrests would be doctrinally interesting and would get legal-press coverage, but the case is a single contempt dispute and the immunity question is narrow.

## Uncertainty and where to discount me

- I have not read the Third Circuit opinion itself (unindexed on CourtListener; not provisioned). My reading of the forfeiture holding is from the petition's quotations of App. 8a n.8 and 9a. If the forfeiture footnote is softer than the petition concedes, discount adjustment 1.
- My belief that cert was sought and denied in Gibson v. Goldston is from memory and not verified this run (CourtListener's SCOTUS docket index returned nothing for either Gibson or Rockett). It did not move the number.
- The corpus query I ran returned recency-ranked granted priors that were mostly emergency applications and unrelated cert grants; no corpus filter reaches judicial immunity, so no similar-case prior set informs this cell.
- Forward mode, no `DECIDED_BEFORE` clock. Nothing I retrieved postdates the snapshot or touches this docket's disposition, which cannot exist before September 28, 2026.
