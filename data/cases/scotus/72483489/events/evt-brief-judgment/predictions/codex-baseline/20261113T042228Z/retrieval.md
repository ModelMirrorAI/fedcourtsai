# Retrieval record

## Provisioned inputs and local references

Read the prediction prompt and schema, event definition, case-level context, November 5, 2026 snapshot, document inventory, question presented, lower-court docket note, and December 19, 2024 opinion. Consulted relevant portions of the provisioned petitioner and respondent merits briefs and the Solicitor General's invited brief. Read the guarded merits and complete-lineup vote sections of `metrics/statpack.md`, the corresponding `merits`, `justice_votes`, and `authorship` JSON data, and the merits-population cautions in `metrics/README.md`. Local shell reads and JSON arithmetic are not external case retrieval. No other prediction, evaluation, outcome file, or labeling artifact was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 72483489 --event evt-brief-judgment --role predictor` failed because the default uv cache was on a read-only filesystem. No corpus transfer occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 72483489 --event evt-brief-judgment --role predictor` succeeded and confirmed the event path; the outcome was explicitly marked evaluator-only and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. The help was displayed again with `tail -65` to inspect its remaining options.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '574 U.S. 418' --decided-before 2025 --limit 2` returned no matches and the citation-coverage warning. Stderr transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No Hana prior was obtained; I did not treat the absence as absence of precedent.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 3` returned docket rows for RiseandShine, Monsanto v. Durnell, and Hikma v. Amarin. Stderr transfer: `ranged corpus reads: 77 GET(s), 20119552 byte(s)`. These had no opinion and no parsed merits judgment. The year mask did not turn those grant rows into useful pre-2025 resolved merits analogues. I excluded all three from substantive inference, including my own still-pending case; no merits outcome surfaced.

## Web calls, in order

1. Batched searches: `site.supremecourt.gov opinions Hana Financial Hana Bank 574 418 2015` and `site.supremecourt.gov opinions U.S. Bank Village Lakeridge standard review mixed questions 2018`. The results identified historical opinions and commentary. I used only opinion text, not commentary. No forecast of RiseandShine surfaced.
2. Opened the official Hana opinion at `https://www.supremecourt.gov/opinions/14pdf/13-1211_8o6b.pdf`; the tool returned an internal fetch error. No opinion text from this attempt was used.
3. Opened `https://supreme.justia.com/cases/federal/us/574/418/`. Read the reproduced Supreme Court opinion, particularly its consumer-impression analysis and preservation of summary judgment. This was primary judicial text, not the site's editorial summary.
4. Opened the official docket at `https://www.supremecourt.gov/search.aspx?filename=%2Fdocket%2Fdocketfiles%2Fhtml%2Fpublic%2F24-1016.html` to locate the missing United States merits filing. The first open returned title/metadata without readable body.
5. Reopened the same docket URL; readable entries and document links were returned. They confirmed the grant and merits schedule and exposed no merits disposition. The docket reported the January 12, 2027 argument setting and the November 4 respondent brief, consistent with the baseline. No later argument or outcome was retrieved.
6. Opened the corrected United States merits brief at `https://www.supremecourt.gov/DocketPDF/24/24-1016/424405/20260917111153556_24-1016tsacUnitedStates.pdf`. The PDF supplied the government's merits position and requested vacatur. This filing predates the briefed cutoff. It is distinct from the provisioned May 20 invited cert-stage brief.
7. Reopened that same United States PDF to inspect its legal analysis and remand discussion, including pp. 11–14 and 30–32. No new document was retrieved.
8. Opened the Court's official current-members page at `https://www.supremecourt.gov/about/biographies.aspx` to verify the nine-member roster. It matched the names used in the structured distributions and votes.

No CourtListener MCP lookup was attempted: the provisioned lower-court opinion already matched the judgment under review. No forecast source, this project's public predictions, case-outcome search, oral-argument transcript, or post-decision discussion was sought.

## Validation

Validation uses the same writable-cache environment override and the exact cell directory. Its result is reported with the completed cell.
