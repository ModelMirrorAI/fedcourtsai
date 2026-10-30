# Why 0.15

**Inputs read:** the snapshot `2026-09-04.json`, `context.json` (forward mode; band `baseline` under sal-v4; distribution_count 1; no CVSG; Term 2026), the provisioned `questions-presented.txt`, and `petition.txt` (62 pages, not truncated). I read the petition's reasons section closely: it asks for summary reversal and, in the alternative, a GVR. No BIO was provisioned, and none was due by my cutoff.

**Anchor.** The band is `baseline`, so I anchor on its bracketed `reached` rate in the sal-v4 table, pooled over the Terms shown before OT2026. It sits around 4–6% per Term (OT2025 4.0%, n=1314; OT2024 5.9%, n=1274; OT2023 5.9%, n=1312), which pools to roughly 5%. The cross-checks agree. The paid-segment no-CVSG cut shows a 6.4% grant family. The one-amicus bucket shows 15.1% grant family (n=1162), but that is measured at disposition, so it is only a shape. Ninth Circuit petitions in the modern set run a grant family of about 3.2%.

**Adjustments up:**
- **Called-for response.** The Court asked for a response the day after the petition was first distributed. That means at least one chambers thought the petition worth a second look. No committed table conditions on this signal. From general knowledge, petitions with a called-for response grant at several times the docket rate, though most are still denied. I judge it roughly doubles to triples the baseline.
- **Posture.** The Court has repeatedly summarily reversed the Ninth Circuit in police-use-of-force and §1983 cases. The petition cites recent per curiam summary reversals on party presentation. A response request is the usual precondition for a summary reversal.
- **GVR path.** *King v. Villegas* was taken en banc and vacated. If the en banc court rules while this petition is pending, a GVR or hold-and-GVR becomes plausible.
- **Counsel and amici.** Petitioners have elite Supreme Court counsel (Garre), and a municipal-lawyers amicus brief was filed.

**Adjustments down:**
- The core holding is record-bound: what the factual basis of a no-contest plea was.
- The Rule 410(a) question may be mooted or repaired by the en banc court, which argues for denial or a hold rather than plenary review.
- The case is interlocutory: the claim was remanded for trial.

Net: about 0.15. That is above the ~5% anchor, scaled for the response request and the summary-reversal/GVR posture, and below what a CVSG or a relist would justify.

**Live docket (forward-mode retrieval).** The Court's docket page shows a brief in opposition filed Oct 5, a reply filed Oct 20, and a distribution for the 11/6/2026 conference. Both are later than my baseline, which is the normal forward shape. The page shows no disposition, so the case is still pending. I did not read the BIO or the reply. That page is where I confirmed the post-response redistribution, though that claim is masked anyway.

**Increments.** `relist-increment` is 0.97 because distribution after the response is near certain, and the harness masks it. `cvsg-increment` is 0.02. `summary-disposition-route` is 0.6, conditional on a grant. `dissent-from-denial` is 0.10, conditional on a denial.

**Uncertainty.** I can't see the en banc *King* timing or the BIO, and the response-requested uplift is my own judgement, not a committed rate. Discount me accordingly. I did not read the case summaries under `summaries/`.
