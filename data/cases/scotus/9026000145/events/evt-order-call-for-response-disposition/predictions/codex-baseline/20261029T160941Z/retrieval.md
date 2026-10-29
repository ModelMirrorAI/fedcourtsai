# Retrieval beyond provisioned inputs

## Corpus and base rates

Commands below were run with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` after the
default cache location proved read-only. No CourtListener REST calls were made.

1. `uv run fedcourts query --help` — read the structured-filter interface.
   Help was also displayed with `COLUMNS=150` and the first 48 lines selected.
   Neither invocation queried case records or printed a transfer line.
2. `uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026 --limit 4`
   — rejected locally because `modern` is not a decade token; the command
   printed the accepted vocabulary. No transfer line was printed.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   — returned U.S. DOGE Service v. U.S. District Court (25-1103), Corey Duran
   Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba
   (25-1343). The bare-year filter screens by derived Term, so these prior-Term
   rows can contain grants dated in calendar 2026. No opinion bodies were
   requested. This grant-selected sample did not establish a matched base rate.

   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

4. `uv run fedcourts query --court scotus --docket-number 25-1223 --limit 1`
   — read the lead case expressly identified in the provisioned petition:
   Kevin Isaac Montoya Palacios v. Vernon Liggins. The row returned certiorari
   granted June 29, 2026, with no recorded merits judgment or termination,
   originating in the Fourth Circuit. Its pull stamp is July 9 and live-poll
   stamp October 28, 2026. This is a related case, not this petition's disposition.

   `ranged corpus reads: 9 GET(s), 2359296 byte(s)`

5. Read the committed `metrics/statpack.md`: modern discretionary-cert section;
   paid-segment relist, CVSG, amicus and adjacent signal tables; and the sal-v4
   reached-band table. Read `metrics/statpack.json` for its keys, a sample Term's
   segment structure, and exact pooling inputs. A local, read-only calculation
   through `uv run python` pooled every OT2017-OT2025 segment's
   `prefix_weighted_resolved` and grant-rate-weighted numerator, yielding
   baseline 660 / 12,913 and federal 151 / 206. No own-case outcome or underlying
   corpus records were opened by this calculation. No transfer lines apply to
   these committed-file reads.

## Web and CourtListener

6. Web search: `site.supremecourt.gov "Montoya Palacios" "Liggins"` — no
   results returned. This sought only the lead case already named in the
   petition, not this case's disposition. No web text contributed to the call.
7. CourtListener MCP `search`, type `o`, case name `Ardestani v. INS`, citation
   `502 U.S. 129`, limit 2, fields `caseName`, `dateFiled`, `citation`,
   `opinions`, `absolute_url` — failed with HTTP 429, daily rate limit exceeded,
   reporting availability in 6,248 seconds. No opinion text or search results
   were obtained; no direct REST fallback was attempted.

## Local setup and checks

The initial `uv run fedcourts paths --court scotus --docket 9026000145 --event evt-order-call-for-response-disposition --role predictor`
failed before execution because the default uv cache was read-only. Repeating
it with the temporary cache resolved the case and event paths without reading
an outcome. Local instruction, schema, path and serialization implementation
reads were contract/setup work, not substantive case retrieval. Final schema
and repository validation use the same cache override.
