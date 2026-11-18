# Evaluation of `codex-baseline` — `scotus/9026000100` (`evt-order-call-for-response-disposition`)

## Summary of quantitative scoring

- **Stage:** `cert` (`moment: response-requested`, opened `2026-08-13`, resolved `2026-11-16`). No semantic claim set (`semantic-v1`) or vote accuracy is scored on a cert-stage cell.
- **Outcome match (`correct = 1`):** `codex-baseline` predicted `denied` (`probability = 0.12`, `granted = 0`), matching `outcome.json` (`actual_disposition = "denied"`, `actual_granted = 0`).
- **Brier score (`0.0144`):** `(0.12 - 0)^2 = 0.0144`.
- **Baseline and skill:** Left null for the harness (`segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are computed and stamped by `stamp-cell` from the stamped segment base rate). To audit `codex-baseline`'s own base-rate discussion without penalizing post-run statpack drift from `sal-v4` to `sal-v8`, we reconstructed the statpack build in force at `run_id = 20261029T160941Z` via `fedcourts statpack-at` (`7bcde3b105cb212283905eda17b827efc188e80c`, `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, landed `2026-10-28T13:56:30-04:00`). Every `sal-v4` figure cited in `codex-baseline`'s rationale reproduces cleanly against that build.

## Reasoning quality (`reasoning_quality = 0.85`)

`codex-baseline`'s `reasoning.md` delivers a disciplined, well-sourced, and methodologically sound cert-stage analysis:

1. **Rigorous base-rate and information-set discipline:** Against statpack build `7bcde3b105cb`, `codex-baseline` properly selected the `sal-v4` risk-set (`reached`) denominator rather than the terminal `baseline` rate, excluded incomplete OT2026 rows, declined to multiply unconditional terminal relist/CVSG cuts into a forward transition hazard, and presciently refused to over-weight the absence of cert-stage amicus briefs as of August 13 because support could arrive on the post-CFR schedule (four amicus briefs were in fact filed on September 14, 2026).
2. **Accurate doctrinal and vehicle diagnosis:** Having read the petition alongside both appended lower-court decisions (App. A and App. B) and verified the official Supreme Court opinions in *Hittle v. City of Stockton* (No. 24-427, Mar. 10, 2025) and *Ames v. Ohio Department of Youth Services* (No. 23-1039, June 5, 2025), `codex-baseline` rightly separated two-Justice interest (Thomas and Gorsuch) from a four-vote grant coalition. More importantly, it identified the core vehicle obstacles that Respondent's October 14, 2026 Brief in Opposition actually foregrounded: the unpublished Ninth Circuit disposition creating no circuit split on binding rules, the contested collision record (police fault findings, asserted admission of fault, additional driving violations, and comparator distinctions addressed at App. 18a–20a), the unpleaded failure-to-accommodate claim (App. 20a n.2), and the petition's overreading of *Bostock* on mixed causation.
3. **Calibration limitation (`0.12`):** Where `codex-baseline` fell slightly short of the strongest analysis in this cohort was in lifting `P(any grant)` all the way to `0.12`. In particular, `codex-baseline` did not highlight the sharpest structural vehicle rebuttal in App. 21a—that CCCTA *conceded* the *McDonnell Douglas* prima facie case on Cross's retaliation claim and still won summary judgment at step three under the settled honest-belief rule, proving on this very record that skipping step one would not alter the Rule 56 outcome—and gave somewhat generous weight to the CFR + *Hittle*/*Ames* pairing given that *Hittle* itself (published opinion, clean preservation, five distributions) had recently failed to draw more than two votes.

## Predicted reasoning (`predicted_reasoning_quality = 0.82`)

`codex-baseline`'s `predicted_reasoning.md` committed to five central claims (four testable against the resolved cert record and one conditional on a grant):

1. **Denial after the requested response (`borne-out`):** Certiorari was denied on November 16, 2026 after Respondent filed its Brief in Opposition on October 14, 2026.
2. **One or two further distributions and disposition by year-end 2026 (`borne-out`):** The petition was redistributed once on October 28, 2026 for the November 13, 2026 conference (`distribution_count = 2`) and denied on November 16, 2026, well before the end of 2026.
3. **No CVSG (`borne-out`):** No invitation to the Solicitor General was issued (`cvsg_date: null`), for the institutional reasons `codex-baseline` stated.
4. **Conditional narrowed Rule 56 question and plenary-over-summary route if granted (`unresolved`):** Untested because certiorari was denied; earns neither credit nor penalty.
5. **No separate writing on denial (`borne-out`):** Despite Justice Thomas's prior writings in *Hittle* and *Ames*, `codex-baseline` committed to an unannotated denial as the modal outcome (80% conditional share), matching `noted_dissent_from_denial: false`.

Every testable claim in `predicted_reasoning.md` held up, including two genuinely discriminating calls on a CFR petition in Justice Thomas's *McDonnell Douglas* wheelhouse (resolution before year-end 2026 rather than an extended *Hittle*-style relist run or Term-long hold, and denial without a separate dissent or statement). The score sits at `0.82`—solidly above `0.75`—moderated from `1.0` because its conference-count framing remained mildly hedged ("usually one or two further distributions... A further true relist is possible") and did not specify the concrete post-BIO vehicle record as tightly as a top-anchor forecast can.

## Leakage and big-case notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** `codex-baseline` ran in `forward` mode on `2026-10-29`, eighteen days before the `2026-11-16` denial existed. Review of `retrieval_log.json` (52 calls, 46 `captured`, 6 `unobserved` `site.supremecourt.gov` PDF lookups for 2025 *Hittle* and *Ames* opinions) confirms clean forward execution with no access to `data/qp-topics/` or post-cutoff target-docket filings.
- **Big-case read (`evaluator_score = 0.22`):** While the Question Presented pitched a high-stakes challenge to *McDonnell Douglas* at summary judgment and drew four cert-stage amicus briefs, the case itself was an unpublished single-employee termination dispute that ended in an unremarked cert denial with zero doctrinal impact.
