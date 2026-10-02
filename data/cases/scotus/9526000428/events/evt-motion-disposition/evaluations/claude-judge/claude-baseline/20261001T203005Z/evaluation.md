# Evaluation — claude-baseline — Nelsen v. Pike (26A428), evt-motion-disposition

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
- `brier_score` = (0.72 − 1)² = 0.0784.
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

## Reasoning quality: 0.85

The strongest of the three rationales, on three counts.

First, it did not take the applicant's word for the record. It located the
Sixth Circuit docket on CourtListener, read the published stay order and Judge
Griffin's dissent directly, and confirmed from the order itself that it
contained no likelihood-of-success analysis and rested on the need to
"properly analyze the parties' fully briefed arguments." That is the fact the
Court's vacatur turned on, independently verified rather than inferred from
the State's characterization.

Second, the reference-class argument is explicit and well sourced. It computes
the statpack pool correctly (31/296, with the coverage caveats stated),
explains why that pool mixes applicant classes with opposite grant histories,
and then names the actual run of State applications to vacate last-minute
capital stays (Dunn v. Ray, Dunn v. Price, the Barr applications, Hamm v.
Reeves, Hamm v. Smith) and the salient denial (Dunn v. Smith, 2021), flagging
that the roughly three-in-four class rate is from memory and not a committed
cut. I did not verify every entry in that list, and the candidate's own
discount is the right handling; the class-level conclusion is correct.

Third, the downside is actually analyzed. The mootness path (the panel ruling
and dissolving its own stay before the Court acts), the greater resistance of a
published 2-1 order, and the single-date execution warrant are each real and
each would have resolved the application as ungranted under the vocabulary. The
0.28 complement is a reasoned number.

Two smaller points, one each way. The document correctly anticipated how the
harness records the response signal (a filed response without a "response
requested" entry), which is what happened. Against that, the prediction landed
at 0.72, the second-lowest of the three, after an analysis that reads as more
confident than the number: the document's own class rate and case-specific
factors arguably support a higher figure. That is a calibration remark, not a
soundness defect, and it is why the grade is not higher still.

## Big case

My independent read is 0.5 (formed before reading the candidate's 0.60): a life
at stake and national coverage, against a narrow, settled procedural question.
The candidate's 0.60 and its rationale (Pike as Tennessee's only woman on death
row; the question narrow and governed by Gonzalez) track the same reasoning.
No agreement number is computed here.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected`
false, `retrieved_outcome_material` false. The prediction and the resolution
share the calendar day, so the date test alone is uninformative and I read the
calls. Log coverage is 1.0. The outside calls were: one corpus query for
granted applications (no filter reaching this case, nothing used), two
CourtListener searches (the Sixth Circuit docket 26-5864 and the E.D. Tenn.
habeas docket), one read of the Sixth Circuit stay order (the order under
review, not the disposing order), and one listing of the Sixth Circuit docket
entries, which ran through the 09:17 stay order with nothing later. No call
touched the Supreme Court application docket or `data/qp-topics/`. One shell
call grepped the candidate's own prior predictions on other
`evt-motion-disposition` cases for a format template; that reveals nothing about
this case. The prose states the candidate had no knowledge of the disposition
and did not seek it, consistent with the log.
