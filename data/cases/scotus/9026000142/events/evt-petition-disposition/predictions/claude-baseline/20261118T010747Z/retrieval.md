# Retrieval log

Provisioned inputs read: snapshot, context.json, same-question.json, event.yaml, record/documents/* ; committed `metrics/statpack.md` (band table, relist/CVSG/amicus cuts).

Corpus:
- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --docket-number 26-141` — companion petition row (Trump v. Carroll; open, one distribution, conference 2026-12-04). `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 25-573` — Carroll II row (denied 2026-06-29, distribution_count 16). `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — rejected: `Unknown era 'modern'` (usage error; not re-issued, since generic granted priors would add nothing over the statpack).

Web:
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-573.html` — the Court's docket for the earlier, already-decided sibling case No. 25-573: about fifteen "Rescheduled" entries Feb.–June 2026, "Petition DENIED" June 29, 2026 with no dissent noted, rehearing denied Aug. 17, 2026. This is not the docket being predicted.

CourtListener MCP: not used. No web search run. No forecast of this case surfaced.
