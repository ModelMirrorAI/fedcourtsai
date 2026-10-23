# Retrieval record

- Read committed `metrics/statpack.md` and the `terms` portion of `metrics/statpack.json` for the sal-v4 baseline reached risk sets across Terms 2017–2025 and the paid-segment relist/CVSG cuts. A local `jq` calculation returned 644 estimated grants / 12,883 weighted resolved = 0.04998835674920438. No live corpus lookup was made and no ranged-transfer line was produced.
- Attempted web search: `site.supremecourt.gov opinions 2010 Astra USA Santa Clara 563 110 09-1273`. The web tool returned no usable result content.
- Attempted web open of the official Supreme Court opinion PDF for docket 09-1273, `opinions/10pdf/09-1273.pdf`. The web tool returned no usable content. Neither web request concerned the target petition's outcome.
- CourtListener MCP `search(type="o", citation="563 U.S. 110", num_results=1)`, query id `e84917cf`: returned an unrelated *Bush v. United States* opinion, not relied upon.
- CourtListener MCP `search(type="o", court="scotus", case_name="Astra USA", filed_before="2012-01-01", num_results=2)`, query id `4b4f42df`: identified *Astra USA, Inc. v. Santa Clara County*, March 29, 2011, 563 U.S. 110, opinion id 213504, plus an ancillary argument-participation order. The ancillary order was not used.
- CourtListener MCP `read_document(opinion_id=213504)`: read the 2011 opinion concerning third-party-beneficiary enforcement of 340B pricing agreements; used to distinguish its holding from the state-preemption question presented here.
- No `fedcourts query` or `open-events` calls; no retrieval of this case's outcome, subsequent history, or other predictors' forecasts.
