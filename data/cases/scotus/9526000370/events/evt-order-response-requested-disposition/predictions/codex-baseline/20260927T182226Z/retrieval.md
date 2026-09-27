# Retrieval log

## Beyond the provisioned record

- Read `metrics/statpack.md`, principally “The interim docket (applications),” and the corresponding `interim.terms` counts in `metrics/statpack.json`. Used jq to pool application-Terms 2016–2025: 31 grants, 296 resolved, rate 0.10472972972972973, and 9,480 unparsed applications. No live corpus query was made; no ranged-corpus transfer line was produced. The inspected pack does not expose a corpus build/pull timestamp.
- Web search attempted two general-law queries: `site.law.cornell.edu/supct/html 08-681 Nken Holder stay four factors` and `site.law.cornell.edu/uscode/text/18/3626 prospective relief narrowly drawn least intrusive`. The tool returned no visible results or usable source text.
- Web open attempted `https://www.law.cornell.edu/uscode/text/18/3626`. The tool returned no visible source content. No legal proposition was added from this attempt.
- CourtListener MCP `search`: `type=o`, `citation=556 U.S. 418`, `num_results=1`, requested fields caseName/dateFiled/citation/absolute_url/snippet/id. Returned Nken v. Holder, dated April 22, 2009, reporter citation 556 U.S. 418, path `/opinion/145884/nken-v-holder/`. The response warned that some requested fields were unavailable. No opinion text was retrieved, and no further results were opened.

## Operational reads

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas. Ran `fedcourts paths` for the exact cell identifiers. Its first invocation failed because the default uv cache was read-only; the retry used a writable temporary cache and succeeded. These commands provided no substantive historical-case evidence. Validation checks the resulting artifacts; it is not outcome research.

No current-case web or CourtListener query, live corpus query, or outcome-file read informed this prediction.
