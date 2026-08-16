# Retrieval consulted

- Committed base-rate sources: `metrics/statpack.md`, section “The merits docket (granted cases),” and the corresponding merits-baseline cautions in `metrics/README.md`.
- Corpus command: `uv run fedcourts query --court scotus --citation '570 U.S. 1' --citation '584 U.S. 756' --limit 4 --full`. It returned no rows and printed no `ranged corpus reads:` line, so it supplied no substantive prior.
- CourtListener MCP opinion search: `type=o`, `citation=570 U.S. 1`, fields `caseName,dateFiled,citation,absolute_url`, three results. The target result was *Arizona v. Inter Tribal Council of Arizona, Inc.*, filed June 17, 2013.
- CourtListener MCP opinion search: `type=o`, `citation=584 U.S. 756`, fields `caseName,dateFiled,citation,absolute_url`, three results. The target result was *Husted v. A. Philip Randolph Institute*, filed June 11, 2018.
- CourtListener MCP document searches within opinion 902770 (*Inter Tribal Council*): `state-developed forms may require`, `serious constitutional doubts`, `state-developed`, and `accept and use`. The exact first phrase did not match because of document formatting; the shorter search returned the passage distinguishing state-developed forms from the Federal Form, and the other searches returned the constitutional-doubt and Federal Form sufficiency passages.
- CourtListener MCP document searches within opinion 4506000 (*Husted*): `two main objectives` and `objectives`. Neither matched the short cached document, so no Husted text informed the forecast beyond the provisioned filings' description of the case.

No web search was used, and no material about this case's future judgment or merits opinion was sought or encountered.
