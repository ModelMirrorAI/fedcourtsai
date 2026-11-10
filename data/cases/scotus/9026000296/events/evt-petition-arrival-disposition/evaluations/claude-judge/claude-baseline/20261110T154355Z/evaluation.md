# Evaluation: claude-baseline

This is a **cert** cell: the arrival moment of the petition in *Sethi v. United States Court of Appeals for the Ninth Circuit*, No. 26-296, mode forward. **Outcome:** `denied` (`actual_granted` 0), resolved 2026-11-09. The record shows respondents waived their response on Sep 18, the petition was distributed on Oct 14 for the 11/6/2026 conference, and it was denied on Nov 9 with no noted dissent and no CVSG. The segment base rate and skill score are stamped by the harness; any comparison here refers only to "the stamped segment base rate". The claims block is scored in code and not graded here. No semantic set applies at the cert stage.

**Score:** predicted `denied` at P(grant) = 0.012, which is correct. Brier = 0.000144, the best of the three.

## Reasoning quality: 0.85
This is the strongest rationale. It has a correct, transparently computed anchor: the baseline reached rate pooled over OT2017–OT2025 by n, about 5.0%, with the terminal relist-0 row expressly rejected. It also reads the actual Ninth Circuit order under review rather than relying on the petition's account. That order shows the sanction was limited to issues in the show-cause order and that the hearing was waived. It brings in Zauderer as a limit on Ruffalo. The downward adjustments are case-specific and persuasive: the posture of a circuit disciplining its own bar, no split on either question presented, error-correction framing, undisputed fabricated citations across three appeals, and non-specialist counsel. The candidate also states its uncertainty candidly. Minor concerns: the counsel and drafting-slip factor is weak evidence, and the CourtListener docket searches for No. 26-296 risked post-cutoff exposure, although both returned nothing.

## Predicted reasoning: 0.70
The central claims were: denial; SG waiver followed by one distribution for a late-October/November conference and denial there with no relist; timing in the first half of November; and no CVSG or separate writing. All were borne out. The record shows a Sep 18 waiver, an Oct 14 distribution for the 11/6 conference, and denial on Nov 9. The waiver and timing calls are specific commitments a reader could have gotten wrong, which lifts this document above the generic anchor. Its conditional Question 1 and summary-route content is unresolved. It stops short of 0.75+ because the core path, though specific, is still the modal course for this kind of petition.

## Leakage
Forward and clean (`not_applicable`). The candidate retrieved the June 2026 Ninth Circuit order, which is legitimate pre-event lower-court material. Its docket lookups for 26-296 returned 0 results, so it saw no post-snapshot entries.

## Big case
My own read is 0.15.
