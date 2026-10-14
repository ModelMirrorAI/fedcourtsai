# claude-baseline — P(grant) 0.06, predicted denied

**Cell.** Cert stage, forward. Sara Boysen, et al. v. PeaceHealth, et al. (No. 25-1280) was denied on 2026-10-13 after two distributions, with no CVSG and no noted dissent. All three candidates forecast on 2026-09-24 from the 2026-09-23 snapshot and all predicted `denied`.

**Base rate.** The prediction froze a band (`elevated`, `sal-v4`), so the segment base rate, skill score and basis are the harness's to stamp from the risk set. I left them null and computed no rate of my own; see the stamped segment base rate.

**Leakage.** Forward mode. I checked for a mis-provisioned decided case and found none: no retrieved document is dated on or after the resolution, no query reached this petition's outcome, and nothing under `data/qp-topics/` was read. Graded `not_applicable`.

**Score.** Correct (1). Brier = 0.06² = 0.0036.

**Reasoning quality: 0.88.** A thorough and well-sourced analysis. It read the full petition and both briefs in opposition. It found the decisive fact: *Curtis v. Inslee* (No. 25-1119), the published decision applied below, was denied on 2026-06-01, along with Sweeney, Horsley and Carvalho, so every petition it proposed consolidating with had been denied. It correctly notes that the QP as framed was not the ground decided below. It also lists the uniform circuit authority, the alternative state-action and qualified-immunity grounds, and the mootness-adjacent posture (damages only, mandates rescinded). It handles the two positive signals carefully: the call for a response coming after the Curtis denial, and the NCLA amicus. It is transparent about method: an explicit anchor (the elevated risk set, OT2017–OT2024), explicit adjustments, and a candid note that the MCP surface returned nothing. The 0.06 sits a little high given its own analysis, since the case for keeping weight on the call for a response is plausible but loosely argued. That only slightly raises its Brier.

**Leakage notes.** Six CourtListener searches, all captured, all returned `count: 0`. One searched this case's caption, but it returned nothing and the prediction predates the resolution. The related-case denials come from the provisioned oppositions and predate the snapshot.
