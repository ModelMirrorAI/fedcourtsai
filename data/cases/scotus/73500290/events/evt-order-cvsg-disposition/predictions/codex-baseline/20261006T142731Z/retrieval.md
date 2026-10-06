# Retrieval record

- Read the provisioned event definition, snapshot dated 2026-10-06, conditioning context, document manifest, questions presented, and selected substantive petition/appendix and opposition passages. These are baseline inputs, not external retrieval.
- Read `metrics/statpack.md`: modern discretionary-cert totals, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. Read the corresponding structured Term rows in `metrics/statpack.json` and calculated the high-band pool for Terms 2017–2024 locally: 314 weighted grants / 898 weighted resolved petitions.
- Web search attempted: `site.supremecourt.gov opinions Apple v Pepper 2019 Illinois Brick direct purchasers`. The tool returned no usable results or source text.
- Web open attempted for the preexisting Apple v. Pepper opinion: `https://www.supremecourt.gov/opinions/18pdf/17-204_bq7d.pdf`. The tool returned no usable source text. The forecast does not rely on a successful external read of that opinion.
- No CourtListener MCP calls and no corpus `query` or `open-events` calls. There are no ranged-corpus transfer lines to report. No search for this case's disposition or subsequent history was performed.
- Ran the prescribed `fedcourts paths` command. The first `uv run` attempt failed because its default cache directory was read-only; rerunning with a cache under `/tmp` succeeded. Schema and artifact validation are local contract checks, not additional case retrieval.
