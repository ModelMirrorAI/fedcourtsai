# Retrieval log

## Provisioned inputs

Read the case-level September 30 snapshot, context, application text and documents manifest, and the interim arrival event definition. No other prediction or realized-outcome file was consulted.

## Committed aggregate context

- Read `metrics/statpack.md`, specifically the interim applications section and its prior-Term rows; inspected the top-level keys of `metrics/statpack.json` for vintage metadata. No build/pull timestamp was available there. Pool: (17 + 14)/(226 + 70), application Terms 2016–2025. No live corpus query or `open-events` call was made, so no ranged-corpus transfer line exists.
- Ran `uv run fedcourts paths --court scotus --docket 9526000428 --event evt-motion-disposition --role predictor`. The default cache was read-only; repeating with a writable temporary uv cache succeeded. This resolved paths, not docket facts.

## General legal context only

1. `web.run` search queries: `site.supremecourt.gov Gonzalez Crosby 545 524 532 Rule 60 merits` and `site.supremecourt.gov "Price" "Dunn" "strong showing" "2019"`. The tool returned no usable results or source text.
2. `web.run` open attempt for the Justia United States Reports 545/524 opinion page. The tool returned no usable text. No proposition is attributed to that failed retrieval.
3. CourtListener `search(type="o", citation="545 U.S. 524", num_results=1)`. It returned a nonmatching *Guion v. England* result, 545 F. Supp. 2d 524, which was discarded; no document was opened.
4. CourtListener `search(type="o", court="scotus", case_name="Gonzalez v. Crosby", num_results=2, filed_before="2006-01-01")`. Returned the June 23, 2005 opinion, 545 U.S. 524, cluster 799985, with lead opinion ID 9500020, plus an unrelated procedural order in the same historical case. Used only the relevant merits-opinion identification.
5. CourtListener `search_document(opinion_id=9500020, query="532", snippet_size=1800)`. Read the Rule 60(b)/successive-petition distinction and the discussion of new evidence supporting a previously litigated claim. This predates the forecast by decades and contains no target-case information.

No search named Nelsen, Pike, application 26A428, or its disposition. No live target docket, subsequent history, or target-case decision coverage was retrieved. The separate September 29 denial described in the provisioned application was not searched or independently retrieved.
