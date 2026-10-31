# Rationale — P(grant) = 0.004

**Inputs read:** snapshot `record/snapshots/2026-10-31.json`; `context.json` (band `baseline`, sal-v4, distribution_count 1, no CVSG, forward mode); `questions-presented.txt`, `petition.txt` (opening and QP portions), `documents.json`; `same-question.json` (empty: no petitions above the 0.5 similarity threshold, so it shows no hold candidate and no split cluster). There is no BIO because the respondent waived its response. I did not read the appendix in depth. The QP says the Fifth Circuit affirmed in a one-page unpublished "no reversible error" opinion.

**Anchor:** `cert_anchor.rate` = 5.09%, the reached rate pooled over the `baseline` band for the 10 prior Terms. The statpack's relist-0 bucket is 1.3% granted + 0.5% GVR, and that figure understates a petition that is still live. The current Term's baseline row shows reached 1.8% (n=170).

**Adjustments (all downward, and large):**
- **Pro se petitioner.** Self-represented paid petitions are granted far less often than the band's population, which includes counseled petitions.
- **Response waived, and nothing calls for one.** The Court almost never grants a petition without first calling for a response. To reach a grant, the Court would first have to call for one, and I put that at about 3%.
- **Fact-bound error correction.** QP 2 asks the Court to apply Tolan, Reeves and Anderson to the summary-judgment record. QP 1 is framed around this petitioner's facts. No circuit split is alleged in the QP.
- **Vehicle.** The decision below is an unpublished, unexplained affirmance from a single municipal employer's case.

So: P(call for response) ≈ 3%, P(grant | response called) ≈ 10–15%, which gives ~0.4%. That allows a little room for a summary Tolan-style per curiam.

**Claims:** relist-increment 0.03 (driven by the chance of a call for response; a reschedule also counts). cvsg-increment 0.002. summary-disposition-route 0.4 conditional on a grant, because the only realistic grant here is a summary reversal for error correction. dissent-from-denial 0.005.

**Uncertainty:** I did not verify the lower-court record beyond the petition's own description. Retrieval was limited to one corpus query for priors. I did not check the live supremecourt.gov docket beyond the snapshot, which is current as of today.
