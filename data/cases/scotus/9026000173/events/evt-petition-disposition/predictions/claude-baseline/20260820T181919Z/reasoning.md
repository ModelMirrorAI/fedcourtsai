# Rationale — why P(grant) = 0.003

**Anchor.** The frozen context (`record/context.json`) carries `band:
baseline` under `sal-v3`, matching the committed statpack's segment table, and
`term: 2026`. Pooling the baseline band's bracketed `reached` rate over the
rendered Terms strictly before 2026 (OT2017–OT2025) gives roughly **6.5%**
(≈857/13,163 weighted) — the yardstick this cell is scored against.

**Adjustments, all downward and large.** The band rate pools every
baseline-band paid petition, including counseled petitions with developed
splits. This one sits far below that pool's center:

- **Pro se, in substance.** The petitioner is his own counsel (a paid filing,
  but self-represented, with scanned exhibits). Pro se petitions grant at
  rates well below even the baseline band's.
- **Serial litigant.** CourtListener shows four EDVA suits by the same
  petitioner against DoD entities (v. DLA, v. Austin, v. Seiling, v. Del
  Toro), a pattern the Court's screening treats unfavorably.
- **No published opinion below.** CA4 No. 24-1166 appears in CourtListener's
  docket index but its disposition is absent from the opinion index —
  consistent with an unpublished, non-precedential per curiam, the classic
  poor vehicle.
- **The asserted split is undeveloped.** QP 1 claims the circuits are
  "hopelessly split" on APA record-rule supplementation, sorting circuits into
  strict and loose camps without case citations establishing an
  outcome-determinative conflict. Record-supplementation doctrine has
  recognized exceptions in every circuit; the QP as framed is error-correction
  ("did the reviewing court and 4th Circuit violate... and cause reversible
  harmful error to the petitioner").
- **The SG waived response** on August 19 — the government reads this petition
  as not worth answering, and the Court calls for a response in only a small
  minority of waived cases.
- **Procedural stumbles.** The petition spent months on the miscellaneous
  docket (linked 25M81); the motion for leave to proceed "as a veteran" (not a
  recognized status) was denied June 8. Filed March 19, docketed August 6.

Net: 0.003 — about one in 300, versus the band anchor's ~6.5%. That is near
the floor for a paid petition that will actually reach conference; I keep it
above 0.001 because the record-rule issue is genuinely recurrent and the Court
occasionally surprises on APA administration questions.

**Claim numbers.**
- `disposition` 0.003 — as above; equals the top-level probability.
- `relist-increment` 0.97 — the frozen `distribution_count` is 1 (the May 19
  distribution of the motion phase). With the waiver filed, the re-docketed
  petition will be distributed for a fall conference with near-certainty; only
  a pre-conference withdrawal or dismissal preempts it.
- `cvsg-increment` 0.002 — the federal government is already the respondent
  with the SG as counsel of record; a CVSG is structurally inapplicable.
- `summary-disposition-route` 0.75 — conditional on the (very unlikely) grant
  family, a GVR/summary order dominates plenary review for a petition in this
  posture; the modern grant family already splits nearly half to GVR, and this
  case's profile pushes the conditional share higher.
- `dissent-from-denial` 0.01 — fact-bound pro se APA case; noted dissents
  from denial are rare generally and essentially unheard-of in this profile.

**Uncertainty and discounts.** The main uncertainty is the meaning of the
frozen `distribution_count: 1`: that distribution predates the petition's
August 6 docketing as 26-173 (it belonged to the miscellaneous-docket motion
phase), so the relist-increment state may reflect the motion rather than the
petition proper — flagged in `flags.json`. My read of the split's weakness
comes from the petition's own text (49 pages, fully extracted); no brief in
opposition exists to weigh against it, because the response was waived. The
statpack is the committed one in `metrics/statpack.md`; I did not refresh the
corpus, and my two CourtListener lookups (the CA4 docket and the petitioner's
EDVA history) were forward-legitimate pre-decision material. Mode is
`forward`; I sought nothing about this petition's own disposition, which does
not yet exist.
