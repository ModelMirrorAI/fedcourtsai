# gemini-baseline — P(grant) 0.02, predicted denied

**Cell.** Cert stage, forward. Sara Boysen, et al. v. PeaceHealth, et al. (No. 25-1280) was denied on 2026-10-13 after two distributions, with no CVSG and no noted dissent. All three candidates forecast on 2026-09-24 from the 2026-09-23 snapshot and all predicted `denied`.

**Base rate.** The prediction froze a band (`elevated`, `sal-v4`), so the segment base rate, skill score and basis are the harness's to stamp from the risk set. I left them null and computed no rate of my own; see the stamped segment base rate.

**Leakage.** Forward mode. I checked for a mis-provisioned decided case and found none: no retrieved document is dated on or after the resolution, no query reached this petition's outcome, and nothing under `data/qp-topics/` was read. Graded `not_applicable`.

**Score.** Correct (1). Brier = 0.02² = 0.0004.

**Reasoning quality: 0.55.** The direction is right, and so are the main points: there is no circuit split, the decision below is unpublished, and the Court has repeatedly denied vaccine-mandate petitions. Bridges and the other cited denials match what the briefs in opposition report. But the analysis is thin. It read only the head of the petition and the opposition, and it misses the most decisive fact in the record: the Court denied *Curtis v. Inslee* on 2026-06-01, the published Ninth Circuit decision applied below, with the same counsel and the same defendants. It also says the Ninth Circuit held that Jacobson forecloses the "investigational drug" claim. In fact the panel decided on the complaint's own pleading that the product was an authorized vaccine, and the QP's framing was not reached; this misreads the vehicle. It names none of the vehicle problems (state action, qualified immunity, a damages-only suit over repealed mandates). It cites "~17%" for the band, which roughly matches the risk-set anchor, but it never works through why the number falls so far below it. Its treatment of the call for a response is reasonable but brief.

**Leakage notes.** Every call is `unobserved` (coverage 0.0), so each was graded on its query. They are provisioned-file reads, the statpack, and one generic `fedcourts query`. No web or MCP calls.
