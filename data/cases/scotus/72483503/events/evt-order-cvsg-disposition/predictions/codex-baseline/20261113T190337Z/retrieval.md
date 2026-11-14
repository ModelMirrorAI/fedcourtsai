# Retrieval and input audit

## Provisioned and local material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the event definition, `record/snapshots/2025-07-01.json`, `record/documents/documents.json`, `questions-presented.txt`, relevant substantive portions of `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and `appendix.txt`, and `record/context.json`. Case-record paths are under `data/cases/scotus/72483503/`. Consulted the required flags and tooling schemas. Read the cert sections and Term-band table in `metrics/statpack.md`; inspected `metrics/statpack.json` and its prior-Term high-band rows. No other prediction, evaluation, realized-outcome file, or topic-labeling artifact was read.

Shell file discovery and text extraction used `rg`, `find`, `cat`, `sed`, `wc`, `fmt`, and Python's standard-library JSON reader. No external PDF extraction or package installation was necessary. Python inspections read only the named schemas and statpack, not a corpus or secret configuration.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 72483503 --event evt-order-cvsg-disposition --role predictor` failed because the default UV cache location was read-only. No corpus request occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 72483503 --event evt-order-cvsg-disposition --role predictor` succeeded, identifying the case, corpus, and event paths. The outcome was described only as evaluator-only and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` displayed the structured-filter interface.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --decided-before 2024 --limit 4` was refused because `modern` is not a decade token. The error displayed the accepted vocabulary; no transfer line was printed.
5. Corrected query: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2024 --limit 4` succeeded. Exact stderr transfer line:

   ```text
   ranged corpus reads: 134 GET(s), 35061760 byte(s)
   ```

   Returned M & K Employee Solutions, No. 23-1209; Landor, No. 23-1197; Medina, No. 23-1275; and Rivers, No. 23-1345. These were compact metadata rows, with no opinion-body hydration. The first two carried CVSG dates. This outcome-selected sample was not used to estimate grant frequency. The Term filter limits docket-era eligibility; returned grant dates can fall in the following Term. No target-case row was sought.

## Web retrieval attempts

The objective was to verify circuit authority already cited in the staged reply, not obtain this petition's current status.

1. Paired searches: `site.ca9.uscourts.gov "Anderson" "Intel" "2025" "meaningful"` and `site.opn.ca6.uscourts.gov "England" "DENSO" "2025"`. Results surfaced circuit-authority material and incidental later related-case commentary. Some snippets mentioned later Intel developments and later government briefing in Parker-Hannifin; a commentator's expectation about related Intel litigation also surfaced. Those commentary pages were not opened and their bottom lines were excluded. See `flags.json`.
2. Opened the Ninth Circuit's May 22, 2025 Anderson opinion, No. 22-16268: `https://cdn.ca9.uscourts.gov/datastore/opinions/2025/05/22/22-16268.pdf`.
3. Searched that document for `to the extent` to locate the performance-comparison discussion. Used the official opinion's pp. 12-14 to verify the narrower rule rather than adopting a claim about all prudence complaints.
4. Search: `"England" "DENSO" "2025" "meaningful benchmark"`, to locate the Sixth Circuit authority. Substantive reliance was on the primary opinion obtained through MCP and the official PDF, not search-result commentary.
5. Opened the Sixth Circuit's May 6, 2025 England opinion: `https://www.opn.ca6.uscourts.gov/opinions.pdf/25a0117p-06.pdf`. Page 5 treats comparators as ordinarily required and applies a service-comparability rule to recordkeeping fees.
6. Reopened the Anderson official PDF to obtain a clear primary-source view of the same opinion.
7. Repeated the in-document search for `to the extent` in Anderson. No later Intel Supreme Court docket, merits decision, or commentator page was opened.

## CourtListener MCP attempts

1. `search(type="o", court="ca6", case_name="England v. Denso", filed_before="2025-07-01", num_results=2)` returned one published May 6, 2025 decision, 136 F.4th 632, cluster 10534897, opinion 11001485, lower-court docket 24-1360. It identified the official PDF URL used above.
2. `read_document(opinion_id=11001485)` returned the England opinion, 27,597 characters, discussing dismissal of a recordkeeping-fee complaint.
3. `search_document(opinion_id=11001485, query="Johnson", snippet_size=1500)` returned three overlapping hits in its benchmark discussion. These confirmed that England cites Johnson while requiring context-specific comparisons for the distinct fee claim. I did not follow the target-case citation or retrieve its later history.

The MCP calls succeeded. There was no direct CourtListener REST request, credential access, or fallback outside the sanctioned interface.

## Completion

Ran the contract's cell-scoped validator with the writable UV cache override. Validation results are reported in the run transcript. The only authored files are the seven contract-named files in this run's prediction directory; harness-owned usage and retrieval JSON logs were not authored.
