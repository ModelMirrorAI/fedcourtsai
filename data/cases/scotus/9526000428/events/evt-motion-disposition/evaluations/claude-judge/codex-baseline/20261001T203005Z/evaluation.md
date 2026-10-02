# Evaluation — codex-baseline — Nelsen v. Pike (26A428), evt-motion-disposition

## Cell and outcome

Interim-stage cell (`event.yaml` stage `interim`, moment `arrival`), forward
mode. The State of Tennessee applied on September 30, 2026 to vacate the Sixth
Circuit's same-morning stay of Christa Pike's execution. The outcome is
`granted` (`actual_granted` 1): the application, referred by Justice Kavanaugh
to the full Court, was granted and the stay vacated on September 30, 2026, with
Justice Sotomayor dissenting joined by Justices Kagan and Jackson. The outcome's
`interim_signals` read referred true, response requested false, amicus 0.

## Scores

- `correct` = 1: predicted `granted`, outcome `granted`.
- `brier_score` = (0.82 − 1)² = 0.0324, the best of the three.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: not mine on an
  interim cell. The harness pools the substantive application slice over
  application-Terms strictly before 2026 and derives the skill from the
  stamped Brier. From the committed statpack the only strictly-prior Terms
  with parsed substantive rows are 2025 (17/226) and 2024 (14/70), a pool of
  31/296 ≈ 10.5% that clears the 50-resolved floor, so I expect the stamp to
  be non-null. If it comes back null, the pack in force at stamp time either
  dropped below the floor or lost its parsed prior-Term rows; the committed
  pack I read supports the pool. Terms 2016–2023 carry zero parsed rows and
  Term 2024 has 972 unparsed applications, so whatever rate is stamped rests
  on two partially covered Terms.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted or null. Not
  a merits cell; no semantic set is declared.
- `claim_scores`: the harness's (`interim-v1`).

## Reasoning quality: 0.80

A disciplined and well-bounded rationale. It states exactly what it read and
what it did not, computes the statpack pool correctly (31/296 with the same
coverage caveats), and refuses to treat the pooled rate as a measured frequency
for this posture. Its four numbered grounds are the right ones, and each
carries its own qualification: the Gonzalez v. Crosby merits-attack
characterization, checked against the opinion's own text on CourtListener
rather than the application's gloss; the point that the "new" state-counsel
statement does not touch the ground on which the mitigation claim was actually
rejected (cumulativeness and lack of prejudice); the panel's stay rationale
lacking the usual findings, with the honest caveat that an administrative
pause to settle jurisdiction is a real counterargument; and the 47-day delay,
read as supporting an equitable objection without adopting the State's
rhetoric about motive. The remark that the application's Price v. Dunn
citation is to a concurrence, not a majority holding, is a precise reading
that the other candidates did not make. The 0.18 complement is itemized.

Two things keep it below claude-baseline. The candidate reasoned solely from the
State's application and says so; the Sixth Circuit order and dissent were a
single CourtListener call away and would have let it test the panel's stay
rationale directly instead of conditionally ("if the application's
description is accurate"). The honesty about the limit is to its credit, but
the limit was avoidable. Second, the section on the increments misreads how
the response signal is recorded: it forecasts a formal response request at
0.94 on the strength of the execution-day posture, where the Court's practice
on same-day capital vacaturs is a filed response with no request entry, which
is what the docket shows. I note that as a reasoning point, not as a score on
the claim, which the harness grades.

## Big case

My independent read is 0.5 (formed before reading the candidate's 0.78): a life
at stake and national coverage, against a narrow, settled procedural question.
The candidate's 0.78 weights the immediate life-or-death consequence more
heavily than I do; its rationale names the same discount for narrow doctrine.
No agreement number is computed here.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected`
false, `retrieved_outcome_material` false. The prediction and the resolution
share the calendar day, so the date test alone is uninformative and I read the
calls. Log coverage is 0.93: the two `unobserved` rows are web searches whose
queries are generic precedent lookups (Gonzalez v. Crosby at 545 U.S. 532; a
Justia page for the same reporter cite) naming neither party nor the docket, so
graded on their queries they are clean, and I do not credit them as having
returned nothing. The captured outside calls are three CourtListener lookups
that resolve and read the 2005 Gonzalez opinion. No call named Nelsen, Pike,
26A428, or the disposition, and none touched `data/qp-topics/`. The prose
explicitly disclaims knowledge of the outcome and declines to infer anything
from the scheduled execution time having passed, which is the right posture.
