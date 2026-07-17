# Retrieval log — scotus/73281673 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Beyond the provisioned inputs (snapshot 2026-07-17, questions-presented.txt,
petition.txt, brief-in-opposition.txt, documents.json) I consulted:

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert disposition split, per-Term
  grant rates, relist and CVSG cuts. (No salience-band table in the committed
  statpack version; anchored on the relist/CVSG/Term cuts instead.)

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "573 U.S. 373" --citation "585 U.S. 296" --citation "466 U.S. 109" --era 2020s --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --citation "138 S. Ct. 2206" --era 2020s --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
3. `uv run fedcourts query --court scotus --topic "Fourth Amendment" --era 2020s --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`

No similar resolved priors surfaced; priors context therefore came from the
statpack alone.

## CourtListener MCP lookups (forward mode — unrestricted)

1. `search(type=o, q='"private search" AND (CyberTip OR NCMEC) AND hash', filed_after=2026-01-01)`
   → 5 results, used to confirm the split's current state: *United States v.
   Nico Lowers* (CA4, 2026-03-10), *United States v. Richard Brillhart* (CA11,
   2026-07-09), *State v. Rauch Sharak* (2026 WI 4), *State v. Gasper* (2026 WI
   3 — the decision below itself, pre-dating the petition; not outcome
   information), *State v. Hill* (Or. Ct. App. 2026).

No web searches. No lookup sought this petition's own disposition (none exists
yet — first post-BIO conference is 9/28/2026).
