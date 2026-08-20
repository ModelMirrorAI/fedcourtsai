# Reasoning — why P(grant) = 0.80

## The anchor

This is an arrival-moment cert cell (`moment: arrival`): forecast at docketing,
before any distribution exists. `record/context.json` freezes `band: federal`
under `sal-v3`, which matches the salience version of the committed statpack's
"Segment base rate by salience band (sal-v3)" table, so that table is my
anchor on the bracketed `reached` figures, as the prompt directs for a frozen
band. Pooling the `federal` column's bracketed rates over every rendered Term
strictly before this case's OT2026 (OT2017–OT2025, the table's full rendered
window): weighted grants ≈ 143.0 over n = 201, a pooled **federal-band
grant-family rate of ≈ 71%**. That is the published anchor for the
federal-petitioner arrival class — the one arrival-time class measured far
above the docket's — and it matches the band cut elsewhere in the pack
(federal: granted 48.8% + gvr 22.4% ≈ 71% grant family). I did not use the
relist-0 cut (terminal-state figure; understates an arrival's future) or the
modern-cert overall rate (~2–3%; wrong population for an SG petition).

## Adjustments from the anchor: up to 0.80

Upward, this petition is stronger than the median federal-band petition:

- **The SG's institutional selection is at its maximum.** This is not a
  routine government petition but the administration's chosen vehicle on the
  constitutional core of its mass grant-termination program, filed by the
  Solicitor General personally with an express plenary ask and a developed
  vehicle section (single QP, sole ground of affirmance below, "no disputed
  facts," Tucker Act deliberately not pressed as to this claim).
- **Recurring question with enormous stakes.** The petition catalogues a
  dozen-plus parallel suits across at least five circuits and claims ~$200B/yr
  of competitive grantmaking is affected; a nationwide class has already won a
  permanent injunction on overlapping grants (S.D.N.Y., appeals pending).
  Percolation is happening *now*, which cuts toward taking the first clean
  vehicle rather than waiting.
- **Forward signal predating the snapshot:** the Court's receptivity to the
  government in the 2025 grant-termination emergency cases (the April 2025
  Department of Education v. California stay and the August 2025 NIH v. APHA
  partial stay, both known from general legal context, not retrieved) shows at
  least five Justices already engaged with — and skeptical of lower-court
  interference in — this exact program area.
- **Ninth Circuit origin** for a government petition, historically a
  favorable reversal posture.

Downward:

- **Interlocutory posture.** The decision below affirms a preliminary
  injunction; a minority path is denial (or a hold) pending final judgment,
  though the Court has repeatedly granted this administration's petitions from
  preliminary postures.
- **The lurking Tucker Act question.** Several Justices in the 2025 stay
  litigation preferred a channeling/jurisdictional resolution; that could
  complicate the vehicle or prompt a hold for a cleaner case, though it could
  equally be folded into a grant.
- **Recent-Term dilution of the federal band**: the two most recent Terms run
  52–60% against the pooled 71%, consistent with the SG filing more petitions
  (n=21 in OT2025 vs. 11–17 in most earlier Terms), so the pooled anchor may
  overstate the current class. This tempers how far above the anchor I go.

Net: 0.80 — above the ~71% pooled anchor because this petition sits well above
its class median on every observable cert signal, but held below the high-80s
the strongest historical Terms would suggest, out of respect for the
interlocutory posture and the recent-Term dilution.

## The other claims

- **relist-increment 0.97**: from a zero-distribution record, this is P(ever
  distributed); only a pre-conference dismissal/withdrawal defeats it, and the
  government will not abandon its own flagship petition.
- **cvsg-increment 0.01**: the United States is the petitioner; a CVSG calls
  for views already before the Court. Near-zero, not zero, only for record
  oddities.
- **summary-disposition-route 0.08** (conditional on grant): no intervening
  decision supports a GVR; a summary reversal is conceivable but the question's
  breadth points to plenary treatment. Stated as the conditional, per the
  contract.
- **dissent-from-denial 0.30** (conditional on denial): a denial here would
  likely be vehicular (posture/percolation), which often passes in silence,
  but Thomas or Alito noting a dissent on a flagship government petition is a
  live possibility. No published baseline; banked honestly.

## Uncertainty and discounts

The main uncertainty is timing-shape, not direction: whether the Court grants
this petition or holds it briefly for (or consolidates it with) a parallel
vehicle. My anchor arithmetic is from the committed statpack (its per-Term
table renders 10 of 10 Terms, so the rendered window is the full pool); the
corpus blob behind it was not re-read for this cell beyond one `fedcourts
query` that returned no rows (sparse citation coverage — a known gap, noted on
stderr). The petition text is provisioned but `truncated: true` at 155 pages;
I read the QP, introduction, statement, reasons-for-granting, and the Ninth
Circuit/district-court excerpts, which is the material a cert call turns on.
My knowledge of the 2025 emergency-docket grant cases comes from general
legal context predating the snapshot, used as forward signal per the
forward-mode rule; I did not retrieve anything about this case's own
disposition, which cannot exist — the petition was docketed the day before
this run's snapshot.
