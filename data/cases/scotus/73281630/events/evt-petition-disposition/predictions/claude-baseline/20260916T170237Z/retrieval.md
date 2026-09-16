# Retrieval log

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --topic "First Amendment"`
   - stderr: `ranged corpus reads: 1556 GET(s), 407502848 byte(s)`
   - Result: empty; tool note that 0 SCOTUS rows carry a topic string (topic is a circuit-row field). Coverage gap, not "no precedent."
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   - stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - Result: ten recent granted rows (mostly OT2025 grants from the June 2026 conferences plus several 26A emergency applications). Used only as a sanity check on what recent grants look like on the distribution count (2 to 22 distributions on the cert grants shown); nothing case-specific.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit" (ca6 row), "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `elevated` bracketed reached rate over OT2017 to OT2024).
- `docs/salience.md`: the scorer's feature lattice (relist count, CVSG, originating circuit, petitioner class), to see which record features the frozen band does not already price.

## Web searches (forward cell; both predate the snapshot and neither concerns this case's disposition, which does not yet exist)

1. `L.M. v. Town of Middleborough certiorari denied Alito dissent "Two Genders" shirt 2025`
   - Confirmed: cert denied May 27, 2025 in No. 24-410, dissent by Justice Alito joined by Justice Thomas. Used as a revealed-preference signal about the Court's appetite for student-speech shirt cases.
2. `"Tri County Area Schools" "Let's Go Brandon" Supreme Court petition 25-1143`
   - Surfaced FIRE's case page, a Cornell First Amendment Clinic post on the scholars' amicus (April 30, 2026), a March 31, 2026 commentary post, the CA6 opinion PDF, the Buckeye amicus PDF, and the scholars' amicus PDF on supremecourt.gov. I read only the result summaries, not the linked briefs. Nothing about a disposition appeared, as expected for a petition set for the September 28, 2026 conference.

## CourtListener MCP

Not used. The provisioned petition, BIO, and snapshot were sufficient for the cert-stage read, and the CA6 opinion's holding and dissent are characterized at length, consistently, by both filed briefs.
