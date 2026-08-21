# Reasoning — why these numbers

## The cell

Interim stage, `moment: arrival`, forward mode. Snapshot cutoff 2026-07-30
(provenance `truncated`). Frozen conditioning: `response_requested: true`,
`referred_to_court: false`, `amicus_briefs: 0`, `band: null` — the normal
interim state, so no salience-band anchor exists and I did not derive one. No
`record/documents/` were provisioned; the forecast rests on the snapshot, the
committed statpack, web retrieval for case background, and one corpus query.

## Baseline

The committed statpack's "The interim docket (applications)" section grounds
the scored base rate (its caption states the scored-rate framing, not the
older descriptive-only one). For this Term-2026 application, the strictly
prior application-Terms with resolved substantive applications are OT2025
(178 resolved, 16 granted) and OT2024 (47 resolved, 14 granted): pooled 225
resolved, 30 granted, clearing the pre-registered floor of 50, for a pooled
grant rate of **13.3%**. That is the yardstick this cell is scored against. I
carry the section's own cautions: the escalation-signal counts are
right-censored and not as-at-prediction, and the scored population is
selected higher on the escalation ladder than the pooled cohort behind the
13.3%.

## Adjustments

**Up from 13.3%:**
- A response was requested the same day the application was docketed — the
  strongest interim attention rung, present at arrival.
- The Solicitor General filed a parallel application (26A124) two days
  earlier; the Court's recent disposition of the administration's emergency
  applications has been strongly favorable, and the two applications will
  resolve together.
- Post-CASA skepticism of nationwide injunctions gives the applicants a
  serious scope argument independent of the merits.
- Enormous stakes and heavy institutional attention (five amicus teams on the
  docket by cutoff).

**Down, holding the number at 0.30 rather than higher:**
- The scored claim is P(an *unqualified* grant): the most plausible relief
  shape here is partial (a stay narrowed to non-plaintiff states or to
  discrete provisions of the executive order), and the resolver reads a mixed
  order denial-first. A large slice of the "applicants win something" mass
  therefore resolves as ungranted.
- The merits are unusually weak for an administration application: no textual
  source of presidential authority over election administration, and the
  district court enjoined on constitutional grounds with the First Circuit
  declining interim relief in strong language.
- Election-proximity equities (Purcell's logic) run against the stay: the
  injunction preserves existing mail-voting administration for the November
  2026 midterms, while a stay would force a new federal regime into effect
  months out.
- This cell is the *states'* application specifically; a small residual risk
  that relief issues only on the government's parallel application.

Net: **P(unqualified grant) = 0.30**, `predicted_disposition: denied`,
`granted: 0`. Roughly: outright denial ~40%, partial relief ~27% (resolves
denied), full grant ~30%, withdrawn/dismissed ~2%.

## Claim-by-claim

- `interim-disposition` 0.30 — equals the top-level probability, as required.
- `response-requested-increment` 0.02 — the rung already fired on my record
  (requested 2026-07-29), so the increment is vacuous for this cell and the
  harness masks it; the nominal number reflects that no further first request
  can occur.
- `referral-increment` 0.92 — not yet referred at cutoff; Justice Jackson will
  not resolve an application of this magnitude in chambers. The residual
  covers the docket never recording an explicit referral entry.
- `amicus-increment` 0.97 — frozen count is 0, but five amicus counsel had
  entered appearances by cutoff; filings are near-certain.

## Uncertainty and discounts

- The dominant uncertainty is the shape of relief (full vs. partial), which
  under the denial-first collapse swings the resolved label more than the
  win/lose question does. My 0.30 is soft by ±0.10 on this axis alone.
- The Court's recent emergency-docket behavior post-dates my training
  distribution in part; I weighed its 2025 pattern (strongly
  administration-favorable) from training knowledge plus retrieved coverage,
  and the election-law context distinguishes this from the removal/spending
  cases that pattern was built on. A reader who thinks the pattern transfers
  fully should sit higher, perhaps 0.45; one who weighs Purcell and the merits
  heavily should sit near 0.20.
- Forward-mode retrieval surfaced a post-cutoff headline (Aug 12) about
  another injunction in parallel mail-voting litigation; it did not disclose
  this application's disposition and I did not pursue or fold in any
  post-cutoff outcome material (flagged in `flags.json`).
- The one corpus `query` I ran returned mostly time-extension applications
  (recency-ranked), so priors came from the statpack pool rather than
  retrieved analogues.
