# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: rejected as a usage error (era must be a decade token). No corpus read.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`: `ranged corpus reads: 31 GET(s), 8060928 byte(s)`. Five recent GVR priors, unrelated subject matter; used only for general shape.
- `uv run fedcourts query --court scotus --docket-number 26-572 --include-open`: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`. This docket's own open row; no new information.
- CourtListener MCP `search`: call failed (invalid argument `query`). Not retried.
- WebSearch "Rojas Seventh Circuit 25-3127 ICE detention": identified *Cirrus Rojas v. Olson* (CA7, July 30, 2026; reversed and remanded; holding that § 1226, not § 1225, governs detention, so a bond hearing is available).
- WebSearch on the § 1225(b)(2) circuit split and certiorari: a 9–2 circuit split; certiorari granted Oct 1, 2026 in *Rhoney v. Barbosa da Cunha*.
- WebFetch jurist.org article on that grant: 403 Forbidden.
- WebSearch on the October 2026 grant: confirmed *Rhoney v. Barbosa da Cunha* and its question presented.

No search result claimed this petition's own disposition.
