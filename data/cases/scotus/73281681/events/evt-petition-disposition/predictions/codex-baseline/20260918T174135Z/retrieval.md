# Retrieval record

## Local sources

- Read the provisioned event, `record/context.json`, `record/snapshots/2026-09-17.json`, `record/documents/documents.json`, questions presented, and substantive sections of the petition and opposition.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating courts, paid-segment relist/CVSG cuts, and the `sal-v4` segment table. Computed an approximate denominator-weighted elevated reached rate from displayed Terms 2017–2024 only. No corpus query or open-events lookup was made; there is no ranged-corpus transfer line to report.
- Read the task instructions and output schemas. Ran `uv run fedcourts paths --court scotus --docket 73281681 --event evt-petition-disposition --role predictor`. The initial invocation failed on the default cache's read-only location; the retry using a writable temporary cache succeeded. Read `src/fedcourtsai/serialize.py` for the artifact-writing convention.

## General precedent through CourtListener MCP

1. `search(type="o", case_name="Anderson Creek Partners", filed_before="2023-01-01", num_results=3)`. Located the North Carolina Supreme Court's August 19, 2022 opinion, including opinion 9348052; no target-case lookup.
2. `search_document(opinion_id=9348052, query="not limited", snippet_size=1500)`. Read paragraph 42 and nearby reasoning concerning monetary exactions beyond in-lieu fees.
3. `search(type="o", case_name="Sheetz", court="scotus", filed_after="2024-04-01", filed_before="2024-04-30", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])`. Located the April 12, 2024 Supreme Court opinion, opinion 11066690.
4. `search_document(opinion_id=11066690, query="threshold", snippet_size=1800)`. Read the end of the majority opinion and the Sotomayor concurrence's threshold-taking discussion.

## Web attempts

The following general-precedent web requests returned no usable source content in this session; the independent doctrinal checks relied on the MCP passages recorded above instead:

- Search: `site.supremecourt.gov opinions 2023 Sheetz County El Dorado 22-1074 pdf`.
- Search in the same request: `site.nccourts.gov Anderson Creek Partners Harnett 2022 280PA20 monetary exactions`.
- Open `https://www.law.cornell.edu/supremecourt/text/22-1074`, attempted twice.
- Search: `"Anderson Creek Partners" "nccourts.gov" "2022"`.
- Open the official Sheetz opinion identified by MCP: `https://www.supremecourt.gov/opinions/23pdf/601us2r14_00m5.pdf`.

No search sought this petition's outcome or subsequent history. No current target-case docket or outcome was retrieved.
