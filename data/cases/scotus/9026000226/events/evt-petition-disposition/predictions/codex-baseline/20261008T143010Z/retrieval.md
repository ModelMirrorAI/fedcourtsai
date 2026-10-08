# Retrieval record

## Local inputs and aggregate context

Read the provisioned event, context, October 8 snapshot, document manifest, QP text, petition argument, and selected appellate and district-court appendix passages. Also read the governing prompt and output schemas.

Beyond provisioned inputs, consulted `metrics/statpack.md`: modern-cert dispositions, originating circuit, paid-segment relists, CVSG, and the sal-v4 per-Term band table. Consulted `metrics/statpack.json` for exact reached-baseline rates and weighted denominators for the displayed 2017-2025 Terms. The executed pooling calculation returned 638 / 12720 = 0.05015723270440252. No target-case outcomes were retrieved from the statpack.

No `fedcourts query` or `open-events` calls were made; there are no ranged-corpus transfer lines. Path resolution was attempted with `uv run fedcourts paths --court scotus --docket 9026000226 --event evt-petition-disposition --role predictor`; the default cache was read-only. The installed CLI and then a no-cache, no-sync uv invocation resolved the same paths successfully. These were path utilities, not corpus lookups.

## Web attempts

The following calls returned no usable text in the tool responses. They did not establish facts used in the forecast; no target-case docket or disposition search was made.

1. Search queries: `site.supremecourt.gov United States Sineneng-Smith 590 371 2020 party presentation`; `site.supremecourt.gov rules Rule 10 certiorari review rarely granted erroneous factual findings misapplication`.
2. Attempted open: `https://www.supremecourt.gov/opinions/19pdf/19-67_n6io.pdf`.
3. Search queries: `site.supremecourt.gov "Margolin" "2026" "presentation"`; `site.supremecourt.gov "Clark v. Sweeney"`; `site.supremecourt.gov "2026" "Rules" "10."`.
4. Attempted open: `https://www.supremecourt.gov/opinions/25pdf/25-767_7758.pdf`.
5. Search queries: `site.supremecourt.gov/opinions/25pdf/ "Margolin"`; `site.supremecourt.gov/opinions "Sineneng-Smith" "drastic"`.
6. Two further attempted opens of `https://www.supremecourt.gov/opinions/25pdf/25-767_7758.pdf`.
7. Attempted open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

## CourtListener MCP

1. `search(type="o", q="caseName:Margolin", court="scotus", num_results=3)`: returned Margolin v. NAIJ, May 26, 2026, docket 25-767, cluster 10864190, opinion 11331634, plus two unrelated 1988 Margolin results. The latter were not pursued.
2. `read_document(opinion_id=11331634)`: retrieved the opinion; the displayed full-read response was truncated.
3. `read_document(opinion_id=11331634, chunk_size=7000, chunk_index=1)`: read the operative party-presentation discussion and disposition, including its treatment of Clark v. Sweeney and Sineneng-Smith. This verified that Margolin was a summary reversal for an unpresented theory, rather than merely accepting the petition's characterization. The precedent predates the snapshot and is distinct from this case.

No direct CourtListener REST calls, target-case subsequent history, other predictions, or realized outcomes were consulted.
