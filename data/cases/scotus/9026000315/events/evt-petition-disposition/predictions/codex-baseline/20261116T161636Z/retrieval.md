# Retrieval record

## Provisioned baseline and local references

Read the event definition and the case-level `record/context.json`, `record/snapshots/2026-11-16.json`, `record/documents/documents.json`, `questions-presented.txt`, `petition.txt`, `appendix.txt`, and `record/same-question.json`. The petition and relevant appellate-opinion passages in its appendix supply the case analysis. No other cell's predictions or evaluations, or any `data/qp-topics/` material, were read.

Read `.github/prompts/predict.md`, the prediction schema, the tooling-feedback schema, the committed `metrics/statpack.md` (modern-cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and the sal-v8 reached-band table), and the repository Justice-service registry at `src/fedcourtsai/pipeline/justices.py`. Repository path searches and git status checks were local housekeeping, not retrieval of case outcomes or forecasts.

## Corpus CLI attempts

1. `uv run fedcourts query --help` — failed before execution because the default uv cache directory was read-only. No corpus retrieval and no transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — succeeded using the existing environment; structured-filter help. No corpus retrieval and no transfer line.
3. `COLUMNS=180 UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — repeated the help with wider formatting to inspect filters. No corpus retrieval and no transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4` — returned Robinhood Markets v. Sodha (25-944; three distributions and a CVSG), Goldman Sachs Bank USA v. Brown (25-1408; four distributions), U.S. DOGE Service v. U.S. District Court (25-1103; two distributions), and Berry v. United States (25-7026; five distributions). These are grant-selected procedural priors, not a representative sample or substantive analogues. None is the target case. Exact stderr transfer line:

   `ranged corpus reads: 40 GET(s), 10420224 byte(s)`

The query year bar is docket-Term-based, not a strict decision-date bar; the returned resolution dates were before this forward prediction date. No `--full` opinion-body corpus retrieval was made.

## CourtListener MCP attempts

1. `search(type="o", citation="725 F.3d 498", num_results=1)` — found *Liberty Mutual Insurance v. United States ex rel. Lamesa National Bank (In re Schooler)*, Fifth Circuit, August 7, 2013, opinion 1036824.
2. `search_document(opinion_id=1036824, query="gross negligence", snippet_size=1400)` — returned historical trustee-liability passages and footnote 10; the long response was partially truncated in display.
3. `read_document(opinion_id=1036824, chunk_index=11, chunk_size=8000)` — read the end of footnote 10, including the government's negligence argument and the Fifth Circuit's adherence to circuit precedent. This is a historical government position, not advice or a forecast concerning Goldman.
4. `search(type="o", q='citation:("196 F.3d 1" OR "5 F.3d 750")', num_results=2, fields=["caseName","dateFiled","citation","absolute_url","opinions"])` — returned duplicate versions of *Hutchinson*, including opinion 653638; did not paginate.
5. `search_document(opinion_id=653638, query="willful", snippet_size=900)` — independently confirmed the historical negligence versus willful-misconduct split and the distinction between personal and official capacity.
6. `search(type="o", citation="196 F.3d 1", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])` — imprecise citation match returned *Wilhite v. District of Columbia*, 196 F. Supp. 3d 1, not the intended authority. Disregarded as irrelevant; no opinion read.
7. `search(type="o", court="ca1", case_name="Mailman", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])` — returned the later Mailman opinion, 212 F.3d 632, which identified and cited the earlier 196 F.3d 1 opinion; its citation graph included opinion 198701.
8. `search_document(opinion_id=198701, query="principled", snippet_size=1100)` — found the earlier Mailman opinion's explicit negligence-liability analysis and its separate derived-immunity discussion.
9. `read_document(opinion_id=198701, chunk_index=0, chunk_size=1500)` — verified the opening procedural account: a creditor's negligence claim against a trustee whose court-authorized abandonment was protected by derived immunity.

No MCP query sought this petition's Supreme Court disposition, subsequent history, or anyone else's forecast. No direct CourtListener REST request was made.

## Web attempts

Each of the following calls returned no usable payload: no search results, document text, or source references were available. No facts from these attempts informed the prediction.

1. One `web.run` search call containing `site.govinfo.gov "Mosser v. Darrow" "341"` and `site.ca5.uscourts.gov "Schooler" "gross negligence" "2013"` — sought historical primary sources.
2. `web.run` search for `Mosser Darrow 341 U.S. 267 Supreme Court trustee negligence 1951` — sought the historical Supreme Court authority.
3. `web.run` open of the Supreme Court's official `/about/biographies.aspx` page — attempted current-bench verification; used the repository dated registry instead.
4. `web.run` open of the September 24, 2026 amicus PDF linked in the snapshot, `/DocketPDF/26/26-315/425581/20260924152750533_26-315%20Amicus%20Brief.pdf` on the Court's official site — attempted to inspect the filed brief, not the docket or an outcome. No brief text was obtained.

## Output checks

The prescribed cell validator is run after writing these artifacts. Validation reads local schemas and cell completeness; it is not a case-information retrieval. The uv cache override and `UV_NO_SYNC=1` use installed tooling without installing packages.
