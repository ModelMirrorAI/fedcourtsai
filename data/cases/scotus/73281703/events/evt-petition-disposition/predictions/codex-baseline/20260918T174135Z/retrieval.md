# Retrieval beyond the provisioned record

## Local aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition counts, paid-segment relist and CVSG cuts, and the `sal-v4` segment table. An initial heading search also surfaced other aggregate section headings and rows; interim and merits aggregates were not used for this cert forecast.
- Inspected `metrics/statpack.json` for timestamp-related metadata and top-level keys only. No build/pull timestamp was found in that inspection.
- Executed a local Python calculation parsing only the displayed elevated reached rows for Terms 2017–2024: denominator 2,810 and approximate rate 0.1723793594 from rounded percentages.
- No `fedcourts query` or `open-events` lookup was made, no corpus blob was opened, and there was no `ranged corpus reads` transfer line.

## General web attempts

1. Search query: `site.ca5.uscourts.gov "Flynn" "15-50314"`.
2. Search query, same call: `site.supremecourt.gov "Rule 10" "state court of last resort"`.
3. Open attempted: `https://www.ca5.uscourts.gov/opinions/pub/15/15-50314-CV0.pdf`.

The search and open tool responses contained no usable results or document text. No factual assertion is attributed to those unsuccessful attempts; neither search named this cell's case.

## CourtListener MCP historical authorities

1. `search(type="o", citation="812 F.3d 422", num_results=1)` returned Flynn v. Distinctive Home Care, Inc., dated February 1, 2016, opinion 3173961. Read the returned holding snippet allowing independent-contractor employment-discrimination suits under section 504.
2. `search_document(opinion_id=3173961, query="retaliation", snippet_size=800)` returned two passages discussing Hiler and related authorities. Used the qualification that Hiler did not itself involve an independent contractor.
3. `search(type="o", citation="232 F.3d 933", num_results=1)` returned an unrelated first hit, Robert Cordaro v. United States, 933 F.3d 232. Disregarded it; the citation search did not identify the intended authority in its first result.
4. `search(type="o", case_name="Redd v. Summers", num_results=1)` returned Redd, Trayon v. Summers, Lawrence H., dated December 1, 2000, opinion 185316.
5. `search_document(opinion_id=185316, query="sheds no light", snippet_size=1700)` returned the conclusion addressing section 504, nonemployer status, and discrimination/retaliation. Used this to assess the opposition's distinction of Redd, not to infer any later result in Greer.

## Operational commands

Read the task instructions and output schemas. Ran `uv run fedcourts paths --court scotus --docket 73281703 --event evt-petition-disposition --role predictor`; the default cache was unwritable. The same path resolution succeeded with a temporary cache and `uv run --no-sync`. Output validation is operational, not a source of prediction facts. No other predictor output, realized outcome, or labeling-measurement artifact was read as evidence.
