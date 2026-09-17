# Rationale for the numbers — scotus/73500241, evt-petition-disposition

**P(any grant) = 0.01; predicted disposition `denied`.**

## What I read

Provisioned snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names): paid petition No. 25-1339, docketed June 1, 2026, from the Kansas Court of Appeals (Kansas Supreme Court denied review February 27, 2026). Three docket entries: petition filed May 28; respondent Kansas Department of Revenue waived its response June 3; distributed June 24 for the September 28, 2026 conference. No call for a response, no amici, no CVSG. `context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, `term` 2025, `signals_observable` true, cutoff null (so the snapshot is the latest poll, dated today).

Provisioned documents: `petition.txt` (22 pages, text extracted cleanly) and `questions-presented.txt`. No brief in opposition exists because the respondent waived. I read the full petition; the reasoning below rests on it.

## Anchor

Cert stage, `moment: distribution` (event `evt-petition-disposition`, no `stage` or `moment` field, so it reads as cert). Band `baseline`, and the context's `salience_version` `sal-v4` matches the statpack's "Segment base rate by salience band (sal-v4)" heading, so the band table is the anchor. Pooling the `baseline` column's bracketed `reached` figures over every rendered Term strictly before this case's own (2017 through 2024; the table renders 10 of 10 Terms, so the shown window is the window):

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

Weighted pool: about 593 grants over 11,580, so **roughly 5.1%**. That is the rate for a paid private petition that ever reached the baseline band, and the yardstick the evaluator will score this cell against. (The modern-cert overall split is 655 granted and 577 GVR against 41,573 denied; the relist-0 cut reads granted 1.2% plus gvr 0.5%, but that is the terminal-state figure and understates a petition that could still climb.)

## Adjustments, all downward

1. **Respondent waived and no response has been called for.** A grant almost never issues on a waived-response docket without a call for a response first, and the Court has had the petition since June without calling for one. Nothing in the record suggests it will. This alone moves me well below the band pool.
2. **The QP does not present the split the petition invokes.** The petition's "six-four split" is about whether the Fourth Amendment governs continued retention of lawfully seized property (Asinor, D.C. Cir. 2024; Honda Lease Trust, 3d Cir. 2025; Brewster, 9th Cir.; against Lee, Shaul, Denault, Fox, Case). The petitioners brought a Fifth Amendment claim, and the Kansas Court of Appeals rejected it on the ground that a tax assessment is not a taking. The QP asks whether retention "in and of itself" violates the Fifth Amendment. No circuit on either side of the cited split holds that, and the courts the petition puts on "its" side treat the claim as procedural due process, which is not what was pleaded or decided below. The Court does not reformulate a question this far from the decision under review.
3. **Vehicle defects.** State intermediate appellate decision with no state supreme court opinion; property returned in October 2023, so the case is purely a damages suit against a state agency and an officer, raising sovereign-immunity, "person" under §1983, and limitations questions the petition never addresses; the trial court dismissed the federal claim in "a single sentence," so there is no developed reasoning to review. The petition also attributes Federal Circuit and Tenth Circuit "illegal exaction" cases (Norman, Ecco Plains, Aerolineas Argentinas) to this Court, which a clerk will notice.
4. **Petition quality and counsel.** A 14-page argument from a Wichita firm without Supreme Court practice, no amici, no supporting statement from the courts below flagging the question.
5. **No GVR source.** I know of no decided or pending case whose judgment would prompt a GVR of a Kansas tax-as-taking dismissal.

Culley v. Marshall (2024) is the nearest recent precedent in the retention-of-seized-property area; it resolved the procedural due process question on civil-forfeiture retention and cuts, if anything, toward the Court treating that area as settled for now. It is general legal knowledge, not retrieved material, and did not drive the number.

Net: from about 5% to **0.01**. I would not go lower than 1% because the underlying subject (post-justification retention of seized property) is one at least two Justices have shown interest in, and a stray call for a response is not impossible.

## The other claims

- **relist-increment 0.10.** One distribution shown, never relisted. A second distribution would come from a call for a response (my best guess about 5%), a relist for a possible statement or hold (about 2 to 3%), or a reschedule that generates another `DISTRIBUTED` entry (a few percent; the statpack warns the count is an upper bound on true relists for exactly this reason). The paid scored segment's relist share sits near 25% but that pools petitions far stronger than this one.
- **cvsg-increment 0.01.** No federal interest.
- **summary-disposition-route 0.50.** Conditional on a grant. Plenary review of this vehicle is essentially foreclosed by the QP mismatch, so if a grant happened at all a GVR is the likelier shape, but I know of no intervening authority to GVR in light of. Among baseline-band grants the pack's gvr share is about a third (0.4% gvr against 0.8% granted); I sit above it because of the plenary-route defects. This is a low-confidence conditional.
- **dissent-from-denial 0.03.** No baseline published. The subject has drawn separate writings from Justices Gorsuch and Sotomayor in the forfeiture setting, but not on a vehicle like this one.
- **big_case_score 0.08.** A family's damages claim over a tax levy returned in 2023. Low stakes even if decided.

## Uncertainty and where to discount me

- I could not read the Kansas Court of Appeals opinion (not in CourtListener; not provisioned). My account of its reasoning is the petition's own characterization, which is adversarial. If the opinion below actually engaged the Fourth/Fifth Amendment vehicle question, adjustment 2 is weaker than stated, though the waived response and the vehicle defects would still hold the number near the floor.
- I could not confirm whether the District of Columbia or Malanga's Auto sought certiorari from the Asinor and Honda Lease Trust decisions; a pending petition on the real split would make a hold-and-GVR route slightly more live. CourtListener showed no SCOTUS docket for either.
- The `fedcourts query` call returned no comparable priors and contributed nothing to the number; the corpus read stands recorded in `retrieval.md`.
- I know nothing about this case's disposition; the docket snapshot is current to today and the conference is eleven days out.
