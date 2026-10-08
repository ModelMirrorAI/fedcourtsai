# Retrieval beyond the provisioned inputs

## Committed base-rate context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and the `sal-v4` segment table.
- Read corresponding fields of `metrics/statpack.json`. Pooled `baseline.prefix_est_grant_rate * baseline.prefix_weighted_resolved` over the displayed Terms 2017–2025, divided by their summed denominators: 638 / 12,720 = 0.05015723270440252.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` for artifact provenance: `808f812e9 2026-09-28T12:02:50Z`. This is not a corpus refresh timestamp.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were emitted.

## Web searches

1. `site.supremecourt.gov opinions Astra USA Santa Clara 563 110 2011 340B` — no visible results or source text returned.
2. `Astra USA Santa Clara 2011 supreme court opinion 09-1273 site.supremecourt.gov` — no visible results or source text returned.

Both targeted a historical authority, not this case or its outcome.

## CourtListener MCP

1. `search(type="o", citation="563 U.S. 110", num_results=1)` — returned an unrelated Bush v. United States tax opinion, not relied upon.
2. `search(type="o", court="scotus", case_name="Astra", filed_after="2011-01-01", filed_before="2011-12-31", num_results=2)` — returned unrelated Petrobras/Transcor Astra orders, not relied upon.
3. `search(type="o", court="scotus", q='caseName:"Astra USA"', filed_after="2011-01-01", filed_before="2011-12-31", num_results=1)` — returned an argument-participation order in the historical Astra litigation.
4. `get_more_results(query_id="0962b185", num_results=2)` — returned another version of that order and the March 29, 2011 merits opinion, Astra USA, Inc. v. Santa Clara County, 563 U.S. 110, opinion 213504.
5. `search_document(opinion_id=213504, query="uniform", snippet_size=1100)` — read two passages describing the issue and holding, centralized federal enforcement, and uniform nationwide administration. These informed the distinction between Astra's actual private-enforcement holding and the petition's proposed state-law preemption extension.

No retrieval sought this event's disposition or subsequent history. No such outcome was encountered. The related McClain denial and other litigation developments discussed in the rationale came from the provisioned petition, not additional searches.
