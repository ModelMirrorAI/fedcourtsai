# Retrieval beyond provisioned inputs

All retrieval took place September 16, 2026, in forward mode. No lookup sought this petition's disposition or subsequent history.

## Committed statistical context

- Read `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit sections, paid-segment relist and CVSG cuts, and sal-v4 per-Term band table.
- Read the corresponding `metrics/statpack.json` baseline segments for 2017–2024 and computed the denominator-weighted reached rate: 593 / 11,580 = 0.05120898100172712.
- No `fedcourts query`, `open-events`, or remote corpus read occurred, so there are no ranged-corpus transfer lines. `fedcourts paths --court scotus --docket 73357827 --event evt-petition-disposition --role predictor` only resolved paths. Its first invocation hit an unwritable default uv cache; an invocation using a temporary cache succeeded.

## Web-tool attempts

The following calls returned no visible content or usable citation result:

1. Open `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf` for general cert standards.
2. Search `site.supremecourt.gov "Alliance for Hippocratic Medicine" "core business"` for primary-source standing guidance.
3. Open `https://www.govinfo.gov/content/pkg/USCOURTS-ca7-25-01279/pdf/USCOURTS-ca7-25-01279-0.pdf` to try to obtain the pre-cert lower-court opinion. No text was received; its contents were not inferred.

## CourtListener MCP

1. `search(type="o", q='citation:("387 F.3d 565" OR "678 F.3d 730" OR "166 F.4th 627")', num_results=3)` returned two Crowley representations and Sandusky. The query was limited to named pre-decision authorities, including the lower-court citation supplied in the petition.
2. `search_document(opinion_id=[798771,788159], query="1983", snippet_size=1200)` supplied primary-source excerpts from Crowley and Sandusky. Used to distinguish the provisional-ballot and local-recount holdings from the present administrative-procedure claim. The response contained many overlapping snippets and was partially truncated; I rely only on visible text, not on a claimed full-opinion review.
3. `search(type="o", citation="166 F.4th 627", num_results=1, fields=["caseName","dateFiled","opinions","absolute_url"])` returned zero results. No inference about the existence or merits of the lower-court opinion follows from this miss.

## Exact pre-decision supplemental filing

URL supplied in the provisioned snapshot:

`https://www.supremecourt.gov/DocketPDF/25/25-1288/424275/20260915123704686_Supp%20Brief%209-15-26.pdf`

- Initial direct public-filing request used `curl` piped to `pdftotext`; the utility was absent and the pipe failed, yielding no document text.
- Retrieved that URL with Python `urllib.request.urlopen`, parsed the response entirely in memory with `pypdf.PdfReader`, and read the extracted text. No CourtListener REST endpoint or credential was used, and no downloaded file was written.
- Repeated the same exact URL to read PDF pages 6–7 (printed pp. 3–4), which the first tool response had truncated. The brief identifies August 19 and August 28 circuit decisions and reports cert denials in different PILF cases. These are pre-prediction context, not this event's outcome.

No target docket search, later-history search, evaluator artifact, other predictor output, or topic-labeling artifact was read.
