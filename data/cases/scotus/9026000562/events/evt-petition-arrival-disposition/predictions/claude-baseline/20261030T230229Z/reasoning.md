# Reasoning — P(grant) = 0.003

**Inputs read.** I read the snapshot `record/snapshots/2026-10-29.json`. It is a paid petition, docketed 2026-10-28, with one entry ("Petition filed; response due Nov 27, 2026"). I also read `context.json` (band `baseline`, sal-v4, distribution_count 0, forward mode, `cert_anchor.rate` 0.0509) and `same-question.json` (an empty list: no similar petitions). From the documents I read `questions-presented.txt`, the petition's table of contents and authorities, and the appendix's App-1 order from the S.C. Supreme Court. None of these are OCR-derived or truncated.

**Anchor.** The frozen cert anchor is 5.1%. That is the pooled `reached` rate for the baseline band over the prior 10 Terms. The caption is private petitioners against a state court. This is an arrival cell, so the baseline floor is the right population.

**Adjustments, all downward and large:**
- **Self-represented petitioners.** Petitioner McNeil is counsel and is not counsel of record. This is a pro se paid filing, and that subgroup's grant rate is far below the paid-segment average.
- **Jurisdiction and finality.** The judgment under review (App-1) is the S.C. Supreme Court declining to take original-jurisdiction mandamus. Its reason was that the trial court had scheduled a hearing on the pending motions, and it warned the petitioners about excessive filings. That is not a final judgment that decides a federal question under § 1257. The underlying civil case (landlord/tenant-type claims against SAC 181, LLC and others) was still active in the trial court.
- **Vehicle and question.** The question is fact-bound and limited to one county. It appears to lack a split, and the petition itself argues "the question is open in this Court" instead of identifying a conflict. Generally, attorney-only e-filing with paper intake for pro se litigants is a common, facially neutral arrangement.
- **Same-question list.** It is empty, so nothing suggests a hold or a split.

I put the probability at 0.3%, about one-seventeenth of the anchor. That is in line with how pro se paid petitions of this kind resolve.

**Increments.**
- **Relist-increment (0.96).** From zero distributions, the petition will almost surely be distributed once after a waiver or after the response time runs out. The residual covers withdrawal or a docket that stalls.
- **CVSG (0.002).** A CVSG is essentially excluded.
- **Summary route given a grant (0.35).** Any grant here would be odd. A GVR or summary vacatur is a substantial share of that thin mass.
- **Dissent from denial (0.01).** Very unlikely.

**Uncertainty.** I did not read the whole petition. The skim was enough to establish the posture, and the posture is what dominates the forecast.
