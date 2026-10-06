# Retrieval record

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Pooled the nine displayed strictly prior Terms' baseline reached rates using their published denominators; approximately 5.01%, weighted n=12,720. No remote corpus lookup was made, so no ranged-read transfer line exists.
- Web search queries: `site.supremecourt.gov opinions Holt Hobbs 2015 13-6827 substantial burden` and `site.loc.gov "Lyng" "485 U. S. 439"`. The tool returned no usable results.
- Attempted to open the Library of Congress historical opinion PDF at `https://tile.loc.gov/storage-services/service/ll/usrep/usrep485/usrep485439/usrep485439.pdf`. The tool returned no usable content. No case-specific current docket search was made; no external legal proposition from these attempts was used.
- No CourtListener MCP lookup; no `fedcourts query` or `open-events` call. No lookup of this petition's disposition or subsequent history.
- Local contract/schema reads, path resolution, and output validation are administrative checks rather than substantive retrieval. `uv run fedcourts paths --court scotus --docket 9026000015 --event evt-petition-disposition --role predictor` initially failed on a read-only cache, then succeeded with a writable temporary cache.
