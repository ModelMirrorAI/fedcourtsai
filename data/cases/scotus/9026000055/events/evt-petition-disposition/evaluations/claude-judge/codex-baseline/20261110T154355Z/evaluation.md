# codex-baseline — evaluation

**Cell.** scotus/9026000055 (Momin v. Blanche, No. 26-55), `evt-petition-disposition`, stage **cert**, forward distribution moment (`cutoff: null`). Outcome: **denied** on 2026-11-09 off the first distribution (11/6/2026 conference), no CVSG, no noted dissent. `actual_granted` = 0. The segment base rate, its basis and the skill score are left to the harness stamp; refer to "the stamped segment base rate" for the comparison. Claims are scored in code and are not graded here. No `semantic_grades` block (cert cell).

**Leakage.** Forward cell; prediction made 2026-10-17, three weeks before resolution. Nothing in the log or prose reads this petition's disposition as decided. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Big case (own read): 0.05.** The SG's brief in opposition (now in the record) frames the question as whether the Fifth Circuit, in an unpublished per curiam, correctly upheld the BIA's denial of an untimely motion to reopen; it is fact-bound, and the SG denies any conflict with the Ninth Circuit. Stakes are confined to the petitioner.

## Score
Predicted **denied**, P(grant) = 0.05 → correct = 1, Brier = 0.0025.

## Reasoning quality: 0.60
This is a disciplined, well-documented derivation. It correctly anchors on the sal-v4 baseline reached risk set (643/12,877 ≈ 5.0% over Terms 2017–2025, strictly prior). It separates terminal relist/CVSG cuts from forward hazards and keeps "no documents provisioned" distinct from "no issue". Its weakness is that it declines to use the legitimate signals the docket did carry: a paid individual petition from the CA5 agency-review series (25-60xxx) against the Attorney General is, on its face, a petition for review of a BIA order. That category is granted far below the band average. Treating the anchor as the forecast leaves the number at the anchor when the record supported a downward move. The rigor is real, but the analysis stops short of the case.

## Predicted reasoning (0.55)
Central claims: unexplained denial after the November 6 conference, zero additional distributions, no CVSG, no noted dissent or statement. All were borne out. Naming the conference and the zero-increment path is slightly more specific than a bare "deny". It is still the modal path, and the document is open that it cannot speak to the question presented. Right but mostly generic, so just above the midpoint.
