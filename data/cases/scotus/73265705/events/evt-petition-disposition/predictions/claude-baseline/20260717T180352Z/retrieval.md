# Retrieval log — scotus/73265705 evt-petition-disposition (claude-baseline, 20260717T180352Z)

## Provisioned inputs read

- `record/snapshots/2026-07-17.json` (docket snapshot, No. 25-1230)
- `record/documents/questions-presented.txt`
- `record/documents/petition.txt` (52 pp., not truncated)
- `record/documents/brief-in-opposition.txt` (35 pp., not truncated)
- `record/documents/documents.json`
- `record/context.json` (mode: forward)
- `events/evt-petition-disposition/event.yaml`

## Corpus tooling

- Committed base rates: `metrics/statpack.md` — "Modern discretionary-cert
  petitions by disposition", "Modern cert petitions by originating circuit"
  (cafc row), "Cert petitions by relist count", "Cert petitions by CVSG
  status", "SCOTUS cert petitions by Term". (No salience-band section is
  present in the committed statpack build.)
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`. Used to
  sanity-check the profile of recently granted petitions (paid,
  multi-distribution, high-salience, repeat-player counsel).

## CourtListener MCP

Forward-mode cell — retrieval unrestricted. Three `search` calls, all against
the docket index (`type: d`, court scotus), checking for companion petitions
raising the same "settled expectations" question and for any other filings in
this case:

1. `q: "settled expectations" "inter partes review"` → 0 results
2. `q: "Cambridge Industries"` → 0 results
3. `q: VirtaMove` → 0 results

CourtListener's docket search does not cover SCOTUS dockets (no PACER/RECAP
coverage), so these were uninformative; no companion-petition signal was
obtained. No result surfaced any disposition of this petition.

## Web searches

None.
