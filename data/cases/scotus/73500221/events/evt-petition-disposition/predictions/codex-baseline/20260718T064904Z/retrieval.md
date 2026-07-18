# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36%). The current statpack did not contain the salience-band table referenced by the prediction prompt.

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
  - Returned ten recent grant-side priors. I used them only as qualitative docket-signal context; they were not close legal analogues.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 40 | jq -c 'select(.originating_court == "ca10")' | head -10`
  - `ranged corpus reads: 150 GET(s), 39321600 byte(s)`
  - Returned no Tenth Circuit row after the local filter.

## CourtListener MCP lookups

- Opinion search for `Knick takings claim preclusion state court merits exhaustion`, restricted to SCOTUS and the Tenth Circuit and filed before July 18, 2026. It returned *Sanchez v. Torrez*, No. 25-2009 (10th Cir. Apr. 21, 2026); I did not retrieve its full text or rely on it as a close analogue.
- The same opinion search restricted to the Tenth Circuit, used to obtain compact metadata for the single result above.
- Opinion search for Tenth Circuit docket number `25-5039`, filed before July 18, 2026. No result.
- Opinion search for `"Rogne" "Catoosa"` in the Tenth Circuit, filed before July 18, 2026. No result.

No web searches were used.
