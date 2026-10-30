# Retrieval log

- `uv run fedcourts query --court scotus --era modern --include-applications --limit 8`: usage error (`modern` is not a valid era; the valid values are decades). No rows returned.
- `uv run fedcourts query --court scotus --era 2010s --include-applications --disposition denied --limit 8`: `ranged corpus reads: 191 GET(s), 50069504 byte(s)`. It returned generic denied cert petitions (e.g. Dignity Health v. Minton) and no capital stay applications, so it was not informative.
- I read the committed `metrics/statpack.md` interim-docket section.
- I made no CourtListener MCP calls and no web searches. I deliberately did not look up linked petition 16-8909 or this application's outcome.
