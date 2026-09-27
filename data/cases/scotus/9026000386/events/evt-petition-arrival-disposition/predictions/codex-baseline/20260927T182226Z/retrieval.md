# Retrieval record

## Local context beyond the provisioned case record

- Read the governing prompt, AGENTS instructions, and prediction, flags,
  and tooling schemas. Inspected directory names to locate applicable
  instructions and the supplied case files; did not open outcome files,
  other predictors' outputs, or labeling-measurement artifacts.
- Read `metrics/statpack.md`: modern-cert disposition and originating-court
  cuts; paid-segment relist/CVSG cuts; and sal-v4 per-Term reached rates.
  Read `metrics/statpack.json` to obtain exact private-floor denominators
  and rates for displayed Terms 2017–2025. Weighted pooling produced
  638 / 12,720 = 0.05015723270440252. Current-Term rows were not used
  for the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` for artifact
  vintage: `96ebdd342 2026-09-26T12:03:37Z`. This is not a corpus-pull stamp.
- Ran `uv run fedcourts paths --court scotus --docket 9026000386 --event
  evt-petition-arrival-disposition --role predictor`. The first attempt
  failed because the default cache directory was read-only; retrying with
  a writable temporary cache succeeded. This is path resolution, not a
  corpus lookup. No `fedcourts query` or `open-events` calls were made,
  and no ranged-corpus transfer line was produced.

## Attempted general-law web retrieval

The following calls returned no usable results or source text. They did not
identify this case and supplied no evidence to the prediction:

1. Search: `site.supremecourt.gov rules Rule 10 considerations governing review writ certiorari`.
2. Search, in the same call: `site.uscode.house.gov 26 USC 3304 (a)(6)(A)(ii) educational institution reasonable assurance`.
3. Open: `https://uscode.house.gov/view.xhtml?req=%28title%3A26+section%3A3304+edition%3Aprelim%29`.
4. Open: `https://uscodeweb1.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section3304`.
5. Open: `https://www.govinfo.gov/content/pkg/USCODE-2021-title26/pdf/USCODE-2021-title26-subtitleC-chap23-sec3304.pdf`.

No CourtListener MCP calls, direct CourtListener requests, or case-specific
web searches were made. No outcome-revealing material was encountered.
