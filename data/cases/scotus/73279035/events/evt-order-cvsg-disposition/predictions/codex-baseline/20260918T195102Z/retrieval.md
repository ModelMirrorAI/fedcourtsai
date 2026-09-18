# Retrieval record

## Provisioned and repository inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags,
  and agent-tooling schemas.
- Read this event's `event.yaml`, case-level `record/context.json`, and
  `record/snapshots/2026-04-07.json`.
- Read `record/documents/documents.json`, `questions-presented.txt`, and selected
  substantive sections of `petition.txt` (including the lower-court opinion)
  and `brief-in-opposition.txt`. No external copy of these case filings was fetched.
- Read `metrics/statpack.md` and relevant fields of `metrics/statpack.json`.
  Locally computed the OT2017-OT2024 high-band reached pool as 314/898.
- Read path and serialization helpers solely to resolve and serialize cell
  outputs. Ran `fedcourts paths --court scotus --docket 73279035 --event
  evt-order-cvsg-disposition --role predictor`. The first attempt failed on
  the read-only default uv cache; using a temporary cache succeeded.
- No `fedcourts query` or `open-events` calls; no ranged corpus transfer lines
  were produced. No current-case docket, outcome, other predictions, or
  labeling-measurement artifacts were read.

## Web attempts: general precedent only

1. Search query: `site.supremecourt.gov opinions 2010 CIGNA Amara 09-804 surcharge`.
   The tool returned no usable result content.
2. Open attempt: `https://www.supremecourt.gov/opinions/10pdf/09-804.pdf`.
   No usable content returned.
3. Open attempt: `https://www.law.cornell.edu/supct/html/09-804.ZO.html`.
   No usable content returned.

No substantive inference rests on those empty web responses.

## CourtListener MCP

1. `search(type="o", citation="563 U.S. 421", num_results=1,
   fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`:
   returned CIGNA Corp. v. Amara, May 16, 2011, including lead opinion 9441561.
2. `search_document(opinion_id=9441561, query="surcharge", snippet_size=900)`:
   read the historical-equity, trustee/fiduciary, and actual-harm passages.
3. `search(type="o", citation="577 U.S. 136", num_results=1,
   fields=["caseName", "dateFiled", "citation", "opinions"])`:
   unexpectedly returned Hawkins v. Community Bank of Raymore, 577 U.S. 495
   (2016), rather than the requested precedent. Not used as analogous evidence.
4. `search(type="o", case_name="Montanile", court="scotus",
   filed_before="2016-12-31", num_results=2,
   fields=["caseName", "dateFiled", "citation", "opinions"])`:
   located the January 20, 2016 Montanile decision, including lead opinion
   9821183; also returned an earlier procedural order, not used substantively.
5. `search_document(opinion_id=9821183, query="Amara", snippet_size=950)`:
   read footnote 3's discussion of Amara and the earlier remedies cases.

These calls sought only pre-existing general legal context, not this petition's
subsequent history. No outcome-revealing material about this cell surfaced.
