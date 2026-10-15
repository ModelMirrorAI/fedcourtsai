# Reasoning: P(grant) = 0.005

**Inputs read.** I read the snapshot `2026-10-15.json`, `context.json` (forward mode, band `baseline` under `sal-v4`, distribution_count 1, no CVSG, Term 2026), the questions-presented file, the petition (38 pp.) and the appendix (the Sixth Circuit opinion and the district court's summary-judgment opinion). No brief in opposition exists, because the respondents filed a waiver on Oct 9, 2026.

**Anchor.** The statpack's "Segment base rate by salience band (sal-v4)" table gives the `baseline` band's bracketed *reached* rate for Terms before 2026. Pooled over 2017–2025, it runs 3.9%–5.9% per Term, about 5% overall. That rate covers every paid petition, including ones that later relist or draw a CVSG, so it is a ceiling for a petition in this one's position rather than a point estimate. The terminal (non-reached) baseline rate is about 0.6%–1.8%. The whole-docket `baseline` row reads granted 0.8% and GVR 0.4%. The Sixth Circuit's originating-court row (granted 3.5%) is the unselected population and adds little.

**Adjustments down, all strong.**
- **Waiver of response.** The respondents waived, and the Court has not called for a response. The Court almost never grants a paid petition without first calling for a response, and a waiver signals that the respondents' counsel sees no cert risk.
- **The questions presented are not cert questions.** All five are phrased as "whether certiorari is warranted where the decision … conflicts with well-established principles." That is a request for error correction across five doctrines. The petition does not plead a circuit split on any of them.
- **Vehicle problems.** The case went up on summary judgment, with qualified immunity and Monell grounds that are independently sufficient. The petition claims jurisdiction under 28 U.S.C. § 1257(a), the state-court provision, when review of a court of appeals runs through § 1254(1). On ripeness it relies on *Williamson County*, which *Knick* (2019) overruled. Both signal a petition the Court will not see as a serious vehicle.
- **The opinion below is published but fact-bound.** The panel (Griffin, Larsen, Readler) was sympathetic in tone about municipal bureaucracy but rested on Monell and qualified-immunity grounds, not on any new rule.

**Why 0.5% and not lower.** The baseline-band floor for denied-at-first-conference paid petitions is still not literally zero, and there is a small chance of an unexpected call for a response. I hold 0.005.

**Increments.** relist-increment 0.05 is the chance of a call for a response followed by redistribution. cvsg-increment 0.002 reflects that no federal interest is present. summary-disposition-route 0.2 is conditional on a grant and reflects the lack of any intervening decision, so a grant would most likely be plenary on a reframed question. dissent-from-denial 0.01.

**Uncertainty.** I did not read the full 89-page appendix closely, only the opening of the panel opinion and grep hits for Monell and qualified immunity. I made no CourtListener or corpus retrieval because the provisioned record was decisive for a petition this weak.
