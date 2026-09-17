# Retrieval record

## Local context beyond the provisioned record

- Read `metrics/statpack.md`: modern cert disposition, paid-segment relist and CVSG cuts, and sal-v4 per-Term reached-band table. Used only Terms 2017–2024 for the grant anchor. A local Python calculation pooled the displayed elevated rates, yielding 0.17237935943060498 over weighted n=2,810.
- Inspected top-level keys of `metrics/statpack.json`; no additional rate was used from it.
- Read the task contract and output schemas. Ran `uv run fedcourts paths --court scotus --docket 73281632 --event evt-petition-disposition --role predictor`. The initial invocation failed on a read-only uv cache; retrying with a temporary cache succeeded. No outcome file was opened.
- No corpus query or open-events lookup was made, so there is no ranged-corpus transfer line to report.

## General-precedent web attempts

The following requests returned no usable result content and supplied no evidence:

1. Search: `site.supremecourt.gov opinions 2024 CFPB Community Financial Services source purpose appropriation`.
2. Search: `site.supremecourt.gov opinions 2025 FCC Consumers Research nondelegation numerical cap`.
3. Search: `site.supremecourt.gov "24-354" "2025"`.
4. Search: `site.supremecourt.gov "22-448" "2024"`.
5. Open attempt: `https://www.supremecourt.gov/opinions/24pdf/24-354_0861.pdf`. The endpoint was not verified and no content was used.

## CourtListener MCP

1. `search(type="o", citation="601 U.S. 416", num_results=1)` returned CFPB v. Community Financial Services Ass'n, decided May 16, 2024, opinion 11066682.
2. `search_document(opinion_id=11066682, query="source and purpose", snippet_size=450)` supplied the majority's appropriation reasoning, including its conclusion that source and purpose provide the control required by the Appropriations Clause.
3. `search(type="o", citation="606 U.S. 656", num_results=1)` returned FCC v. Consumers' Research, decided June 27, 2025, opinion 11243407.
4. `search_document(opinion_id=11243407, query="qualitative", snippet_size=250)` supplied majority and dissent excerpts. I distinguished the majority's acceptance of qualitative constraints from the dissent's objections.

Both retrieved precedents predate this petition and its lower-court judgment. No lookup targeted this case's disposition or subsequent history; no outcome-revealing material was encountered.
