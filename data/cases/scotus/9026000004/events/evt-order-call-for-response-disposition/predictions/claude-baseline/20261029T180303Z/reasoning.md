# Why P(grant) = 0.07

**Inputs read.** Snapshot `record/snapshots/2026-08-14.json` (cut `date`,
cutoff 2026-08-15); `record/context.json` (forward, band `baseline` under
`sal-v4`, distribution_count 1, no CVSG); `record/documents/questions-presented.txt`
and `petition.txt` (151 pages, truncated at the cap — I read the QP, jurisdiction
statement, introduction, statement of the case and the reasons headings). No
brief in opposition exists yet: the response was only requested on the cutoff
day, and I do not infer its content.

**Anchor.** The statpack's sal-v4 segment table, band `baseline`, bracketed
`reached` rate pooled over OT2017–OT2025 (the Terms strictly before OT2026):
about 5.1% (≈660 weighted grants over n≈12,900). Petitioner is a private
corporation, so the baseline floor is also the caption-class floor.

**Adjustments up.**
- The Court called for a response after a waiver — a Justice or clerk read the
  petition and thought it worth an answer. No committed table conditions on
  this; my judgment is that it roughly doubles a paid petition's odds, but
  most such petitions are still denied.
- One amicus brief (Atlantic Legal Foundation); the statpack's amicus `1`
  bucket (n=1,162 resolved) grants ~10% vs ~2% for `0`, though that is a
  terminal-count population cut, not a conditional effect.
- Elite Supreme Court counsel; the QP targets an issue *Mallory* expressly
  noted (Georgia's implied-consent regime) and the petition asserts a 3–2
  state split over whether statutory notice is required.

**Adjustments down.**
- The Court has already declined Georgia's regime once: the corpus shows
  *Cooper Tire & Rubber Co. v. McCall*, No. 21-926, held through *Mallory* and
  denied on 2023-06-30 after four distributions, with three amicus briefs.
- Vehicle: the case arrives from the Georgia Court of Appeals in a
  default-judgment posture; by the petition's own account the state courts
  never addressed the personal-jurisdiction argument (raised only as an
  alternative ground for affirmance), inviting "not pressed or passed upon"
  and adequate-state-ground objections; finality under § 1257 rests on *Cox
  Broadcasting*. The sympathetic facts (wrong defendant, $10.9M award) are
  not what the QP presents.
- The asserted split is thin and partly from intermediate courts.

Net: from ~5% to about 7%. Main uncertainty is how much weight the CFR deserves
— if the request came from a Justice actively interested in post-*Mallory*
limits, the true figure could be in the low teens.

**Other claims.** relist-increment 0.97 (masked on this moment; a further
distribution follows the response almost mechanically). cvsg-increment 0.03
(no federal interest). summary-disposition-route 0.08 (no intervening
decision to GVR on). dissent-from-denial 0.04, with order-writer mass small
and spread over the *Mallory* separate writers.

**Retrieval.** Two corpus queries plus one broad one (see `retrieval.md`); no
MCP or web lookups. Nothing I saw claims this petition's disposition.
