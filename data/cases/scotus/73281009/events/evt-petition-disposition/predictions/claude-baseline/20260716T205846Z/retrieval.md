# Retrieval log — scotus/73281009 / evt-petition-disposition / claude-baseline / 20260716T205846Z

## Provisioned inputs read

- `record/snapshots/2026-07-16.json` (baseline snapshot)
- `record/documents/questions-presented.txt`, `petition.txt`,
  `brief-in-opposition.txt`, `documents.json`
- `events/evt-petition-disposition/event.yaml`, `record/context.json`
  (mode: forward)

## Corpus tooling

- `metrics/statpack.md` (committed) — anchors used: "Cert petitions by CVSG
  status" (cvsg: granted 27.1%, denied 71.2% of 59 resolved; none: granted
  3.0%), modern discretionary-cert base rate, ca3 originating-circuit cut
  (granted 2.9%), relist buckets, per-Term rates (2023–2025 grant 2.5–3.3%).
  Also checked `metrics/statpack.json`: no salience-band section present in
  this statpack build.
- `uv run fedcourts query --court scotus --citation "Burdick v. Takushi"
  --citation "Anderson v. Celebrezze" --citation "Crawford v. Marion County
  Election Board"` — 0 rows returned.
  `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
- `uv run fedcourts query --court scotus --citation "Crawford v. Marion"` —
  0 rows returned.
  `ranged corpus reads: 418 GET(s), 109576192 byte(s)`

## CourtListener MCP

None used (the provisioned snapshot and filed-document texts covered the
docket record; no MCP calls were needed).

## Web searches (forward mode — unrestricted; used for related-case signal only)

1. "Baxter v. Philadelphia Board of Elections Pennsylvania Supreme Court
   decision date requirement mail ballots" — confirmed Baxter (Pa. Free and
   Equal Elections Clause challenge to the same date requirement) was granted
   allocatur Jan. 17, 2025 and argued Sept. 10, 2025; no decision surfaced.
   Sources: votebeat.org, aclu.org, statecourtreport.org, statesunited.org.
2. "Pennsylvania Supreme Court Baxter ruling 2026 undated mail ballots 'free
   and equal'" — same conclusion: still pending as of this run; the mootness
   risk is live but unrealized.
3. "Supreme Court solicitor general views CVSG Pennsylvania v. Eakin RNC
   25-962 mail ballot date requirement June 2026" — confirmed the June 29,
   2026 CVSG covers both No. 25-962 (RNC v. Eakin) and No. 25-967, and that
   contemporaneous commentary (Election Law Blog, Democracy Docket,
   PoliticsPA) reads the CVSG as a strong grant signal. No disposition of this
   petition surfaced (none exists).
