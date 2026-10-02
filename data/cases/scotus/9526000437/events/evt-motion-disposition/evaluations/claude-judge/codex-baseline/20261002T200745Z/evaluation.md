# Evaluation: codex-baseline — In re Nikolay M. Valov, 26A437 (evt-motion-disposition)

**Stage: interim** (an application for an injunction pending appeal, submitted to the Chief Justice). Outcome: `denied`, `actual_granted` 0, entered 2026-10-01 by the Chief Justice alone — no response requested, no referral, no amici.

## Scores

- `correct` = 1: predicted `denied`, outcome `denied`.
- `brier_score` = (0.04 − 0)² = 0.0016.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: not written. Interim cell; the harness pools the statpack's interim section over application-Terms strictly before 2026 and writes both. For the reader: the committed rows for 2016–2025 carry 31 grants over 296 resolved substantive applications (2025: 17/226; 2024: 14/70; earlier Terms unparsed), above the 50 floor, so a stamped rate near 0.105 is expected; a null would mean the pack changed.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`, `claim_scores`: omitted — not an interim cell's fields (no `semantic_claims` block and no votes on the prediction in any case).
- `big_case.evaluator_score` = 0.02: pro se application to preserve possession of one house pending a Virginia mandamus petition arising from a partition sale and a contempt eviction sanction; purely private stakes, denied in chambers in three days. The candidate left its own `big_case_score` null, so there was nothing to anchor on; my read rests on the OCR'd application text the candidate could not see.

## What the record now shows that the candidate could not

Every predictor in this run saw `application.txt` as empty (`empty_text: true`, a 73-page scan). The record has since been re-fetched with OCR. The application is an All Writs Act request to preserve possession of 3831 Elbert Avenue while Supreme Court of Virginia Record No. 260843 (a mandamus/prohibition petition, already under a show-cause order toward dismissal) is pending, with a parallel emergency request in the Court of Appeals of Virginia; it asserts due-process and Fourth Amendment questions around a civil-contempt eviction sanction and concedes there is no reviewable final state judgment.

## Reasoning quality: 0.72

The document is careful and honest about its evidence. The anchor is located, computed (31/296 = 10.47%), and caveated correctly, including the coverage unevenness and the selection difference between the pooled cohort and predicted cells, and the candidate says plainly that it did not query the corpus. It notes the unreadable application and treats that as content-unavailable rather than as absent, which is right. Its refusal to infer a jurisdictional defect from the docket's listing of a trial court alone — "a listed trial court does not prove that state appellate remedies were omitted" — turned out to be factually correct: the applicant had gone to both Virginia appellate courts. The increments are labelled as subjective forecasts rather than measured rates, and the timing forecast is labelled unscored.

Where it is weaker: the adjustment stops too early. The candidate reasons that missing text is "not affirmative proof that the applicant failed those requirements" and keeps 4% for a compelling showing in the unreadable material. That misreads where the probability mass lives. For a pro se applicant seeking an injunction — not a stay — against a state-court matter, the Circuit Justice's in-chambers denial rate is close to one regardless of the application's quality, because the indisputably-clear-right standard and the absence of a final state judgment are posture facts the docket shell already disclosed, not content facts a better brief could cure. The candidate had the pack's escalation columns and a corpus query available to test the applicant-class prior and used neither, so its 10% response and 20% referral increments sit well above what the comparable denied shape supports (claude-baseline's corpus pull shows none of that shape drew a response or referral). The epistemic humility is a virtue on an unread record; applied uniformly to every number here it left the forecast less sharp than the record allowed. Two web searches for general legal context returned nothing and are reported as such.

## Leakage: forward, `not_applicable`, `leakage_suspected` false

`result_capture_coverage` 0.91; the two uncaptured calls are web searches whose queries are general legal context (a search on the "indisputably clear" / Turner standard restricted to the Court's site, and a Justia URL for 507 U.S. 1301), neither naming this applicant or case, so they are graded on their queries and cannot have carried this case's disposition. Every other call is a captured local read of the provisioned inputs, the prompt, the schemas, or the statpack. No CourtListener or corpus calls. `retrieved_outcome_material` false. The prediction was created 2026-10-01T21:59Z, the date the denial was entered, but no call here could have reached the Court's docket page.
