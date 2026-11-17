# Evaluation: codex-baseline, Loop v. Washington (No. 26-369), evt-petition-disposition

**Stage:** cert. **Outcome:** petition denied on 2026-11-16 after a single distribution, with no CVSG and no noted dissent.

## Scores

- Predicted `denied` at P(grant) = 0.025; actual `denied`. `correct` = 1.
- `brier_score` = (0.025 - 0)^2 = 0.000625.
- `reasoning_quality` = 0.84.
- `predicted_reasoning_quality` = 0.76.
- The segment base rate, skill score and basis are the harness's to stamp and are left null here, as are the claim scores. No vote accuracy and no semantic grades apply on a cert cell.

## Reasoning

A careful and epistemically disciplined rationale. It anchors on the frozen reached-band rate and explains why the terminal rate and the marginal amicus, relist and CVSG cuts are shape rather than multipliers, including the point that the 2+ amicus bucket is a disposition-time count correlated with other attention. Its vehicle analysis tracks the staged appendix closely: the memorandum's de facto appeal characterisation and refusal to reach newly raised matters (App-1 to App-2), the complaint language and requested relief the district court quoted (App-6 to App-7), the alternative immunity and failure-to-state-a-claim grounds (App-7 to App-9), and the September 1, 2025 expiry, where it sensibly declines to declare the whole case moot. Its reading of T. M. is the most accurate of the three: adverse context that does not eliminate the independent-injury distinction and supplies no GVR hook.

Short of the top because it gives little explicit weight to the single most decisive signal, the two waivers with no call for a response, which it records but does not treat as near-conclusive at a first conference; that omission is likely why its grant probability and its 18% further-distribution figure sit higher than the record warranted. The final number is described, candidly, as a judgmental adjustment.

## Predicted reasoning

Central claims: denial in the orders after the November 13 conference, zero further distributions as the modal path, no CVSG, and no separate writing. All four were borne out. The document opens with flat commitments ("will deny", "will not call for") and names the modal path explicitly, which is more committal than a bare probability, though it kept 18% on a further distribution. The conditional QP1-narrowing and plenary-route content is neither credited nor penalised. As with the other candidates, the borne-out path is the expected one for a waived petition from an unpublished decision, so the grade sits at the 0.75 anchor rather than above it.

## Leakage

Forward cell run 2026-10-31 against a 2026-10-31 snapshot; the petition was denied 2026-11-16. Captured calls show provisioned-file reads, two corpus queries (one legible retrieved_doc_date of 2026-04-29, before the run), and CourtListener retrieval of T. M. (June 2026). Two web-search rows are unobserved; graded on their queries, they sought Skinner and T. M. Rooker-Feldman material on the Court's site, not this petition's docket or disposition. Nothing dated on or after resolution; the reasoning treats the outcome as open and says so. Graded `not_applicable`; `leakage_suspected` false.

## Stakes

My own read is 0.12: An unpublished two-page Ninth Circuit memorandum affirming a Rooker-Feldman dismissal of a pro se section 1983 suit arising from one domestic-relations arbitration and an expired restraining order. Five advocacy-group amicus briefs show some interest in the parental-rights/private-arbitration theme, but both respondent groups waived, no response was called for, and the petition was denied at its first conference without a noted dissent. Low stakes beyond the parties.
