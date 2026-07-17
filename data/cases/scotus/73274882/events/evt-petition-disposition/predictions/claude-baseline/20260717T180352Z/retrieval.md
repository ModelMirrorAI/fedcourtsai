# Retrieval log — scotus/73274882 evt-petition-disposition (claude-baseline, 20260717T180352Z)

## Provisioned inputs (read first)

- `record/snapshots/2026-07-17.json` (docket refreshed 7/14/2026)
- `record/documents/questions-presented.txt`, `petition.txt` (truncated at 356 pp.), `brief-in-opposition.txt`, `documents.json`
- `events/evt-petition-disposition/event.yaml`, `record/context.json` (mode: forward)

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  — `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3`
  — `ranged corpus reads: 145 GET(s), 37879808 byte(s)`
  — used to confirm that grants from the 6/29/2026 mop-up conference issued on
  6/30/2026 (e.g., Monsanto 24-1097/24-1098), establishing that Duncan was
  affirmatively carried over the recess rather than awaiting a delayed order.
- Committed `metrics/statpack.md` — modern cert base rates, relist-count cut
  (3+ relists → 21.8% granted), originating-circuit cuts, per-Term table. The
  salience-band table referenced in the prompt is not present in the committed
  statpack.

## CourtListener MCP

- None. The MCP server was available, but the open questions (identity of
  "Benson", Wolford outcome, circuit-court posture) were faster to resolve via
  web search; the docket snapshot was already current to 7/14/2026.

## Web searches / fetches (forward mode — unrestricted)

1. Search: `Duncan v. Bonta supplemental brief "Benson" Supreme Court 25-198`
   — identified Benson v. United States (D.C. Court of Appeals, 3/5/2026 panel)
   striking D.C.'s 10-round magazine cap; located both parties' supplemental
   filings and relist commentary.
2. Fetch: supremecourt.gov PDF of respondent's 4/23/2026 letter re Benson —
   HTTP 403, not retrieved (content confirmed via search 3 instead).
3. Fetch: calgunlawyers.com "19 Relists and Counting" (June 2026) — relist
   count, Ryan v. Hurles record (~22), outcome scenarios.
4. Search: `"Benson v. United States" magazine ban D.C. Court of Appeals 2026
   rehearing en banc` — confirmed 4/22/2026 en banc grant vacating the panel
   opinion (the subject of respondent's 4/23 letter).
5. Search: `Wolford v. Lopez Supreme Court decision June 2026` — decided
   6/25/2026, 6–3 (Alito, J.), striking Hawaii's private-property carry rule.
6. Search: `Duncan v. Bonta relist July 2026 cert petition long conference
   magazine ban` — status commentary; companion petitions context.
7. Fetch: SCOTUSblog "Déjà vu all over again" (March 2026 Relist Watch) —
   Duncan relist tally and companion arms-ban petitions (Gator's Custom Guns
   25-153, NAGR v. Lamont 25-421, Grant v. Higgins 25-566).
8. Search: `Third Circuit en banc decision 2026 New Jersey magazine ban
   "Association of New Jersey Rifle" Platkin assault weapons` — en banc still
   pending; 7/6/2026 order invited supplemental briefs on Wolford and Hemani
   (due 7/10/2026).

No search surfaced any disposition of this petition (none exists); all
retrieved material predates the snapshot.
