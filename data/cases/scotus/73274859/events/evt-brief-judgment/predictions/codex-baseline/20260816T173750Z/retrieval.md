# Retrieval

- Read `metrics/statpack.md`, especially “The merits docket (granted cases),” and pooled the strictly prior OT2015-OT2024 window: 359 disturbed / 515 parsed = 69.7% (the rendered rows are OT2017-OT2024; Terms without parsed judgments are omitted).
- Retrieved the petitioners' May 14, 2026 merits brief from the Supreme Court docket URL in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-170/408810/20260514091116673_Boulder%20brief%20for%20petitioners%20FINAL.pdf`.
- Retrieved the United States' May 21, 2026 merits amicus brief from the Supreme Court docket URL in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-170/409590/20260521184428959_25-170_Suncor_v_Boulder_Merits_FINAL.pdf`.
- Retrieved the respondents' complete July 27, 2026 merits brief from the Supreme Court docket URL in the provisioned snapshot because the provisioned composite document was marked truncated: `https://www.supremecourt.gov/DocketPDF/25/25-170/418043/20260803182738077_25-170%20Brief.pdf`.
- CourtListener MCP opinion search for `Hencely v. Fluor Corp.` (SCOTUS, January 1-August 16, 2026): HTTP 429 rate-limit error; no result used.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '146 S. Ct. 1086' --full --limit 3`: returned no match and no `ranged corpus reads` diagnostic; no result used.
- Google and Bing web searches for `Hencely v. Fluor Corp. 146 S. Ct. 1086` returned no usable case material; no result used.
