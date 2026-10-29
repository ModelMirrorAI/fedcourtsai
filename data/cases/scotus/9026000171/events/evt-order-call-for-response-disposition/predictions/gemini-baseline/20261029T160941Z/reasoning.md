# Predictor Rationale: *Galesburg Community Unit School District No. 205 v. N. T.* (No. 26-171)

## 1. Summary of the Call

- **Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.05`)
- **Conditioning State:** `mode: forward`, `stage: cert`, `moment: response-requested`, `band: baseline` (`sal-v4`), `distribution_count: 1`, `input_snapshot: 2026-09-29.json`

## 2. Base-Rate Anchoring (`metrics/statpack.md`)

In `record/context.json`, this cell is frozen in the `baseline` salience band under `salience_version: sal-v4`, in October Term `2026`, with `distribution_count: 1` and `cvsg_date: null`.

Per the cert-stage anchoring rules, I anchor on the `baseline` column's bracketed `[reached]` rate in the **"Segment base rate by salience band (`sal-v4`, paid scored segment)"** table of `metrics/statpack.md`, pooling all 10 strictly prior Terms shown (`2016` through `2025`):

- **OT 2016–2022 (7 Terms):** each Term shows `[2.9% of 3781]` (`26,467` weighted petitions reached, ~`765.3` grants).
- **OT 2023:** `[3.2% of 2167]` (~`69.3` grants).
- **OT 2024:** `[2.6% of 2289]` (~`59.5` grants).
- **OT 2025:** `[2.4% of 2088]` (~`50.1` grants).
- **Pooled 10-Term `baseline` `[reached]` anchor:** `944.2 / 33,011 = 2.86%` (~`2.9%`; across the three most recent complete Terms OT 2023–2025, `178.9 / 6,544 = 2.73%`).

For additional context from the adjacent cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall (all fee classes):** `1.6%` (`granted` `1.3%` + `gvr` `0.3%`, `n = 219,708`).
- **Originating circuit (`ca7`):** `1.5%` (`granted` `1.2%` + `gvr` `0.3%`, `n = 11,488`), virtually identical to the overall national rate.
- **Paid scored segment by relist count:** `0` relists (terminal single distribution) resolves to a grant `1.5%` of the time (`granted` `1.3%` + `gvr` `0.2%`, `n = 30,983`), while `1` relist resolves to `17.5%` (`granted` `13.7%` + `gvr` `3.8%`, `n = 1,111`).
- **Paid scored segment by amicus-brief count:** `0` amicus briefs is `0.4%` (`n = 770`), `1` amicus brief is `4.4%` (`granted` `3.5%` + `gvr` `0.9%`, `n = 342`), and `2+` is `22.9%` (`n = 689`), with a large `(unknown)` coverage gap (`n = 31,753`). While the provisioned `2026-09-29.json` snapshot records no amicus briefs, the live corpus row (`uv run fedcourts query --court scotus --docket-number 26-171`) shows a coalition of national school organizations (National School Attorneys Association, AASA, ASBO International, and CASE) entering appearance as amici.

## 3. Case-Specific Adjustments from the Anchor

### Upward Factors (+4.5 percentage points from the ~2.9% anchor)

1. **The Call for a Response (`moment: response-requested`):** Respondents waived their right to file a response on August 19, 2026 (`2026-09-29.json`), and the petition was distributed for the September 28, 2026 Long Conference. Rather than letting the petition be denied on the Long Conference order list, at least one chambers flagged it and requested a response on September 28, 2026. While the bar for a CFR is low and most called-for-response petitions are still denied once the Brief in Opposition arrives, surviving the Long Conference via a CFR after a waiver approximately doubles to triples the baseline hazard.
2. **Published Seventh Circuit Opinion and Doctrinal Framing:** The Seventh Circuit issued a published opinion (`174 F.4th 1044`, Pet. App. 1a–30a) addressing a recurring statutory question under the IDEA, 20 U.S.C. § 1415(i)(2)(C): how a district court's authority to "hear additional evidence at the request of a party" interacts with `Board of Education v. Rowley`, 458 U.S. 176, 206 (1982) ("due weight" to state administrative proceedings), and `Endrew F. v. Douglas County School District RE-1`, 580 U.S. 386, 399 (2017) (evaluating an IEP's reasonableness prospectively). Specifically, in Footnote 4 (Pet. App. 23a n.4), Chief Judge Brennan distinguished FAPE claims (reviewed prospectively as of the time the IEP was drafted) from LRE claims (which the panel characterized as "retrospective and, in some cases, prospective"), and applied the Seventh Circuit's `Alex R.` "sliding scale" (Pet. App. 14a–17a) under which admitting substantial post-hearing evidence at a bench trial reduces the deference owed to the impartial hearing officer (`IHO`).
3. **Institutional Stakes and Amicus Support:** Public school districts nationwide face recurring litigation where parents invoke the IDEA's automatic "stay-put" injunction (`20 U.S.C. § 1415(j)`) and then introduce months of post-hearing behavioral or academic developments at a district court trial to challenge an IEP placement. The appearance of national school-district organizations (NSAA, AASA, ASBO, CASE) underscores the practical concern for school administrators.

### Downward Factors (-2.4 percentage points, bringing net `probability` to `0.05`)

1. **Severe Waiver / Preservation Defect on the Core Evidentiary Issue:** As the Seventh Circuit explicitly noted in Footnote 2 of its opinion (Pet. App. 18a n.2), at the October 2024 bench trial the school district objected to *only one* expert witness's testimony, and on appeal the school district recounted that objection "without developing an argument for abuse of discretion," thereby **waiving** any challenge to the *admission* of the post-hearing evidence! Because the school district waived any challenge to the district court's decision to admit the post-hearing evidence under § 1415(i)(2)(C)(ii), it was forced to argue that the district court erred in *weighing* the evidence once admitted. Once the Brief in Opposition is filed (it is not yet in the record at this `response-requested` moment), respondents will inevitably highlight Footnote 2 as a textbook vehicle defect preventing the Court from cleanly reaching what constitutes permissible "additional evidence" under § 1415(i)(2)(C)(ii).
2. **Fact-Bound Record and Independent Pre-Hearing Grounds for Reversal:** A close reading of both the Seventh Circuit opinion (Pet. App. 25a–30a) and Judge Hawley's District Court opinion (Pet. App. 31a–49a) shows that the reversal of the hearing officer did not rest solely on post-hearing "stay-put" progress. Crucially:
   - The school district proposed removing C.T. (a 6-year-old first grader) to a completely segregated private therapeutic day school 45 minutes away in Peoria **only three weeks** after placing him in the local school's EBD classroom (Pet. App. 6a, 27a, 45a), before he had ever been educated under an IEP tailored to that classroom.
   - Contrary to testimony given to the hearing officer that no students at Silas Willard received 1:1 aides, the district court learned at trial that other students at Silas Willard *had* been provided 1:1 aides, and the school district failed to explain why C.T.'s needs differed (Pet. App. 9a, 26a–27a, 30a).
   - C.T.'s own EBD classroom teacher testified that his physical aggression was "not fundamentally different from his peers" in the EBD classroom and partly blamed his un-updated IEP for his difficulties (Pet. App. 8a–9a, 27a–28a, 39a).
   - The Seventh Circuit reviewed the district court's ultimate LRE determination for clear error under `U.S. Bank N.A. v. Village at Lakeridge, LLC`, 583 U.S. 387, 395–96 (2018) (Pet. App. 11a–13a), because the district court held a live bench trial with seven witnesses and made in-person credibility determinations.
3. **Soft Circuit Split on "Due Weight" Formulations:** While the petition (Pet. 13–24) contrasts the Fourth, Sixth, Eighth, and Tenth Circuits' "modified de novo" / "prima facie" formulations with the Seventh Circuit's `Alex R.` "sliding scale," every circuit agrees that under `Rowley` a district court must give "due weight" to the state administrative record while independently deciding based on the preponderance of the evidence after hearing any properly admitted additional evidence. Without a preserved challenge to the *admission* of post-hearing evidence, the verbal differences among circuits over how to describe "due weight" when material new evidence is admitted are unlikely to warrant plenary review.

Balancing the CFR signal and statutory framing against the Footnote 2 waiver and fact-intensive record yields a final grant probability of **`0.05` (5.0%)**.

## 4. Secondary Claims and Distributions

- **`relist-increment` (`0.98`):** The snapshot stops on September 28–29, 2026 (`distribution_count: 1`), the day the Court called for a response. Because the Clerk distributes a called-for-response petition again once the Brief in Opposition is filed (or the response time expires), at least one additional distribution past the snapshot's count of `1` is virtually certain (`0.98`), subject only to a rare voluntary dismissal under Rule 46. (As noted in the prompt, the harness masks `relist-increment` on `response-requested` cells for this reason.)
- **`cvsg-increment` (`0.04`):** Although IDEA cases occasionally draw a CVSG when the Court wants the Department of Education's view on a clean statutory split, the Footnote 2 waiver and fact-bound record make a CVSG unlikely (`0.04`).
- **`summary-disposition-route` (`0.08`):** Conditional on a grant, plenary review is far more likely (`0.92`) than a summary reversal or GVR (`0.08`), as there is no pending Supreme Court case for a hold/GVR and the standard-of-review question would require full merits treatment.
- **`dissent-from-denial` (`0.02`) and `order-writers`:** Conditional on denial, a published dissent or statement is unlikely (`0.02`) given the preservation issue in Footnote 2, with small per-Justice probabilities assigned primarily to Justices Thomas (`0.008`), Alito (`0.008`), and Gorsuch (`0.005`).

## 5. Retrieval and Upstream Notes

 All provisioned files (`2026-09-29.json`, `context.json`, `questions-presented.txt`, `petition.txt`, and `appendix.txt`) were intact and read in full. No Brief in Opposition is provisioned because the cell is at `moment: response-requested`. Two CourtListener MCP `search` calls returned HTTP 429 (`Rate limit exceeded: 1400/day`); per the prompt instructions, I fell back cleanly to the corpus tooling (`uv run fedcourts query`) and the comprehensive lower-court opinions in `appendix.txt`.
