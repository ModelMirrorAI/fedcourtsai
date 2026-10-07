# Evaluation: gemini-baseline — scotus/73302615, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied on 2026-10-05 after the September 28 long conference, no noted dissent, Justice Kavanaugh not participating; `actual_granted` 0, two distributions, no CVSG.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.16 | (0.40 − 0)² |
| `segment_base_rate` | 0.172242 | elevated band, bracketed **reached** figure, sal-v4 table, Terms 2017–2024 pooled resolved-weighted: 484 / 2810 |
| `base_rate_basis` | risk_set | the prediction froze `context.band` = elevated **and** `context.salience_version` = sal-v4, matching the table heading |
| `brier_skill_score` | −4.393 | 1 − 0.16 / (0.172242)² = 1 − 0.16 / 0.029667 |
| `reasoning_quality` | 0.30 | below |
| `vote_accuracy` | omitted | cert cell, never scored |
| `judgment_correct` | null | no judgment on either side |

Base-rate window: the sal-v4 table caption says it renders all 10 Terms the pack holds, so the rendered and pack windows coincide and nothing is flagged. Strictly-prior to Term 2025 leaves 2017–2024. The cell's own `record/context.json` band is terminal and was not used.

## What the prediction got right and wrong

Right: the disposition label, and the starting point. The one-paragraph rationale correctly names the elevated reached anchor at about 17%, correctly identifies the call for a response after a waiver as a signal of interest, and correctly notes that the opposition concedes a split while calling it stale.

Wrong, or rather unargued: everything that takes the number from 17% to 40%. The uplift rests entirely on an expectation that the Court would call for the Solicitor General's views and that a CVSG implies a "higher-than-baseline probability of an eventual grant". That chain is asserted in two sentences with no engagement with the reasons it might fail. The opposition's central arguments, that the act-of-state ruling reached the court of appeals only through pendent appellate jurisdiction, that the posture is interlocutory, and that the question has been outcome-determinative almost nowhere in forty years, are not mentioned. The August 26 counsel-withdrawal letter on the docket is not mentioned. The log shows why: the candidate read the first fifty lines of the petition and then grepped both briefs for the word "split", which is the whole of its engagement with the merits of the cert question. It also says the anchor spans "the strictly prior 10 terms" when the table renders eight prior Terms; a small slip, but it suggests the table was skimmed rather than pooled.

The result is a probability more than double the anchor, held against a petition the Court denied at its first fully briefed conference without a CVSG, a relist, or a word of dissent. The disposition label was right, but the reasoning gave no grounds for the number attached to it, and the brief that answered the petition's strongest points went unread. `big_case_rationale` is null, so the stakes score is unexplained as well.

## reasoning_quality: 0.30

Correct anchor and correct identification of the two real signals, which keeps this off the floor. The uplift from 17% to 40% is a single unexamined CVSG hypothesis, with no engagement with the opposition's vehicle arguments or the counsel-withdrawal entry, and a record of reading that confirms the thinness. Graded on `reasoning.md` alone; the forecast document and the claims block were read for context only and are not scored here.

## Leakage

Mode forward; `retrieved_outcome_material` false; `influenced_prediction` not_applicable; `leakage_suspected` false. Predicted 2026-09-18, decided 2026-10-05. Every call in the log carries an `unobserved` marker (capture coverage 0.0), which is an engine's standing telemetry shape and not a defect, so each call was graded on its query: all are reads of the provisioned record, the prompts, and the committed statpack, followed by the output writes and a validate run. No web or CourtListener call at all, no `data/qp-topics/` read, nothing that could have reached this petition's disposition. Not a mis-provisioned decided case.

## Big case

My independent read, formed before reading any candidate's score, is 0.35: a genuine but narrow statutory question in foreign-expropriation litigation, interlocutory, no amici, resolved by a bare denial. The candidate's own score is recorded on its prediction; no agreement number is computed here.

## Blind

Graded from `record/blinded/gemini-baseline/` only. The alias is the only identity used anywhere in this cell's output.
