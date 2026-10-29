# Retrieval record

No lookup sought this petition's disposition, subsequent history, a current docket page, another prediction, or labeling artifacts. The baseline and staged filings, including the explicitly dated October 13 Walmart response, are provisioned inputs. Repository instructions, schemas, the CLI help, and serialization helpers were read to implement the contract.

## Corpus and committed context

- Attempted `uv run fedcourts paths --court scotus --docket 73538544 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help`. Both initially failed because the default uv cache was on a read-only filesystem. Neither returned corpus material.
- Repeated both commands with `UV_CACHE_DIR=/tmp/uv-cache`. Path resolution and query help succeeded. The paths command did not expose a realized outcome.
- Consulted `metrics/statpack.md` for the cert, relist, CVSG, amicus, and salience-band sections. Read the corresponding baseline segments in `metrics/statpack.json` and calculated the strictly-prior 2017–2024 pool with jq: 607 / 11,599 = 0.05233209759462023. No fresh aggregate corpus query was used to generate that figure.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2025 --limit 4`. Returned `scotus/72483572` (24-1097), `scotus/72483573` (24-1098), `scotus/72484159` (24-449), and `scotus/72483574` (24-1099), all labeled GVR and all without a stored opinion body. The tool response was display-truncated, including the transfer-line area, so its first-call transfer figures were not retained; no estimate is substituted for them.
- Repeated that exact query with stdout projected through `jq -c '{case_id,case_name,docket_number,disposition,distribution_count,has_opinion}'` to retain a compact, readable result and stderr. It returned the same four rows. The emitted line was exactly:

  `ranged corpus reads: 24 GET(s), 6291456 byte(s)`

These were broad, filtered procedural priors, not an outcome search for this cell or a close-comparator sample. No `--full` hydration was attempted. `DECIDED_BEFORE` was unset; the explicit query bound was conservative and masks by docket-derived year, not exact decision date.

## Web and CourtListener attempts

1. Web search: `site.supremecourt.gov opinions 2025 Montgomery Caribe Transport safety exception 2026`. No usable result or source text was returned.
2. Web open: `https://www.supremecourt.gov/opinions/25pdf/24-1238_1b7d.pdf`. This speculative opinion locator returned no usable content and was not relied on.
3. Batched web searches: `"Montgomery v. Caribe Transport" "2026" Supreme Court` and `site.supremecourt.gov "Lawrence" "Chater" "516"`. No usable result or source text was returned.
4. Repeated web open of the same speculative locator. Again no usable content; not relied on.
5. CourtListener MCP `search(type="o", case_name="Montgomery v. Caribe", num_results=3)`: HTTP 429, daily rate limit exceeded; the response estimated availability in 2,437 seconds. No opinion was obtained, no wait was attempted, and no direct REST fallback was used.

The legal and factual analysis rests on the provisioned filings, not any of these failed external lookups. No outcome-revealing material surfaced.

## Independent critique

One read-only subagent reviewed the same provisioned record and cert-stage contract, with no external retrieval or edits. It favored GVR, confirmed Irigoyen's actual Q2-grant request and Walmart's October 13 GVR request, and identified different supply-chain roles and unresolved state-law defenses as the strongest reasons to retain denial probability. It did not consult outcomes or other cells.
