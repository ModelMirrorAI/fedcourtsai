# Retrieval record

## Beyond the provisioned case inputs

- Read the committed `metrics/statpack.md` merits section, prior-Term per-Justice vote rows, and corresponding `merits`, `justice_votes`, and `authorship` data in `metrics/statpack.json`. Computed the applicable prior-Term pools locally. No live corpus query or `open-events` lookup was used, and there was no ranged-corpus-read stderr line.
- Web search queries: `site.govinfo.gov Bennett Spear 520 U.S. 154 177 178 final agency action` and `site.supremecourt.gov opinions 2024 Seven County NEPA final agency action`. The tool returned no usable search-result content. These were general-precedent searches, not searches for this case or its outcome.
- Attempted to open the official Bennett v. Spear opinion at `https://www.govinfo.gov/content/pkg/USREPORTS-520/pdf/USREPORTS-520-154.pdf` with the web tool. No usable opinion text was returned; none informed the forecast.
- CourtListener MCP `search`: `type=o`, `citation=520 U.S. 154`, `num_results=1`, requesting case name, filing date, citation, URL, identifiers, and snippet. The request returned HTTP 429, with an estimated 14-second wait. It supplied no case text or search result. I proceeded with the provisioned briefs' presentation of the finality standard and did not use a direct REST fallback.

## Local contract and validation tooling

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the output schemas.
- Ran `fedcourts paths --court scotus --docket 73279024 --event evt-argument-judgment --role predictor` to confirm paths. The first `uv run` attempts could not initialize the default read-only cache; using a writable temporary cache allowed the command and local statpack arithmetic to run.
- No target-case outcome, post-argument docket update, external case commentary, other predictor output, evaluation output, or topic-label artifact was consulted.
