# Retrieval

## Corpus and base-rate material

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist-count, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025-Term paid-petition cut (estimated grant rate 0.0536499560).
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic "qualified immunity" --era 2020s --limit 10`.
  - Result: failed before producing any prior rows because DNS resolution for the remote corpus host failed.
  - No `ranged corpus reads: …` line was printed because no ranged read completed.

## CourtListener MCP

- Opinion search: `"reckless creation" "Barnes v. Felix" qualified immunity`, filed May 15, 2025 through July 16, 2026. The sole result was the already provisioned Tenth Circuit decision in *Burke v. Pitts*.
- Opinion search: `Barnes Felix "created the need to use force"`, same date window. The sole result again was *Burke v. Pitts*.
- Opinion search: `Barnes Felix pre-seizure conduct qualified immunity`, same date window. It returned nine published circuit decisions.
- Inspected the CourtListener cluster and opinion endpoint schemas to retrieve only relevant metadata and opinion text.
- Retrieved cluster metadata for *Brittany Ruffin v. Kevin Davis* (Fourth Circuit, cluster 10851363), *Michael Chrestman v. Metropolitan Government of Nashville & Davidson County* (Sixth Circuit, cluster 10672549), and *Tuttle v. Gallegos* (Fifth Circuit, cluster 10881911).
- Retrieved the published opinion text for *Ruffin* (opinion 11318751), *Chrestman* (opinion 11139136), and *Tuttle* (opinion 11349434). *Ruffin* and *Chrestman* applied post-*Barnes* totality review while treating immediate-threat facts and preexisting taser/deadly-force rules as decisive; *Tuttle* found force reasonable in the materially different context of an active gunfight in which several officers had been shot.

No web searches were used, and no search sought this petition's disposition.
