# Retrieval record

## Provisioned and committed local inputs

Read the prediction prompt and prediction schema before the case inputs. Consulted the event, November 9 snapshot, context, document metadata, questions presented, petition selections, opposition selections, reply, appellate decision and lower-court docket summary under the provisioned case-level record. No related-docket snapshot was provisioned. Read `metrics/statpack.md` for the modern-cert, circuit, paid relist/CVSG/amicus and salience-band cuts and prior-Term table; inspected top-level keys of `metrics/statpack.json`. Also read the tooling and flags schemas. No outcome, other prediction, evaluation or qp-topics artifact was consulted.

## CLI setup and corpus lookups

An initial `uv run fedcourts paths --court scotus --docket 73500275 --event evt-order-relist-disposition --role predictor` failed because uv's default cache path was read-only. Subsequent uv calls used `UV_CACHE_DIR=/tmp/uv-cache` and `--no-sync`, without installing packages. The paths command then succeeded and only identified the event and corpus paths. Read `uv run --no-sync fedcourts query --help`, with a second local help invocation to inspect its lower options.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 3`
   - Transfer: `ranged corpus reads: 79 GET(s), 20643840 byte(s)`.
   - Returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). Each showed three distributions, a CVSG and a subsequent grant. No opinion bodies requested. These are descriptive procedural examples, not a random sample or substantive analogues. Their docket-number Terms passed the derived-year filter; their grant dates extend into 2026.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-944 --limit 1`
   - Transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`.
   - Returned pending Robinhood v. Sodha, case scotus/73280982, June 1, 2026 CVSG, three distributions, next conference November 13, and no grant/denial date, last polled November 9. This was the separate petition identified in ON24's own briefs, not a lookup for ON24's disposition.

## Public companion materials

No broad web searches and no live CourtListener MCP calls were made.

The web tool was attempted three times: twice opening the official Robinhood docket and once opening its government PDF. All three returned no visible content or usable source handle. I did not infer anything from those empty responses. Exact targets:

- `https://www.supremecourt.gov/docket/docketfiles/html/public/25-944.html`
- `https://www.supremecourt.gov/DocketPDF/25/25-944/428786/20261007154234084_25-944_Robinhood_CVSG_final.pdf`

Shell fallback attempts, all directed only to that separate petition:

1. `curl -fsSL` of the official docket piped to uv/Python/BeautifulSoup failed at uv's default read-only cache; curl reported a broken pipe. No docket facts were obtained.
2. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; Python reported BeautifulSoup unavailable and curl again reported a broken pipe. Installed nothing.
3. Repeated with standard-library Python HTML processing. Retrieved the docket, but uncollapsed whitespace and scripts made the output noisy/truncated. No script or embedded value was executed or copied into an output file.
4. Repeated with script/style removal and whitespace normalization. Read the proceedings and PDF link list. Confirmed the June 1 invitation, October 7 government filing, October 20/21 supplements, and common November 6/November 13 conference sequence. The page did not report Robinhood disposed of. ON24's live docket was not requested.
5. `curl -fsSL` of the government PDF piped to `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts pdf-text /dev/stdin` failed because the command did not recognize that path as a file. No PDF text obtained on this attempt.
6. Retrieved the government PDF into a Linux anonymous memory file using Python's standard library and invoked `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts pdf-text /proc/<reader-pid>/fd/<descriptor>`; displayed its opening 160 text lines. Extraction succeeded: 29 pages, 49,821 characters. Read the questions and contents, including the distinction between recommending review of question 1 and not question 2. No PDF was saved on disk.
7. Repeated the same memory-file retrieval/extraction and displayed the substantive discussion opening and conclusion. Read printed pp. 9–12 and 22–24: the United States recommends review of reformulated question 1, not question 2, and notes that the required-statements theory can remain in litigation. This sharpened both the possible hold/GVR route and its limits. No ON24 outcome material surfaced.

The related-docket and government-brief evidence was publicly dated before or on the snapshot date. In this forward cell its use is permitted; no allegation about ON24's own disposition was encountered. The government did not recommend an outcome for ON24. Its significance here is my inference.

## Validation

Cell validation uses `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/73500275/events/evt-order-relist-disposition/predictions/codex-baseline/20261109T212928Z`. This is local schema/completeness checking, not substantive retrieval.
