# claude-baseline — P(grant) 0.12, predicted denied

**Cell:** scotus/73280380 (No. 25-882, *Parker v. Gates*), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` (`actual_granted` 0), resolved 2026-10-13 after three distributions, no noted dissent from denial, no CVSG.

The prediction froze `context.band` = `elevated` under `sal-v4`, so the segment base rate, `base_rate_basis` and skill score are the harness's to stamp; this write-up refers only to "the stamped segment base rate". (The decided docket's terminal band is `high`, but the frozen band governs.) The forecast document and claims block are not graded here; the harness scores the claims in code. No `semantic_grades` block: this is a cert cell.

**Leakage:** forward cell, predicted 2026-09-16, before the 9/28 long conference and the 10/13 denial. Graded `not_applicable` / `leakage_suspected` false after checking the log: no `retrieved_doc_date` on or after resolution, no query for this petition's disposition, no read of `data/qp-topics/`.

**Scores:** correct 1; Brier (0.12 − 0)² = 0.0144.

**Reasoning quality 0.85.** The strongest analysis of the three. It anchors on the frozen band, then makes the key observation: the two distributions came from a response request followed by a redistribution, not a relist after a conference. So the band's population overstates the docket signal. It takes the brief in opposition seriously. It notes that the petition does not contest the specific false statements behind the sanctions, that § 1927 has an independent basis that makes the Purcell question (QP 4) non-dispositive, that the issues are fact-bound and reviewed for abuse of discretion, and that there is no real circuit split. It also weighs the real positives: the six-judge en banc dissent, which it verified against the en banc order on CourtListener, the response request, and Bost as a GVR hook. It lands below the anchor. That direction was borne out. Small deductions: the "first word in three decades" stakes claim is asserted rather than shown, and the 0.12 call still leans somewhat on general institutional-reluctance intuition.

Retrieval: four CourtListener calls about the Ninth Circuit en banc order and possible companion petitions, all predating resolution and disclosed in retrieval.md, plus one corpus query with no rows.
