# Retrieval log — scotus/73500245 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Beyond the provisioned inputs (snapshot, petition text, questions presented,
event definition, context.json):

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - stderr: `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
  - Returned 8 recent resolved SCOTUS priors (mix of granted/denied/dismissed);
    generic ranking was not case-specific enough to shift the estimate — no
    attorney-discipline topic filter exists for SCOTUS rows — so the base-rate
    anchoring came from the committed statpack instead.

## Base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (~3% granted), "Cert petitions by relist count" (relist-0: 0.8% granted),
  "Cert petitions by CVSG status", "Petitions by originating court (incl.
  state courts)", "SCOTUS cert petitions by Term" (OT2025 grant rate 2.5%).
- `metrics/statpack.json` — per-Term per-fee-class detail: paid grant rate
  5.4% (OT2025) / 6.9% (OT2024); IFP ~1%.

## CourtListener MCP

None. The provisioned petition text and snapshot were complete, and the case's
posture (distributed for the 2026-09-28 conference, respondent waived
response) needed no live lookup; no search touching this case's disposition
was run.

## Web searches

None.
