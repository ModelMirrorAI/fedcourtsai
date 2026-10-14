# Retrieval log

## Provisioned inputs

Read the event, October 13, 2026 snapshot, context, document manifest, questions presented, and substantive excerpts from the petition (including appended opinions), opposition, and reply. These are provisioned inputs, not external retrieval. No petition outcome, other predictor output, or labeling-measurement artifact was read.

## Committed base rates

- Read the modern-cert, paid-segment relist/CVSG, and sal-v4 segment sections in `metrics/statpack.md`.
- Read `metrics/statpack.json` to pool the state band's exact reached rates over displayed Terms 2017–2025. Result: weighted grant-family numerator 99, weighted resolved denominator 421, rate 0.23515439429928742. No 2026 row entered the pool.
- `git log -1 --format='%cs %h' -- metrics/statpack.md` returned `2026-10-12 ea0a1e70a`. This identifies the artifact commit, not underlying corpus refresh dates.
- No `fedcourts query` or `open-events` call was made; no ranged-corpus transfer line was produced.

## Web attempts: general historical precedent only

The following `web.run` operations returned no usable result content:

1. Search queries `site.ca11.uscourts.gov "McClendon" "1330"` and `site.supremecourt.gov "2018" "Becerra" "uncontroversial"`.
2. Search queries `McClendon Long 22 F.4th 1330 opinion 2022` and `site.supremecourt.gov opinions 16-1140 Becerra`.
3. Open `https://media.ca11.uscourts.gov/opinions/pub/files/202110092.pdf`.
4. Find `factual` against that same historical opinion URL.

No substantive conclusion rests on these unsuccessful calls. None searched Hanaway v. Sanderson or its disposition.

## CourtListener MCP

`search(type="o", citation="22 F.4th 1330", num_results=2)` returned one match: Corey McClendon v. Gary Long, Eleventh Circuit, January 19, 2022, docket 21-10092, cluster 6237698, opinion 6104580. The response supplied identifying metadata and a caption snippet, not substantive opinion text. It confirmed the historical citation; the treatment of its holding in this forecast comes from the provisioned petition, opposition, and appended appellate opinion.

## Local contract checks

Read repository instructions and output schemas. The initial `uv run fedcourts paths --court scotus --docket 9026000034 --event evt-petition-disposition --role predictor` failed because the default cache was read-only; repeating with a temporary writable cache succeeded. No CourtListener REST fallback or credential access was attempted.
