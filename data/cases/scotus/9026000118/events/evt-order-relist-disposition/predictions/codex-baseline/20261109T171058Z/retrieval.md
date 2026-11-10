# Retrieval record

## Repository and corpus

- Read the prediction contract, prediction schema, flags/tooling schemas, committed `metrics/statpack.md`, and statpack top-level keys. Read only the identified cell's event and provisioned record; no outcomes, other predictions/evaluations, or `data/qp-topics/` artifacts were read.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000118 --event evt-order-relist-disposition --role predictor`. Initial attempt failed because the default uv cache was read-only. Reissued successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it identified the event and corpus paths and labeled the outcome evaluator-only.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026 --limit 5`. Refused: `modern` is not an era token; no transfer line.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 5`. Returned five grants, including Goldman Sachs Bank USA v. Brown, U.S. DOGE Service v. United States District Court, Corey Duran Berry v. United States, and Todd Blanche v. Ozurumba. No opinion bodies requested; no close substantive analogue identified. Transfer: **`ranged corpus reads: 41 GET(s), 10747904 byte(s)`**. This is a Term/year-mask query, not a guarantee of grant dates preceding January 2026.

## Web interface attempts

Each call below returned no usable text or source identifier in this execution's web-tool response; none supplied factual content used in the forecast.

1. Search: `site.supremecourt.gov opinions 2026 Louisiana Callais section 2 alternative map politics districting criteria`.
2. Open guessed official precedent PDF path `https://www.supremecourt.gov/opinions/25pdf/24-109_n758.pdf`.
3. Open the snapshot's September 18 motion-to-dismiss PDF, document 424782, filename `20260918112621309_Singleton%20Motion%20to%20Dismiss%20Final.pdf`.
4. Attempted find for `Singleton` with an empty reference after the nonresponsive open; no usable result.
5. Repeated the September 18 PDF open.
6. Repeated the September 18 PDF open again.
7. Open the snapshot's September 29 appellants' response PDF, document 425967, filename `20260929142631829_2026.09.29%20-%20Ala.%20Opp.%20-%20Singleton%20-%20FINAL.pdf`.

## Successful official-document retrieval

All URLs below were copied from links already present in the provisioned snapshot; neither a current docket nor this appeal's outcome was requested.

- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts pdf-text <(curl -fsSL 'https://www.supremecourt.gov/DocketPDF/26/26-118/424782/20260918112621309_Singleton%20Motion%20to%20Dismiss%20Final.pdf')`. Failed: `pdf-text: no file at /dev/fd/63`. The process-substitution pipe was not a regular input file. No text obtained.
- Retrieved that same September 18 PDF using `urllib.request.urlopen`, held the bytes in `os.memfd_create`, and invoked `uv run fedcourts pdf-text /proc/<reader-pid>/fd/<descriptor>` while the in-memory descriptor remained open. Successful: **27 pages, 35,751 characters**. Read questions presented, introduction, mootness arguments, alternative-map dispute, and conclusion; terminal output was truncated. No downloaded file written to disk.
- Retrieved the September 29 response at `https://www.supremecourt.gov/DocketPDF/26/26-118/425967/20260929142631829_2026.09.29%20-%20Ala.%20Opp.%20-%20Singleton%20-%20FINAL.pdf` with the same in-memory method and extractor, piping stdout through `sed -n '110,380p'`. Successful: **18 pages, 25,544 characters**. Read argument I on mootness and portions of argument II; terminal output was truncated.
- Repeated that response retrieval and extraction, piping stdout through `sed -n '213,252p'`, to complete the mootness discussion, including footnote 2 requesting Munsingwear vacatur if the Court finds mootness. Successful with the same page/character counts. No later filing or disposition was consulted.

## CourtListener MCP

- `search(type="o", case_name="Louisiana v. Callais", num_results=3)`. Successful; query id `750ceadc`, four total results, three displayed. The first two identified original/revised April 29, 2026 Supreme Court opinions in 24-109, opinion ids 11317641 and 11320154. The third was an unrelated 1990 Louisiana case. Only metadata/snippets were returned; no opinion body read, no further pagination. This corroborated the existence/date of the provisioned statement's precedent, not its complete holding.

## Local diagnostics and validation

Read-only schema extraction initially had a jq syntax error, then succeeded. Read-only searches located the supplied PDF extractor after the pipe-input failure. `git status --short` showed no preexisting changes. The final cell validation is recorded by the engine transcript; no harness-owned usage or retrieval-log JSON was written.
