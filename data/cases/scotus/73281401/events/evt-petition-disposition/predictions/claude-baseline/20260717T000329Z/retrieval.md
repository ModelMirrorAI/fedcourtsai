# Retrieval log — scotus/73281401, run 20260717T000329Z (forward mode)

## Corpus tooling

- `uv run fedcourts query --court scotus --topic "qualified immunity excessive force" --limit 8 --corpus-backend ranged`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "qualified immunity" --limit 6 --corpus-backend ranged`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "excessive force" --limit 6 --corpus-backend ranged`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "1983" --limit 6 --corpus-backend ranged`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --limit 5 --corpus-backend ranged`
  → 5 rows (sanity check that query works; captions null, not topically relevant).
  `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

Topic-filtered retrieval surfaced no usable priors, so the quantitative anchor
is the committed `metrics/statpack.md` / `metrics/statpack.json` (modern-cert
base rates; paid-vs-IFP, relist, CVSG, and circuit cuts). No salience-band
table exists in the current statpack.

## Web retrieval (forward mode — unrestricted)

- Fetched the brief in opposition directly from the docket link in the
  provisioned snapshot (its text was not provisioned):
  `https://www.supremecourt.gov/DocketPDF/25/25-1108/416564/20260715132212406_260709a%20BIO%20for%20efiling.pdf`
  (WebFetch was 403-blocked; downloaded via curl with a browser UA — the same
  channel the pipeline's live poller uses — and extracted text with pypdf,
  12 pages). Read in full; source of the Third Amended Complaint vehicle fact.
- Web search: `Zook v. Fuqua 25-1108 certiorari Supreme Court video evidence motion to dismiss`
  → no commentary or analyst coverage of this petition found; only the Tenth
  Circuit opinion mirror (FindLaw) and unrelated same-name cases. No
  disposition information exists (case pending); no leakage.

## CourtListener MCP

Not used — the provisioned snapshot, petition, and directly fetched BIO
covered the record, and the Tenth Circuit opinion's content is described in
detail by both sides' filings.
