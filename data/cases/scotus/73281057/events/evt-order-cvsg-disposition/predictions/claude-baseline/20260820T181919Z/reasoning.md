# Reasoning — why P(grant family) = 0.44

## Cell and inputs

CVSG-moment cert cell (`moment: cvsg`), `forward` mode, Term 2025 paid docket
(No. 25-1018). Provisioned snapshot of 2026-06-23 (two distributions, response
requested 3/30/2026 after the State's waiver, BIO filed 5/28/2026, reply filed,
CVSG 6/22/2026). All three provisioned documents carried extractable text and I
read them: the questions presented, the petition (44 pp.), and the brief in
opposition (27 pp.). `record/context.json` freezes `band: high` under
`sal-v3`, `distribution_count: 2`, `cvsg_date: 2026-06-22`, `term: 2025`.

## Anchors

- **Salience band (the scored yardstick).** The statpack's "Segment base rate
  by salience band (sal-v3)" table matches my context's salience version, and
  `high` is a rendered column. Pooling the `high` band's bracketed `reached`
  rates over the Terms strictly before this case's own (2017–2024; the frozen
  band is scored against the risk-set figure): weighted by their bracketed
  denominators (n = 129, 131, 124, 148, 146, 125, 124, 147; total 1074), the
  pooled rate is **≈ 40.9%**.
- **CVSG cut (the moment-specific cut).** "Cert petitions by CVSG status (paid
  scored segment)": CVSG'd petitions resolve granted 29.4% + gvr 5.5% ≈ **35%
  grant family** (n = 163 resolved), against ~6% for the non-CVSG segment.
  This is a terminal-status bucket, not a forward hazard from my state, so I
  read it as confirming the band anchor's neighborhood rather than replacing
  it.

Base rates come from the committed `metrics/statpack.md`; the two corpus
`query` pulls below returned rows with live-poll stamps of 2026-08-16, so the
corpus blob I read is days old, not stale.

## Adjustments from the ~0.41 anchor

**Up:**
- **Divided panel below.** Judge Bea dissented in the Ninth Circuit — a
  classic grant signal, and the petition quotes the dissent's framing
  ("newly minted" test) throughout.
- **Two independent split claims.** QP1 sets the Ninth Circuit against
  *Int'l Dairy Foods v. Amestoy* (CA2) and *NAM v. SEC* (CADC) on whether
  correcting "information asymmetries" alone sustains compelled commercial
  disclosure; QP2 sets it against *Philip Morris v. Reilly* (CA1) and Federal
  Circuit takings doctrine on trade secrets in regulated industries. Either
  could carry a grant alone.
- **Docket trajectory.** The Court itself called for a response after Oregon
  waived, then CVSG'd after effectively one conference look — a fast
  escalation, not a petition limping through relists.
- **Recurring national question with elite counsel.** Repeat-player trade
  association, Arnold & Porter (Allon Kedem, former Assistant to the SG);
  California and Nevada have materially similar statutes, and the
  compelled-disclosure question generalizes to other transparency regimes
  (the cert-stage X.AI amicus signals cross-industry interest).

**Down:**
- **SG-follow risk.** The disposition now runs through the SG's
  recommendation, and the Court usually follows it. The federal government
  administers extensive mandatory reporting regimes of its own and has an
  institutional reason to resist strict scrutiny for "reporting requirements,"
  whatever the administration's sympathy for the trade-secret claim.
- **Vehicle problems the BIO presses.** Both claims travel in a facial
  posture — a hard road after *Moody v. NetChoice*, which the BIO cites — and
  the takings claim has a ripeness shadow (no trade secret has yet been
  published under the public-interest exception; the BIO cites *Nat'l Park
  Hospitality*). A vehicle-based SG deny recommendation is a live path.
- **The BIO's merits framing is respectable.** Oregon argues the panel applied
  *Bolger*/*Central Hudson* to specific facts and that the claimed splits
  dissolve on the cases' facts; that will not stop four Justices who want the
  question, but it gives a cautious SG something to work with.

Net: the ups and downs roughly offset, with the petition's quality signals
slightly outweighing the vehicle risk, so I land a little above the pooled
band anchor: **0.44**. The modal single outcome is still denial, hence
`granted: 0` and `predicted_disposition: denied` with probability 0.44 —
the two fields state one belief.

## Claim-level rationale

- `disposition` 0.44 — restates the top-level probability.
- `relist-increment` 0.97 — the snapshot shows two distributions; a CVSG'd
  petition is mechanically redistributed when the SG files, so the increment
  fails only on settlement, withdrawal, mootness, or an extreme SG delay
  crossing the resolution horizon.
- `cvsg-increment` 0.02 — vacuous by construction on this cell (the CVSG is
  already on the docket; the harness masks it); stated as the near-zero chance
  the record could show a further invitation.
- `summary-disposition-route` 0.06 — conditional on a grant. No intervening
  decision supplies a GVR predicate, and the whole point of a CVSG is plenary
  consideration; a small residual covers an SG-suggested GVR or a
  grant-and-consolidate that resolves in the order.
- `dissent-from-denial` 0.18 — conditional on denial. Well above the
  all-denials base rate because a denial here most likely follows a reasoned
  SG deny in a high-salience compelled-speech case, the setting where
  statements respecting denial cluster; no published baseline exists for this
  claim, so it is banked, and I state it as my honest conditional.

## Uncertainty and discounts

The dominant uncertainty is the SG's recommendation, which is genuinely
unpredictable from this record and swings the posterior hard in both
directions (grant-recommended CVSG petitions are granted at very high rates;
deny-recommended ones mostly die, though not always). Second-order: whether
the facial posture reads to the current Court as a reason to deny or as an
opportunity to say something about facial First Amendment challenges after
*NetChoice*. I did no live CourtListener or web retrieval, so I have not
checked for post-snapshot developments in companion litigation over the
California or Nevada statutes; if a parallel case is further along than I
know, my number is anchored a little too low or too high depending on its
direction. The forecast rests on the provisioned record, the committed
statpack, and two corpus prior pulls.
