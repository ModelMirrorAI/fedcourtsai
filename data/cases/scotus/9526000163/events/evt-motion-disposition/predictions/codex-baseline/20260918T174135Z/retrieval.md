# Retrieval beyond the provisioned inputs

- Read `metrics/statpack.md`, specifically the interim-docket section, and the corresponding `interim` object in `metrics/statpack.json`. Pooled application terms 2016–2025 using `jq`: 31 substantive grants / 296 substantive resolutions. The displayed current-Term row was excluded from the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to establish the committed pack's vintage: `55121cdb8`, `2026-09-14T11:02:00Z`.
- Web search: `site.supremecourt.gov opinions 2009 Hollingsworth Perry 09A648 stay reasonable probability fair prospect irreparable harm`. The tool returned no usable content.
- Web search: `site.supremecourt.gov "Hollingsworth" "fair prospect" "2010"`. The tool returned no usable content.
- Attempted web opens of the historical official opinion at `https://www.supremecourt.gov/opinions/09pdf/09A648.pdf` and bound volume at `https://www.supremecourt.gov/opinions/boundvolumes/558bv.pdf`. Neither returned usable content.
- CourtListener MCP `search`: `{"type":"o","citation":"558 U.S. 183","num_results":1}`. Failed: `Upstream CourtListener request failed: [Errno 104] Connection reset by peer`. No opinion or search result was received. No REST fallback was attempted.

No `fedcourts query` or `open-events` lookup was made, so there is no ranged-corpus transfer line to report. The `fedcourts paths --court scotus --docket 9526000163 --event evt-motion-disposition --role predictor` command only resolved local paths. Its first invocation encountered an unwritable default cache; retrying with a temporary cache succeeded.

No search targeted this case, its subsequent history, or its outcome. No outcome-revealing material was retrieved. Supplemental legal retrieval failed, so it supplied no substantive evidence.
