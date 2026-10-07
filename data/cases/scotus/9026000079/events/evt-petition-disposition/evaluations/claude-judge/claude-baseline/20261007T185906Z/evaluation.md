# Evaluation — claude-baseline — scotus/9026000079 / evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`), forward mode. *Acosta-Tapia v. Blanche*, No. 26-79, paid petition from an unpublished Ninth Circuit memorandum; the Solicitor General waived a response on Aug 14, 2026; distributed once, for the Sept 28, 2026 long conference. **Outcome:** `denied` on Oct 5, 2026, `actual_granted` 0, one distribution, no noted dissent.

**Scores.**

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0004 | (0.02 − 0)² |
| `segment_base_rate` | 0.0501 | `risk_set` basis: the prediction froze `band: baseline` with `salience_version: sal-v4`, the statpack's segment table heading is sal-v4, so the bracketed `baseline` `reached` figures pooled resolved-weighted over Terms 2017–2025 (strictly before Term 2026; the caption renders 10 of 10 Terms, so the rendered window is the pack's window): n = 12,720 |
| `brier_skill_score` | 0.8407 | 1 − 0.0004 / (0.0501 − 0)² |
| `vote_accuracy` | omitted | cert cell; never scored |
| `semantic_grades` | none | no semantic set is declared on a cert event |
| `claim_scores` | not mine | harness-computed |

**What the prediction got right.** The disposition, the anchor, and, uniquely among the candidates, the case. It retrieved the Ninth Circuit memorandum (No. 25-2460) and so could say what the petition must be about: dismissal as untimely under 8 U.S.C. § 1252(b)(1) as construed in *Riley v. Bondi* (2025), with the 30-day clock running from the 2022 reinstated removal order, equitable tolling and non-retroactivity held forfeited, and an alternative substantial-evidence holding on withholding and CAT. From that it identified three independent vehicle defects (unpublished, forfeiture, alternative merits holding), added the dominant procedural signal (SG waiver, no call for a response), noted the absence of a visible circuit conflict, and still kept the number off the floor because the underlying timeliness question is real and recurring, with most of the residual grant mass routed through a hold-and-GVR path rather than plenary review. The anchor is the right table pooled the right way (5.0% on n = 12,720, reproducing my own pooling) with the terminal relist-0 cut explicitly declined as an anchor. The forecast of denial on the first order list of the Term with no writing is exactly what happened.

**What drove `reasoning_quality` = 0.85.** This is the only document whose discount from the band anchor rests on facts about this petition rather than on the docket skeleton alone, and each inference is stated with its evidence and its direction. The uncertainty section is specific and honest: it says where the number would move if the petition framed a conflict or if a response were called, and admits it never saw the petition. Two small deductions. The *Riley* account is accurate as far as I can check it from what the cell holds, but the candidate's reading of the memorandum is the only source for those facts and I could not verify it against the record without fetching new case facts, so I grade it as well-sourced rather than confirmed. And the hold-and-GVR weight (0.7 of grant mass) presumes a pending better vehicle that its own search did not find; that is a reasonable structural prior but is asserted more confidently than the evidence supports.

**Big case.** My own read, formed before looking at the candidate's score, is 0.08 (see `big_case.notes`). The candidate's 0.25 is higher, resting on the class-wide significance of post-*Riley* tolling to noncitizens in reinstatement proceedings; its rationale is coherent, and the panel's rank-agreement at leaderboard time is the grade, not mine.

**Leakage.** Forward cell. The prediction was written Oct 4, 2026; the denial entry is dated Oct 5, so the case was open and the forward default applies. Checked: 38 calls, all captured. CourtListener searches for the Ninth Circuit docket and for SCOTUS 26-79, two corpus `query` calls used as shape checks, a web-fetch of the live supremecourt.gov docket on Oct 4 (disclosed in `retrieval.md` as matching the snapshot with no grant, denial, relist, or response request) and of the Ninth Circuit memorandum PDF, and two web searches on the case and on *Riley v. Bondi*. The only `retrieved_doc_date` is 2025-04-16; nothing reaches the resolution date; no `data/qp-topics/` path. Lower-court material and a pre-resolution live docket read are legitimate forward signal, not leakage. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

**Flags.** None. `correct` and `brier_score` are written per their definitions knowing the harness re-stamps `correct`.
