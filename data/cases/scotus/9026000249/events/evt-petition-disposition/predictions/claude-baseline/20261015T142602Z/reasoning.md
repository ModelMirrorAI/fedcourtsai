# Rationale: P(grant) = 0.004

**Inputs read:** snapshot `2026-10-15.json` and `context.json` (forward mode,
band `baseline` under sal-v4, distribution_count 1, no CVSG, term 2026).
Provisioned documents: the questions presented, the petition, the appendix
listing, and the Fidelity respondents' brief in opposition.
`documents.json` marks the cert reply (filed Oct 5, 2026) `empty_text: true`.
It was a scanned filing with no text layer, so I did not read the
petitioner's reply. I treat its content as unavailable, not as absent.

**Anchor.** The statpack's "Segment base rate by salience band (sal-v4)" table
gives the `baseline` band's bracketed `reached` rate. I pooled Terms 2017–2025,
the rows strictly before OT2026, weighting each Term by its n. That gives about
5.0% (roughly 640 weighted grants over n ≈ 12,900). That figure is the yardstick.

**Why far below the anchor:**
- **Pro se petitioners.** Randy Quaid is listed as the filing party, not as
  counsel of record. Paid pro se petitions are granted far less often than the
  counselled paid petitions that make up most of the baseline band.
- **Unpublished memorandum.** The Ninth Circuit's disposition is a
  nonprecedential memorandum (confirmed by both the petition and the BIO). The
  Court rarely takes these as vehicles.
- **State-law question.** The QP asks how California's litigation privilege
  (§ 47(b)) and its gravamen test apply. The petition argues the decision
  conflicts with California Supreme Court precedent. That is a claim of
  state-law error, not a conflict among federal courts on federal law. The
  Rule 12/Rule 15 framing does not create a federal question.
- **Posture.** Two sets of respondents waived their right to respond. One
  institutional respondent filed a BIO without being asked. No response was
  ever requested by the Court, and the case has been distributed only once.

I put the grant probability at 0.4%, roughly a tenth of the anchor. The remaining
mass covers an unexpected summary disposition.

**Increments:** the relist-increment is 3% because almost all first-conference
petitions like this one are denied without another distribution. The
cvsg-increment is 0.2% because no federal party or federal interest is involved.
The dissent-from-denial claim is 0.5%. The summary-route claim, conditional on a
grant, is 0.3: any grant here would most likely be a corrective order, not
plenary review.

**Where to discount me:** I could not read the cert reply. I did not use
CourtListener or the corpus query; I relied on the provisioned record and the
statpack. I know the petitioner is a public figure from general knowledge, but
I do not know this petition's outcome.
