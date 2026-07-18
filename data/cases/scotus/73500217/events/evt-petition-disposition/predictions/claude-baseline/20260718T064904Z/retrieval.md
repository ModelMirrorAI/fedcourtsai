# Retrieval log — scotus/73500217 / evt-petition-disposition / claude-baseline / 20260718T064904Z

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Purpose: profile recent grants for contrast. The five returned grants
     (June 30, 2026 conference: Monsanto ×2, Petersen, Davis, Viramontes) all
     carry 3+ conference distributions and salience scores ≈ 0.4 — the
     opposite docket profile of this zero-relist, waived-response petition.

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert sections: overall grant
  rate ≈ 2.5–3.3% by Term; relist-count cut (0 relists → 0.8% grant); CVSG cut
  (none → 3.0%); originating-circuit cut (ca9 → 3.0%). The salience-band table
  referenced in the prompt is not present in this statpack revision, so I
  anchored on the relist/CVSG/circuit cuts directly.

## CourtListener MCP lookups

1. `search(type=o, q="Crites-Bachert Providence")` — 0 results (the unpublished
   Ninth Circuit memorandum and D. Or. rulings are not in the opinion index);
   relied on the petition's reproduction of the decisions below instead.
2. `search(type=o, q='"360bbb-3" "informed consent" vaccine mandate private right of action')`
   — 0 results (over-constrained phrase query).
3. `search(type=o, q="emergency use authorization informed consent vaccine mandate")`
   — 382 results; top hit was the July 6, 2021 OLC opinion, *Whether Section
   564 of the Food, Drug, and Cosmetic Act Prohibits Entities from Requiring
   the Use of a Vaccine Subject to an Emergency Use Authorization*, confirming
   the consensus reading of § 360bbb-3 against petitioner's theory. No result
   suggested any disposition of this petition (forward cell — none exists).

## Other

No web searches. General background knowledge of the Court's uniform denials
of COVID-vaccine-mandate cert petitions (2021–2024) informed the genre prior;
this is pre-decision context about *other* cases, not retrieval about this
case's outcome.
