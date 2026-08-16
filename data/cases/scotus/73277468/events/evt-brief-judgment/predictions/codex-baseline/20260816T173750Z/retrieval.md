# Retrieval beyond the provisioned inputs

- Consulted `metrics/statpack.md`, “The merits docket (granted cases),” and computed the strictly prior OT2015-OT2024 pool for an OT2025 grant: 359 disturbed of 515 parsed judgments. The available contributing rows were OT2017-OT2024.
- Retrieved the petitioner merits brief from the Supreme Court filing URL recorded in the provisioned snapshot: docket 25-352, filing dated June 8, 2026.
- Retrieved the Washington Legal Foundation amicus brief in support of neither party from the Supreme Court filing URL recorded in the provisioned snapshot: filing dated June 15, 2026.
- Retrieved the amicus brief of West Virginia and 16 other States in support of respondent from the Supreme Court filing URL recorded in the provisioned snapshot: filing dated August 10, 2026.
- Retrieved Professor Derek Muller's amicus brief in support of respondent from the Supreme Court filing URL recorded in the provisioned snapshot: filing dated August 10, 2026.
- Attempted one CourtListener MCP opinion search for `"unpleaded affirmative defense" "summary judgment" prejudice`, limited to material filed before August 3, 2026. The server returned HTTP 429 (rate limit exceeded), and no results informed the prediction.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '547 U.S. 198' --citation '371 U.S. 178' --citation '574 U.S. 10' --limit 5`. It returned no rows and emitted no `ranged corpus reads` line.
- Repeated the same query with `--corpus-backend service`. It returned no rows and emitted no `ranged corpus reads` line.
