# Retrieval log

- Read the committed `metrics/statpack.md` modern-cert, paid-segment relist/CVSG, and salience-band sections, plus `metrics/statpack.json` prior-Term baseline reached fields. Used local `jq` arithmetic to pool 2017–2024: 593 weighted grant-family outcomes / 11,580 weighted resolved petitions. No live corpus lookup was performed and no ranged-read transfer line was produced.
- Checked artifact commit vintage with `git log -1 --format='%cI %h' -- metrics/statpack.json`: October 13, 2026, cf9ae960e. This is not a corpus pull timestamp.
- Attempted `web.run` searches for `site.supremecourt.gov opinions Erlinger United States 2024 23-370` and `site.supremecourt.gov Rule 10 considerations governing review certiorari`. No usable results were returned to this session; no factual inference rests on these attempts.
- Attempted `web.run` open of `https://www.supremecourt.gov/opinions/23pdf/23-370_8o6a.pdf`. No usable content was returned; this attempted address was not verified as a valid opinion location.
- CourtListener MCP `search`: type `o`, case_name `Erlinger v. United States`, filed_before `2024-07-01`, court `scotus`, num_results `2`. Returned the June 21, 2024 decision, 602 U.S. 821, including opinion 11066653. Used the decision's identity and date; did not treat dynamic citation counts as predictive evidence.
- CourtListener MCP `search_document`: opinion_id `11066653`, query `We hold`, snippet_size `900`. No matches.
- CourtListener MCP `search_document`: opinion_id `11066653`, query `occasions`, snippet_size `300`. Read the returned excerpts describing the ACCA separate-occasions jury-finding holding. This is general preexisting legal context, not material about Mizrahi's disposition.

No target-case live lookup, corpus query, outcome file, or labeling artifact was consulted. Local contract/schema/path/serialization inspection was operational, not additional case evidence.
