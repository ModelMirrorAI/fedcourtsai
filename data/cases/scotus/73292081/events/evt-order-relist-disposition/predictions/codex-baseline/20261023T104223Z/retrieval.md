# Retrieval record

- Consulted the committed `metrics/statpack.md` modern-cert, paid-segment relist/CVSG, and sal-v4 per-Term band sections, with `metrics/statpack.json` for exact pooled arithmetic. No live corpus lookup was made; there is no ranged-corpus-read transfer line.
- Web search: `site.supremecourt.gov "Bowe" "2026" "2244"`. The tool returned no usable content.
- Web open, attempted twice: `https://www.supremecourt.gov/opinions/25pdf/24-5438_o7kq.pdf`. This was an unverified candidate URL, not a successfully retrieved opinion; no usable content was returned.
- Web searches: `site.supremecourt.gov "Newberry" "25-862"` and `site.supremecourt.gov "Bowe v. United States" "2026"`. No usable content was returned.
- No CourtListener MCP lookup or live corpus query. No search for this case's own disposition or later history. No outcome material was surfaced.
- Local contract and tooling references: `AGENTS.md`, `.github/prompts/predict.md`, the prediction/tooling/flags JSON schemas, `fedcourts paths`, and the path and serialization helpers. The initial path command could not open the default uv cache; setting `UV_CACHE_DIR` to a writable temporary directory resolved it.
