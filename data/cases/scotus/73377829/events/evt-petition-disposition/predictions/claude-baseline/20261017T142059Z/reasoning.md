# Why P(grant) = 0.06

**Anchor.** `record/context.json` freezes this cell at band `baseline` under
`sal-v4`, Term 2025, one distribution, no CVSG. The statpack's "Segment base
rate by salience band (sal-v4)" table matches that version; pooling the
`baseline` bracketed `reached` rate over the Terms strictly before 2025 that the
table renders (2017–2024: 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7%, n ≈ 1,190–1,740
each) gives roughly **5.2%**.

**Adjustments.**
- Up: the Court **requested a response** after the SG waived — someone in
  chambers wanted the government's position. That is a real positive signal the
  band (which is keyed on relists/CVSG) does not fold in; requested-response
  paid petitions grant meaningfully more often than the baseline floor. There is
  also amicus support and a repeat clinic counsel (Emory's Supreme Court
  Advocacy Program).
- Down: no circuit split (petition's own authorities, e.g. *Dotson v. Griesa*
  (2d Cir.) and the Ninth Circuit EDR orders, do not conflict with the Fourth
  Circuit); the case comes up after a full trial with fact-intensive findings
  (the appendix is ~330 pages of district-court order); QP 2 rests on a
  statute/policy that does not obviously supply a cause of action; and the
  Court has institutional reasons to leave EDR reform to the Judicial
  Conference. The "important and recurring" argument is policy-framed rather
  than doctrinal. The relist-1 terminal bucket (8.2% grant + 5.1% GVR) is not my
  anchor — it describes petitions that *ended* at one distribution, and this
  distribution was a pre-response one effectively vacated by the response
  request.

Net: slightly above the anchor, **0.06**. Predicted disposition: denied.

**Claims.**
- `relist-increment` 0.95: a requested-response petition is re-distributed once
  the response is filed; the only ways out are withdrawal or something odd.
- `cvsg-increment` 0.01: the SG is already counsel for respondents.
- `summary-disposition-route` 0.05 (conditional on grant): no intervening
  decision to GVR in light of; plenary review would be the route.
- `dissent-from-denial` 0.08 (conditional on denial): issue may draw a
  statement, but nothing in the record signals one.

**Inputs and uncertainty.** I read the snapshot `2026-10-10.json`, the QP file,
and the first part of `petition.txt` (388 pages, truncated). No brief in
opposition was provisioned — it was not yet due at the snapshot — so I do not
know what vehicle or merits arguments the SG makes; a strong vehicle objection
(e.g. waiver, mootness of equitable relief given petitioner's departure) would
push lower. I did no live retrieval. Main discount: my read of why the response
was requested is inference.
