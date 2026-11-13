# Retrieval record

## Local inputs and calibration

Read `.github/prompts/predict.md`, the prediction/flags/tooling schemas, this event's `event.yaml`, and the case-level `record/`: context, November 13 snapshot, questions presented, document manifest, petition front matter and appendix, decision below, lower-court docket summary, and same-question list. Consulted `metrics/statpack.md`, including the modern-cert, circuit, paid relist/CVSG/amicus cuts and the sal-v8 per-Term reached table. Used the frozen 0.051587928582714486 anchor; no other prediction/evaluation or outcome artifact was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000624 --event evt-petition-arrival-disposition --role predictor` failed before execution because uv's default cache at `/home/codexcell/.cache/uv` is read-only.
2. Retried as `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts paths --court scotus --docket 9026000624 --event evt-petition-arrival-disposition --role predictor`. Succeeded and identified the case/event paths. The outcome was explicitly labeled evaluator-only and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --help`. Succeeded; read the structured-filter options before querying.
4. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 4`. Completed with no returned prior rows. Transfer line: `ranged corpus reads: 1143 GET(s), 299368448 byte(s)`. No empirical summary-reversal frequency or analogous-case estimate was inferred from this empty result. Forward mode requires no replay clock; the query did not name the subject petition.

No packages were installed. Local paths/schema inspection and cell validation are operational calls, not additional legal evidence.

## Web calls

1. One `web.run` search call contained two queries: `site.supremecourt.gov opinions "Galette" "2026"` and `site.supremecourt.gov "Galette" "corporate form"`. No results were returned. It provided no evidence.
2. Opened the provisioned official petition URL, `https://www.supremecourt.gov/DocketPDF/26/26-624/432234/20261109133223577_26-__%20Petition%20For%20A%20Writ%20Of%20Certiorari.pdf`, to try to recover its missing substantive text. The tool returned an internal error; no document text was obtained.
3. Opened the official Galette opinion URL returned by CourtListener, `https://www.supremecourt.gov/opinions/25pdf/24-1021_p860.pdf`. The tool returned an internal error; no text was obtained through that surface.

These searches targeted a prior precedent, not this petition's outcome or another forecaster's prediction. No forecast of the subject case or outcome surfaced.

## CourtListener MCP calls

1. `search(type="o", case_name="Galette", court="scotus", num_results=5)`. Query id `23e2aacd`; one result, Galette v. New Jersey Transit Corp., docket 24-1021, filed March 4, 2026, cluster 10803604, opinion 11270334. This was a precedent lookup, not a search for the subject petition's current state. The search supplied the official opinion-PDF URL used above.
2. `search_document(opinion_id=11270334, query="not the only", snippet_size=1800)`. One matching excerpt, at position 53133 in the opinion text. It confirms that legal separateness is not restricted to corporations and discusses state-law structural indicators and formal judgment liability. This strengthens the narrow corporate-form objection but does not determine CCSO's ultimate status.

## Limits

The substantive petition body remains unavailable as extracted text. The supplied appendix resolves the rehearing-summary gap. No current Supreme Court docket search was needed, no outcome was sought, and no external forecast was used.
