# Retrieval record

## Provisioned inputs

Read the event definition, context.json, snapshot `2026-10-04.json`, documents.json, questions-presented.txt, and relevant petition.txt passages including the appended lower-court opinion. All case-specific external retrieval was confined to exact pre-decision filing URLs already present in this snapshot. No current docket, outcome, subsequent history, companion-case outcome, other predictor output, or labeling-measurement artifact was consulted.

## Local aggregate context

- Read `metrics/statpack.md`: modern cert, originating circuit, paid-segment relist and CVSG cuts, and sal-v4 reached-band Term rows.
- Read corresponding aggregate fields in `metrics/statpack.json`; used jq to pool the elevated risk set for Terms 2017–2025, yielding denominator 3,085 and rate 0.16888168557536468.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json`: `808f812e9 2026-09-28T12:02:50Z`. This dates the committed artifact, not the underlying corpus refresh.
- No `fedcourts query`, `open-events`, or other live corpus retrieval. No ranged-corpus transfer line was produced. The administrative `fedcourts paths --court scotus --docket 9026000093 --event evt-petition-disposition --role predictor` command resolved the cell paths; its first attempt hit an unwritable default cache and succeeded with a temporary writable cache location.

## Web-tool attempts

1. Search: `site.supremecourt.gov Rule 10 considerations governing review on certiorari courts appeals conflict`.
2. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open the federal-response PDF below, twice.
4. Open the reply PDF below.

These tool attempts supplied no usable displayed source content; they were not relied upon as verification of a rule or case fact.

## Exact public filing retrieval

- Federal respondents' brief, filed August 14, 2026: `https://www.supremecourt.gov/DocketPDF/26/26-93/419170/20260814192425841_Ream_cert_response.pdf`. An initial curl-to-pdftotext pipeline failed because pdftotext was unavailable. Successfully fetched through Python httpx and extracted in memory with pypdf; the full-output attempt was truncated in the tool display, so a second fetch displayed printed pp. 8–11 specifically. The conclusion on p. 18 was also read. Decisive information: the government acknowledges the issue warrants review but favors McNutt as the vehicle and requests a hold here; it no longer advances the commerce-power theory in this case.
- Petitioner's reply, filed September 1, 2026: `https://www.supremecourt.gov/DocketPDF/26/26-93/422654/20260901095511196_26-93%20Reply%20Brief.pdf`. Fetched through httpx and extracted in memory with pypdf in two calls displaying printed pp. 1–4 and 7–10. Read the arguments for taking Ream as well as McNutt, preserving the Raich question, and rejecting the government's comparative standing concerns. The reply identifies the companion petition as No. 26-204; no separate lookup of that docket was made.

Both documents predate the prediction and are advocacy, not realized outcomes. The federal response materially changed the forecast toward a companion hold and possible GVR. No outcome-revealing material was encountered. No CourtListener MCP calls or direct CourtListener REST calls were made.
