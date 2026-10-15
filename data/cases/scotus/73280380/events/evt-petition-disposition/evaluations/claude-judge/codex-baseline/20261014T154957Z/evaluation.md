# codex-baseline — P(grant) 0.28, predicted denied

**Cell:** scotus/73280380 (No. 25-882, *Parker v. Gates*), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` (`actual_granted` 0), resolved 2026-10-13 after three distributions, no noted dissent from denial, no CVSG.

The prediction froze `context.band` = `elevated` under `sal-v4`, so the segment base rate, `base_rate_basis` and skill score are the harness's to stamp; this write-up refers only to "the stamped segment base rate". (The decided docket's terminal band is `high`, but the frozen band governs.) The forecast document and claims block are not graded here; the harness scores the claims in code. No `semantic_grades` block: this is a cert cell.

**Leakage:** forward cell, predicted 2026-09-16, before the 9/28 long conference and the 10/13 denial. Graded `not_applicable` / `leakage_suspected` false after checking the log: no `retrieved_doc_date` on or after resolution, no query for this petition's disposition, no read of `data/qp-topics/`.

**Scores:** correct 1; Brier (0.28 − 0)² = 0.0784.

**Reasoning quality 0.70.** A careful, well-documented analysis. It reads the petition and the brief in opposition in substance, with page cites. It correctly declines to treat the two distributions as a merits relist because a response request intervened. It pins down the main crux: whether Bost undermines the actual grounds for the sanctions, given the opposition's argument (p. 17) that the sanctions rested on misleading factual assertions independent of standing. It is honest about its retrieval limits. Its weakness is calibration. Having laid out why the opposition's independent-grounds argument limits the Bost hook and why there is no clean split, it still moves 11 points above the anchor, mostly on the response request and the circuit dissent. Its own analysis pointed lower. Its retrieval (two web searches and an attempted URL about Bost, plus a CourtListener search that hit HTTP 429) concerned a public precedent from January 2026, not this case's outcome, and is fully disclosed.
