# Retrieval log — scotus/73280412 · evt-petition-disposition · claude-baseline · 20260716T205846Z

Forward-mode cell (`record/context.json`: `forward`) — retrieval unrestricted. The
petition itself is undecided (distributed for the 9/28/2026 conference, after this run's
date), so no search below could surface this case's own disposition; none did.

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --topic redistricting --limit 8`
   → no rows returned.
   stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --citation "600 U.S. 1" --citation "585 U.S. 969" --citation "602 U.S. 1" --limit 8`
   (Moore v. Harper / Covington / Alexander as citation hooks) → no rows returned.
   stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`

Base rates taken from the committed `metrics/statpack.md` and `metrics/statpack.json`
(Term-2025 paid-class grant rate ≈ 5.4%; relist/CVSG cuts; no salience-band section is
present in the committed statpack).

## CourtListener MCP lookups

None — the SCOTUS docket facts came from the provisioned snapshot, and the external
questions (Callais, Trevino) were news/orders questions better answered on the open web.

## Web searches and fetches (engine-surfaced)

1. WebSearch: `Louisiana v. Callais Supreme Court decision June 2026 Voting Rights Act Section 2`
   → decided 4/29/2026, 6–3 (Alito): §2-driven majority-minority map held an
   unconstitutional racial gerrymander; §2 sharply narrowed.
2. WebSearch: `Trevino v. Hobbs certiorari Supreme Court Washington redistricting Soto Palmer`
   → companion petition pending; Washington urged the Court to grant (6/2/2026); district
   court denied a post-Callais bid to toss the remedial map (5/18/2026).
3. WebFetch: `https://washingtonstatestandard.com/2026/06/02/wa-urges-us-supreme-court-to-take-redistricting-case/`
   → HTTP 403, not retrieved.
4. WebFetch: `https://en.wikipedia.org/wiki/Louisiana_v._Callais`
   → holding details; Court GVR'd Mississippi and North Dakota redistricting cases on
   5/18/2026 for reconsideration under Callais.
5. WebFetch: `https://thearp.org/litigation/trevino-v-hobbs/` → HTTP 404.
6. WebSearch: `Trevino v. Hobbs Supreme Court docket "25-" petition distributed conference 2026`
   → Trevino is No. 25-918; motion to expedite filed 5/15/2026; parallel briefing
   completed 6/10/2026 (same day as Garcia's reply).
7. WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-918.html`
   and `https://www.supremecourt.gov/orders/courtorders/052626zor_6j36.pdf`
   → both HTTP 403 via the fetch tool; the order list was instead downloaded with
   `curl` and text-extracted locally (pypdf):
   **Order list 5/26/2026 (608 U.S.): "25-918 TREVINO, JOSE A., ET AL. V. HOBBS, SEC. OF
   STATE WA, ET AL. — The motion of petitioners to expedite consideration is denied."**
   No order in 25-901 on that list.

Total: 2 corpus queries + 3 web searches + 4 fetch attempts (2 successful) + 1 curl
download — within the ~25-call budget.
