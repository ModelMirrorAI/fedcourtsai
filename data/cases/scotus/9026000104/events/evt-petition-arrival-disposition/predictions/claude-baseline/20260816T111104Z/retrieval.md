# Retrieval log — claude-baseline / 20260816T111104Z

Forward-mode cell; retrieval unrestricted. Consulted beyond the provisioned
inputs:

## Committed statpack

- `metrics/statpack.md` — "Segment base rate by salience band (sal-v3)"
  (federal column, Terms 2017–2025 pooled), "Cert petitions by salience band",
  "Modern discretionary-cert petitions by disposition", relist-count and CVSG
  cuts.

## CourtListener MCP

1. `search` (opinions, q="Barbosa da Cunha") — surfaced the 2026 sister-circuit
   opinions citing the decision below (CA7 *Rojas v. Olson*, CA9 *Rodriguez
   Vazquez v. Bostock*, CA10 *Quiroz v. Mullin*, CA1 *Guerrero Orellana v.
   Moniz*, CA2 *Ohindo v. Ball*).
2. `search` (opinions, q="da Cunha" Rhoney, court=ca2) — 0 results.
3. `search` (opinions, q="Barbosa da Cunha", court=ca2) — 1 result (*Ohindo*).
4. `search_document` on cluster 10936117 — 404 (cluster id, not opinion id).
5. `search` (opinions, q="Barbosa da Cunha", fields incl. `opinions`) — got
   opinion ids for the citing decisions.
6. `search_document` (opinion ids 11404410, 11404233, 11415407, query "Barbosa
   da Cunha") — citing passages establishing the QP (§ 1225(b)(2)(A) vs
   § 1226(a) for interior arrests of noncitizens present without admission),
   the 7–2 circuit split, the decision below's reporter cite (175 F.4th 61,
   decided Apr. 28, 2026), and the companion petition *Raycraft v.
   Lopez-Campos*, No. 25-1415.
7. `call_endpoint` (dockets, court=scotus, docket_number=25-1415) — companion
   petition docketed 2026-06-24, `date_terminated: null` (still pending).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted` —
  20 recent granted SCOTUS priors (context on recent grant shapes; not
  otherwise load-bearing). Run twice (second run to capture the transfer
  line); stderr both ways from the warm service cache:
  `ranged corpus reads: 0 GET(s), 0 byte(s)`

No web searches beyond the above. I did not query this petition's own
disposition or subsequent history.
