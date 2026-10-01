# Evaluation — gemini-baseline — Nelsen v. Pike (26A428), evt-motion-disposition

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
- `brier_score` = (0.70 − 1)² = 0.09.
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

## Reasoning quality: 0.55

The rationale is a single paragraph and gets the structure right: it anchors on
the ~10.5% pooled interim rate, identifies why that pool is the wrong reference
class for a State's application to vacate a last-minute stay, names the two
dispositive points the Court in fact acted on (the panel's failure to find a
likelihood of success, and the Rule 60(b) motion as a disguised successive
petition), and reads the compressed timeline correctly (referral quick, no
time for a response request, no amici). Everything it says is sound and the
direction and rough magnitude of the adjustment were right.

What holds it at the midpoint is thinness rather than error. Every fact in the
document comes from the State's application, and the document never says so or
weighs that the characterizations of the Sixth Circuit order and of Pike's
motion are an advocate's. No authority is named: Gonzalez v. Crosby, Price v.
Dunn, Bucklew, and Hill v. McDonough are all in the application and none is
engaged. The only counter-consideration is that the respondent "can assemble a
compelling opposition," with no account of the realistic alternative paths (the
panel ruling first and mooting the application, or the Court letting a brief
jurisdictional stay run). The retrieval log confirms no outside source was
consulted. It is a correct sketch, not an analysis.

## Big case

My independent read is 0.5 (formed before reading the candidate's 0.40): a life
at stake and national coverage, against a narrow, settled procedural question.
The candidate's 0.40 sits slightly below mine and rests on the same two
considerations. No agreement number is computed here.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected`
false, `retrieved_outcome_material` false. I did not rubber-stamp it: the
prediction and the resolution share the calendar day, so a date-granular check
cannot separate pre- from post-disposition retrieval. The content settles it.
The log holds only reads of the prompt, the provisioned record, and the
statpack, then the write-out; every call is `unobserved` (coverage 0.0, the
engine's standing shape), so each is graded on its query, and no query names
this application or its disposition. The prose treats the application as
pending throughout. Nothing suggests a decided case was provisioned forward:
the provisioned 2026-09-30 snapshot held only the submission entry.
