# Retrieval log

- Read the committed metrics/statpack.md modern-cert, paid-segment relist and CVSG, and sal-v4 band sections. Calculated the prior-Term elevated reached-rate approximation locally from displayed Terms 2017-2024: weighted n=2,810 and approximately 17.24%. No corpus query or open-events lookup was made; no ranged-corpus transfer line was produced.
- Ran `uv run fedcourts paths --court scotus --docket 73500225 --event evt-petition-disposition --role predictor`. The default cache was read-only; reran successfully with a writable temporary uv cache. This resolved paths and did not read a case outcome.
- Web search: `site.supremecourt.gov opinions Wolford Lopez 2026 24-1046`. The tool returned no usable content.
- Web search: `site.supremecourt.gov Bruen sensitive places 2022 opinion`. The tool returned no usable content.
- Attempted to open the official Bruen opinion at `https://www.supremecourt.gov/opinions/21pdf/20-843_7j80.pdf`. The tool returned no usable content.
- No CourtListener MCP lookup was made. No external result was relied on, and no search sought this petition's disposition or subsequent history.

All substantive filing references are to the provisioned petition and brief in opposition, including the opposition's account of the distinct Wolford and Moore v. Kipke proceedings. The snapshot and context were the sole sources for the target petition's procedural state.
