# Retrieval log — scotus/73246321, evt-petition-disposition, claude-baseline, 20260717T180352Z

Mode: `forward` (per `record/context.json`) — unrestricted retrieval. Kept to 3
substantive lookups beyond the provisioned inputs.

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — profile of recent granted petitions for contrast with this one.
   stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`

Base rates were read from the committed `metrics/statpack.md` (modern
discretionary-cert disposition table, relist/CVSG cuts, originating-court and
per-Term tables). The statpack version in the repo carries no per-Term
salience-band table, so the relist-bucket cut served as the signal anchor.

## CourtListener MCP lookups

1. `search` (opinions, courts `ga` + `gactapp`, query `"Francis" "Allstate"`) —
   identified the underlying litigation: Court of Appeals of Georgia
   discretionary applications A25D0341 (decided 2025-05-05, the decision under
   review) and A25D0089 (2024-10-24), both *Andron Miguel Francis v. Allstate
   Insurance Co.* (A first attempt at this call failed client-side on a
   court-parameter format error and consumed no API call.)
2. `get_endpoint_item` (opinions, id 10729215) — attempted to read the
   A25D0341 ruling text; the record's text fields carry a mismatched document
   (a 2020 S.D. W. Va. federal order in an unrelated case), so it yielded no
   usable content. No further attempt made.

## Web searches

None.
