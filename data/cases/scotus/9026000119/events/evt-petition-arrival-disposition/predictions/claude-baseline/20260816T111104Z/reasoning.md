# Rationale — P(grant) = 0.06

## The cell

Arrival-moment cert cell, forward mode. Snapshot (2026-08-16) shows the
docketed petition (July 27, 2026), the Kagan-granted extension (linked
application 25A1260), and nothing else — zero distributions, no CVSG, exactly
as the moment's definition requires. Frozen context: `band: state` under
`sal-v3`, `distribution_count: 0`, Term 2026, paid case. Provisioned documents:
the full petition (98 pages, clean text) and its QP section; no brief in
opposition exists yet (response due August 26, 2026), so my read of the
opposition is anticipation, not text.

## Anchors

- The statpack's band table (sal-v3, matching my context's `salience_version`)
  is the committed yardstick for a frozen `state` band: the bracketed
  `reached` rate pooled over Terms strictly before 2026 (OT2017–OT2025) is
  ≈ **36.6%** (n ≈ 1425).
- That figure needs care at this moment. The risk sets are nested, so the
  `state` reached pool contains everything above it — federal-caption
  petitions (grant ≈ 50–90% per Term) and every petition that climbed into
  `high` via relists or a CVSG. The state-caption class itself, read from the
  band's own terminal figures (docs/salience.md: per-Term 4–30%, pooled 17.5%
  over the four floored Terms, plus its strongest members who leave for
  `high`), grants at roughly **15–25% at arrival**. That is my class prior.
- The arrival-moment guidance's whole-segment fallback (the weakest band's
  bracketed rate, ~5–8%) is the floor for an unbanded arrival; my cell carries
  a frozen band, so I treat ~20% as the class anchor and adjust from case
  specifics.

## Adjustments (down, hard)

1. **No conflict.** The petition's own framing gives this away: it asks that
   federal jurisprudence "should be extended to state and territorial courts."
   Its authorities are district-court decisions (Bullock v. Carver, D. Utah;
   Sierra Melendez, D.P.R.) and one Tenth Circuit case — no split among
   circuits or courts of last resort is alleged, and my CourtListener check
   found no SCOTUS precedent line on summary disqualification of a prosecuting
   office. State-band grants are overwhelmingly split-driven; this is the
   single largest discount.
2. **Doctrinal defect in the theory.** The petitioner is a government claiming
   Fourteenth Amendment due-process and equal-protection rights for "the
   People of Guam." A government entity is a very awkward due-process
   claimant, and the cert pool will say so. The Organic Act overlay
   (48 U.S.C. § 1421b) complicates rather than cures this.
3. **Fact-bound vehicle.** Unreported orders below, a one-case disqualification
   dispute entangled with Guam-law prosecutorial-authority statutes, and a
   plausible adequate-territorial-ground problem.
4. **In-house drafting.** The Guam AG's office, not a Supreme Court
   practitioner; the state-band class rate is carried by state SG offices
   filing selectively on developed splits.

## Adjustments (up, modestly)

- The facts are stark: an entire elected prosecuting office disqualified —
  the petition says without notice — and a public-corruption prosecution
  dismissed with prejudice, with an "evades review" structure. The subject has
  national resonance after recent high-profile DA-disqualification fights.
- The Court does occasionally take territorial-governance cases from the
  Supreme Court of Guam (Limtiaco v. Camacho, 2007), and a government
  petitioner reliably gets a careful pool read.

Net: ≈ 0.20 class prior × heavy within-class discounts ≈ **0.06**. Even the
band's weak-year terminal rates (4–8%) bracket this from below, which is
where I judge this petition to sit within its class.

## The other claims

- **relist-increment 0.97** — from a zero-distribution state this resolves
  true if the petition is ever distributed. A paid petition in a live
  prosecution dispute will reach a conference unless dismissed or withdrawn
  first (~2–3% combined, from the modern-cert dismissed share).
- **cvsg-increment 0.02** — near the paid-segment CVSG base (~1.3%,
  173/13,596), nudged up marginally for the federal territorial interest.
- **summary-disposition-route 0.12 (| grant)** — the population's cert-order
  share of grants is high (GVRs), but a GVR needs an intervening decision and
  none is plausible here; conditional on this case being granted, plenary
  review dominates.
- **dissent-from-denial 0.04 (| denial)** — no published baseline; slightly
  above my unconditional sense of the paid-docket rate for the institutional
  stakes. Banked honestly.

## Uncertainty and discounts

- Largest: my within-class quality read. If the no-notice facts are as clean
  as the petition presents and a competent amicus effort materializes, the
  relist and grant chances are meaningfully higher than 6%.
- The BIO does not exist yet; respondents' framing (and any territorial-law
  alternative ground) could make the vehicle look even worse, or the absence
  of opposition could let the petition's narrative stand.
- The frozen-band yardstick (~37%) sits far above my number by construction —
  the reached pool is dominated by high-band climbers and federal petitions.
  I am deliberately far under it; if this class of arrival-time state-band
  cells systematically grants near the reached rate, I am miscalibrated.
- Retrieval was light (one corpus query, two CourtListener searches); the
  corpus query surface ranks by recency without free text and returned nothing
  similar, so priors came from the statpack and the salience doc's published
  figures.
