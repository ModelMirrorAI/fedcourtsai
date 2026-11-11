# Evaluation: gemini-baseline

## Outcome and scoring

This is a cert-stage CVSG-disposition cell. The authoritative outcome is `gvr` on November 9, 2026, with `actual_granted = 1`. The staged docket specifies reconsideration in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. The predicted label `granted` is not an exact match: **correct = 0**. The binary Brier score is **(0.70 - 1)^2 = 0.09**; a GVR counts as a grant on that axis. Cert votes are not scored. No semantic-grades block applies.

## Rationale quality

**Reasoning quality: 0.35.** The rationale recognizes the CVSG, competing scrutiny standards and multistate support as legitimate signals of attention. But it calls this a clean, mature split without engaging the opposition's party-presentation objection, the petitioners' acceptance of intermediate scrutiny below, or the pleading-stage limits. The staged opposition, printed pages 6–8, identifies those constraints. An assessment of the Court's ideological composition does not adequately justify nearly doubling the reference probability or establish that plenary review is the appropriate route. The rationale omits the intervening-precedent/GVR mechanism that actually resolved the petition. This is a critique of the rationale's support, not a penalty for the forecast document or a reward for its relatively good binary score.

The prediction-time statpack was reconstructed with `statpack-at`: build `73762050f49cd68912e89c864e25a792e498b45a`, digest `sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, landed September 14, 2026. Its CVSG table supports the candidate's descriptive figures. The methodological weakness is using a pack-wide CVSG cut without the frozen high-band, strictly-prior-Term risk-set check, not a discrepancy with today's pack. The scored comparison belongs to the stamped segment base rate; no evaluator-computed replacement is supplied.

## Predicted reasoning

**Forecast quality: 0.20.** The document's main discriminating commitment is plenary review of both questions rather than a GVR, and that failed. Its further-distribution forecast held, but the docket added only one distribution, not the additional subsequent relist it anticipated. The conditional denial-writing forecast is unresolved and receives neither credit nor penalty. The November 9 order does not establish how the Court would have ruled after plenary argument.

## Leakage

The captured log records forward mode and a September 18 prediction, before the November 9 resolution. It includes current-docket and circuit-authority queries, but every result is `unobserved`; this is not evidence of failed or empty retrieval. No query or staged prose shows the petition's own disposition already known. Thus influence is `not_applicable` and leakage is not suspected, while the retrieval boolean remains null because the actual returns cannot be inspected. The absent predictor flags channel is not treated as evidence of cleanliness. No provisioning blocker prevents grading.
