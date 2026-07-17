# Retrieval log — scotus/73274837 evt-petition-disposition (claude-baseline, 20260717T145024Z)

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "New York State Rifle & Pistol Assn., Inc. v. Bruen" --citation "District of Columbia v. Heller" --limit 10`
   - stderr: `ranged corpus reads: 421 GET(s), 110166016 byte(s)`
   - Returned no rows (case-name-style citation strings matched nothing).
2. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "554 U.S. 570" --limit 10`
   - stderr: `ranged corpus reads: 420 GET(s), 109903872 byte(s)`
   - Returned no rows. No usable citation-overlap priors; fell back to the
     committed statpack for base rates.

## Base rates

- Read the committed `metrics/statpack.md` (modern discretionary-cert
  disposition table, relist-count buckets, CVSG cut, per-Term table) and the
  per-Term fee-class detail in `metrics/statpack.json` (Term 2025 paid-class
  grant rate ≈ 5.4%). The statpack build in the repo carries no
  "Segment base rate by salience band" table (checked `statpack.json`
  sections), so anchoring used the relist-count bucket (3+ relists →
  granted ≈ 21.8%) plus the fee-class rate.

## CourtListener MCP

None. The supremecourt.gov docket snapshot (created 2026-07-14) was current
and authoritative for this cell; no MCP calls were needed.

## Web searches (forward mode — unrestricted)

1. `Ninth Circuit Benson magazine ban Second Amendment vacated en banc 2026`
   — identified *Benson v. United States* (D.C. Court of Appeals, not CA9):
   panel struck D.C.'s 10-round magazine limit Mar 5, 2026; en banc rehearing
   granted Apr 22, 2026, vacating the panel opinion — matching the
   supplemental briefs on this docket.
2. `Supreme Court relist "Gator's Custom Guns" 25-153 magazine ban cert`
   — SCOTUSblog case page and relist coverage: ~20 distributions; petition
   passed over at the June 30, 2026 clean-up conference and held to next
   Term (i.e., still undecided — confirms the forward cell is properly
   provisioned); surfaced reports of the assault-weapons-ban cert grants.
3. `Supreme Court grants cert Viramontes v. Cook County assault weapons ban 2026`
   — confirmed (JURIST, The Reload, SAF, Everytown) cert granted in
   *Viramontes v. Cook County* (25-238, CA7) consolidated with
   *Grant v. Higgins* (CA2), argument fall 2026.
4. `SCOTUSblog relist "Gator's" magazine ban Duncan v. Bonta Ocean State Tactical 2026`
   — *Duncan v. Bonta* (25-198) likewise serially distributed (~19 times) and
   held over; commentary reads the magazine petitions as carried pending
   related developments.

No search surfaced any disposition of this petition (none exists); nothing
outcome-revealing was encountered.
