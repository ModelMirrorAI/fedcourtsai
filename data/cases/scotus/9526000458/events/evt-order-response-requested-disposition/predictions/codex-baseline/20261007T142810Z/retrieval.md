# Retrieval

- Read the committed `metrics/statpack.md` interim-docket section and `metrics/statpack.json` interim rows. Used `jq` to pool application Terms 2016–2025: 31/296 = 0.10472972972972973. Read the pack's last-change commit with `git log -1 --format='%h %cI' -- metrics/statpack.md`: `808f812e9`, September 28, 2026, 12:02:50 UTC. This identifies the committed artifact's vintage, not the underlying corpus's newest pull.
- Attempted a general web search for `site.supremecourt.gov injunction pending appeal "indisputably clear" "All Writs"`; no usable result was retained from that call. It did not name this case or request its outcome.
- Attempted two web opens of the Cornell LII Supreme Court text for *Hobby Lobby Stores, Inc. v. Sebelius*, No. 12A644, December 26, 2012. No usable response was visible from those calls. Subsequently retrieved the public Cornell page with shell `curl`, removed HTML tags, and searched for the date, All Writs Act, and injunction-standard passages. That shell retrieval confirmed the opinion text used for the distinction between an injunction pending appeal and a stay. This historical decision concerns different parties and supplied general procedural context only.
- Attempted an official Supreme Court PDF path for that historical opinion, `12a644_k53l.pdf`; no usable response was visible and it supplied no evidence.
- No `fedcourts query` or `open-events` retrieval and no CourtListener MCP lookup. Consequently there are no ranged-corpus transfer lines to report.
- The path-resolution command used the supplied literal identifiers. Its first invocation could not initialize the default read-only uv cache; retrying with a temporary writable cache succeeded. No credential access or direct CourtListener REST fallback was attempted.

No current docket lookup, disposition search, or subsequent-history search was performed for K.M.K.'s application. Provisioned inputs are identified in `reasoning.md`.
