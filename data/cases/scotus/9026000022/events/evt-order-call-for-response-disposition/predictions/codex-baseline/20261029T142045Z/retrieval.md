# Retrieval record

## Provisioned inputs and local references

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling schemas, this event definition, `record/context.json`, `record/snapshots/2026-08-27.json`, and the provisioned `documents.json`, questions-presented text and petition. No other cell's output, realized outcome, or topic-label artifact was read. The petition's 1992 cert denial is historical appendix material, not this event's disposition.

Read the cert sections of `metrics/statpack.md` and corresponding `metrics/statpack.json` Term/band fields. Computed the strictly-prior state reached-band anchor for 2017–2025: 104/426 = 0.2441314554. This is a committed aggregate reference with no pull-vintage assertion. Also inspected local paths/serialization APIs and validation help to produce conforming output.

## CLI calls

- `uv run fedcourts paths --court scotus --docket 9026000022 --event evt-order-call-for-response-disposition --role predictor`: failed before execution because the default uv cache was read-only. No corpus read or transfer line.
- `uv run fedcourts query --help`: same cache initialization failure; no query executed and no transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000022 --event evt-order-call-for-response-disposition --role predictor`: succeeded, resolved case/event paths; no outcome read.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`: succeeded. Repeated once with output piped to `tail -85` to inspect the options. Help calls made no corpus lookup.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026 --limit 3`: succeeded; returned Burford German Funding (25-1269), Roofing Designs by JR (25-1367), and Silva Ochoa (25-7569), all unrelated GVR rows without opinion bodies. The integer clock filters by derived year, not resolution day, so the returned 2026 grant dates are not inconsistent with the command. Forward mode permits these unrelated priors; none was used as a substantive analogue or to estimate a rate. Transfer line: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate --help`: succeeded; local command documentation only.

## Web attempts

Each call returned no readable results or source text. No legal assertion in this forecast relies on a retrieved web page.

1. Search: `site.supremecourt.gov Horne Flores 557 433 Rule 60(b)(5) changed circumstances`.
2. Search in the same call: `site.supremecourt.gov Agostini Felton 521 203 Rule 60(b)(5) injunction`.
3. Search: `Horne v Flores 557 U.S. 433 2009 Rule 60 site:loc.gov`.
4. Search in the same call: `United States v Munsingwear 340 U.S. 36 site:loc.gov`.
5. Direct open of the Library of Congress official U.S. Reports PDF for Horne: `https://tile.loc.gov/storage-services/service/ll/usrep/usrep557/usrep557433/usrep557433.pdf`; no readable response.

## CourtListener MCP attempt

`search(type="o", citation="557 U.S. 433", num_results=1)` for Horne v. Flores: refused with HTTP 429, daily quota exhausted. No opinion was returned. No REST fallback was attempted.

## Independent assessment

A read-only subagent assessed only the provisioned petition, QP, snapshot, and context, with an explicit prohibition on outcome retrieval or other cells' outputs. It identified the independent repeal/mootness barrier, absence of a demonstrated circuit split, VanDyke's express agreement with dismissal, and potential summary-vacatur limitations. I checked the cited appendix passages before using those points. No separate external retrieval was reported.
