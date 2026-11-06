# Forecast rationale

P(any grant) = **0.87**; predicted disposition: **granted**, ordinarily for plenary review.

## Conditioning record and anchor

I read the event definition, `record/snapshots/2026-09-21.json`, `record/context.json`, and `record/same-question.json`. This is a forward, cert-arrival cell. The baseline contains **zero distributions**, no CVSG, and no amicus-brief entry. Its September 22 cutoff bounds the baseline, not forward retrieval. `paper_only_filings: true` explains the absent staged documents; that is not a provisioning failure. The same-question list is null, not evidence that no similar litigation exists.

The official-capacity federal petitioners and Solicitor General as counsel support the frozen `federal` band, sal-v7. I anchor on the harness-frozen **0.7311320754716981**, not the whole cert docket's much lower rate. The prior-Term federal rows displayed in `metrics/statpack.md`, OT2017–OT2025, have denominators totaling 212; their rounded rates imply approximately 155 grants, or 73.1%. I exclude OT2026. The frozen anchor is authoritative; rounding the table is only a cross-check. Neither counsel's identity nor the caption earns a second upward adjustment: the band already incorporates that selection.

## Case-specific adjustment

DOJ's September 21 petition seeks certiorari **before judgment**, proposing this as a replacement for the moot granted case, *Black v. D.C.* [R1]. Its question concerns 8 U.S.C. 1252(g), other jurisdictional provisions, and judicial interference with discretionary immigration enforcement. The Court's own *Black* docket independently confirms the June 15 grant and September 15 vacatur/remand [R2]. Those earlier companion events are legitimate pre-baseline evidence, not this petition's outcome.

My inference is that demonstrated interest in substantially the same dispute is considerably stronger than an ordinary assertion of importance. I move roughly fourteen percentage points above the federal anchor, rather than treating the case as a generic new government petition. Conversely, an unfinished appeal and possible vehicle or mootness problems leave meaningful room for refusal or delay. No Second Circuit opinion was returned by the targeted MCP lookup [R3]; I cannot independently assess preservation or the underlying factual record. I do not infer their contents from that absence. The petition is advocacy; its characterizations are not independent findings. I verified the decisive prior-case procedural dates, not every allegation or authority it cites.

## Other probabilities

- **Further distribution: 0.98.** From zero, this asks whether an initial distribution occurs, not whether an already-considered petition is genuinely relisted. An early withdrawal or dismissal is the main residual risk. My central path is one initial distribution, with at most one or two additional distributions before disposition.
- **New CVSG: 0.001.** The Solicitor General already represents petitioners; an invitation to obtain the government's otherwise-missing position has little purpose here.
- **Summary route conditional on grant: 0.03.** I expect briefing and argument, not an immediate merits judgment or reconsideration remand. This is conditional, not 3% multiplied by the grant probability.
- **Writing conditional on denial: 0.10.** Refusal remains more likely to produce a bare order than an explanatory statement. The independent per-Justice writing probabilities are unconditional and small; they also allow writings accompanying non-denial orders. They are not a forecast of cert votes.

For procedural calibration I read the paid-segment terminal relist buckets: 0 (resolved n=10,204), 1 (n=2,532), 2 (n=495), and 3+ (n=482), and CVSG buckets none (n=13,549) and CVSG (n=164). These are terminal populations, not the forward hazard from this arrival state. In particular, the zero-relist terminal grant rate is not this cell's arrival anchor. I also inspected the amicus cut: zero briefs (resolved n=11,109), one (n=1,158), and two-plus (n=1,446). The present lack of amicus entries at arrival is weak evidence because the count can rise; I apply no separate amicus adjustment.

The 0.85 stakes score is distinct from the 0.87 grant forecast. It reflects potential institutional and practical reach, not a predicted merits winner.

## Limitations and conduct

The snapshot abbreviates the filing as an ordinary petition and does not expose the before-judgment posture identified in the retrieved filing; I record that material input discrepancy in `flags.json`. The default uv cache was read-only; setting a temporary cache and disabling dependency synchronization restored the CLI without installing anything. I sought no disposition or subsequent history of this petition and encountered none. A search surfaced a fedcourts.ai case-page snippet; I did not open it or use it as another predictor's forecast. Sources and every external lookup are recorded in `retrieval.md`.
