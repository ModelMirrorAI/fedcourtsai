# Evaluation — codex-baseline, 26A428 (Nelsen v. Pike), evt-brief-response-disposition

## The cell

This is an **interim** cell (a State's application to vacate a Sixth Circuit stay of
execution), graded on the forward mode the prediction's own context records. The outcome
is `granted` (`actual_granted` = 1): the application, referred by Justice Kavanaugh to
the Court, was granted on September 30, 2026 and the panel's stay vacated, with Justice
Sotomayor dissenting, joined by Justices Kagan and Jackson. No response was requested
and no amicus was docketed.

## Scores

- `correct` = 1. The prediction's `granted` matches `actual_disposition` exactly.
- `brier_score` = (0.78 − 1)² = 0.0484.
- `segment_base_rate` and `brier_skill_score` are **not written here**: on an interim
  cell the harness pools the baseline from the committed statpack's interim section over
  application-Terms strictly before 2026 and derives the skill from the stamped Brier.
  What the pack supports, read from the committed table: only Terms 2024 (14/70) and
  2025 (17/226) carry parsed substantive resolutions, so the pool is 31/296, which
  clears the 50-resolved floor. If the stamp pools the same rows the rate will be about
  0.105 and the skill strongly positive; whatever it writes is the record. `base_rate_basis`
  stays null structurally (an application freezes no band, and this prediction's
  `context.band` is null, so no cert-band flag applies).
- `vote_accuracy` omitted: this is not a merits cell, and the prediction carried no votes.
- `judgment_correct` null, no `semantic_grades`: neither applies off the merits stage, and
  the prediction's `semantic_claims` is null.
- `claim_scores` is the harness's and is not touched.

## Reasoning quality: 0.85

The rationale correctly identifies the stage, mode, and the exact meaning of `granted`
(unqualified vacatur, mixed relief ungranted). Its base-rate work is right on the
committed pack: it pools the two parsed Terms, quotes the coverage caveat (972 unparsed
2024 rows), and explicitly declines to claim the pooled rate measures the State-vacatur
sub-population. The case-specific analysis is the strongest in the set on the adversarial
side: it retrieved and read both the opposition and the reply (pre-decision filings linked
in its own snapshot), stated the respondent's best argument fairly (a defect-in-integrity
theory under Gonzalez rather than mere new mitigation evidence), checked Gonzalez v.
Crosby's actual text rather than the parties' characterizations, and reported a
misquotation in the State's reply while separately crediting the State's independent
no-prejudice ground. The residual 22% is itemized (preserving the short stay, a procedural
ending if the panel acts first, record uncertainty). Referral at 0.96 was borne out.

What holds it below the top: the move from 10% to 78% leans on a general "different
practical posture" of State applicants rather than on the Court's actual run of
execution-stay vacaturs, which is the most direct evidence for this posture and which the
rationale never names; and given its own reading that the integrity theory was unlikely to
carry, 0.78 reads as somewhat under-confident relative to its own analysis. Those are
calibration remarks on a sound document, not errors.

## Leakage

Mode `forward`; `retrieved_outcome_material` = false; `influenced_prediction` =
`not_applicable`; `leakage_suspected` = false. I checked the forward cell for a
mis-provisioned decided case: the log's case-specific retrieval is the two September 30
briefs, both inside the provisioned snapshot and both pre-decision; the two unobserved
web-search rows were graded on their queries, which name the opposition brief and Gonzalez
v. Crosby, not this application's disposition; the CourtListener calls fetch Gonzalez
only. No `retrieved_doc_date` is at or after resolution, no call names the 26A428 docket,
and the reasoning reads the outcome off nothing. The event resolved the same calendar day
the cell ran (the cell wrote at about 21:55 UTC); the order's clock time is not in the
record, so I cannot say whether the order already existed when the cell ran, only that
nothing in the log or prose reached it. That is recorded as an info flag for the cell.

## Big case

My independent read is 0.55 (see the JSON note): absolute human stakes and high public
attention, a written three-Justice dissent, but a routine shadow-docket application of
Hill and Gonzalez with no majority writing and no doctrinal consequence.
