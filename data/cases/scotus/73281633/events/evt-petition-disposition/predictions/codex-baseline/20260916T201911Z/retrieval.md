# Retrieval record

- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit cuts, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table.
- Read matching segment fields in `metrics/statpack.json` and computed the baseline reached pool over displayed Terms 2017–2024: numerator 593, weighted resolved denominator 11,580, rate 0.05120898100172712. Inspected aggregate coverage metadata, not individual case outcomes.
- Used `git log -1 --format='%h %cI' -- metrics/statpack.json` to identify artifact vintage: `55121cdb8`, September 14, 2026 at 11:02 UTC. This is not a corpus-pull freshness measurement.
- Web search: `site.supremecourt.gov Rule 10 considerations governing review on certiorari erroneous factual findings misapplication properly stated rule law`. No usable results were returned.
- Web open: `https://www.supremecourt.gov/ctrules/2019RulesoftheCourt.pdf`. No usable content was returned. No rule text from this attempt informed the forecast.
- No CourtListener MCP calls, no `fedcourts query` or `open-events` calls, and no ranged corpus reads. No case-outcome or subsequent-history retrieval.
- Local contract/schema/path/serialization reads and path-resolution commands supported artifact construction only. `uv run fedcourts paths --court scotus --docket 73281633 --event evt-petition-disposition --role predictor` first failed on a read-only default cache and succeeded after selecting a temporary writable cache.

The provisioned inputs used are identified separately in `reasoning.md`; the unprovisioned reply and amicus texts were not retrieved.
