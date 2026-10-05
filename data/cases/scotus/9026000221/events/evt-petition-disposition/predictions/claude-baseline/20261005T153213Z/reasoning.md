# Why 0.03

**Anchor.** `record/context.json` freezes the band at `baseline` under
`sal-v4`, with `distribution_count: 1`, no CVSG, mode `forward`, Term 2026.
The statpack's "Segment base rate by salience band (sal-v4)" table matches
the context's version, so the anchor is the `baseline` column's bracketed
`reached` rate pooled over the Term rows strictly before 2026. Pooling the
nine rendered prior rows (OT2017 through OT2025, weighted n 12,720) gives a
reached grant-family rate of about 5.0%, ranging 3.9% (OT2025) to 5.9%
(OT2023). That is the yardstick the evaluator scores this cell against. The
relist-count cut agrees in shape: the 0-relist bucket resolves granted 1.2%
plus GVR 0.5%, while one relist lifts the family to about 13%, which is why
the relist claim matters more than the grant claim here.

**What pushes down from 5%.** Several vehicle problems, each of which the
Court weighs heavily on a paid state-criminal petition:

- *Posture.* The federal question arrives through a K.S.A. 60-1507
  ineffective-assistance claim. The Kansas Court of Appeals said only that it
  was "skeptical" the statements were testimonial or hearsay, and then
  rested on an independent Strickland prejudice holding: the same accusation
  came in through Agent Bridges over objection, and the conviction rests on
  repeated confessions. The petition's answer, that the prejudice analysis
  is infected by the same characterization, is plausible but makes the
  Court decide a record-bound prejudice question before the constitutional
  one can matter. The Court rarely grants to reach a question that an
  alternative holding may moot.
- *Unpublished memorandum opinion* of an intermediate state court, with
  discretionary review denied by the Kansas Supreme Court. The Court treats
  that as a weak vehicle for a doctrinal split.
- *Response waived, no call for a response at first distribution.* A grant
  without a response is essentially never made; the honest grant path runs
  through a CFR that has not yet happened.
- *The Court already passed on the same split last Term* in Reed v.
  Fredrick (cert denied 2025), the Sixth Circuit case the petition relies on
  for the split. The AEDPA posture there is a real distinction, and this
  petition makes it well, but the denial shows the Court is not pressing to
  resolve the "course of investigation" question.
- *Facts.* A three-year-old complainant, a confession repeated three times,
  and a Clark question layered under the Smith question. The Court would be
  asked to disturb a rape conviction on a record where the challenged
  testimony was a single exchange.
- *Originating court.* The corpus holds 11 resolved petitions from the Court
  of Appeals of Kansas, all denied; thin, but consistent with the above.

**What pushes up.** The split is genuine and acknowledged: Judge Stranch's
dissent in Reed v. May names the Second, Fifth, and Seventh Circuits as
contrary, and the First Circuit's Cartagena (April 2026) applied Smith the
same way. Both decisions exist on CourtListener as the petition describes
them. Smith v. Arizona (2024) is a recent, broad-majority hook, the
petition is competently drafted by retained appellate counsel, and the case
is on direct review under section 1257 rather than habeas, which cures the
exact defect that doomed Reed. Those facts make a call for a response
plausible even though a grant is not.

**Net.** I land at 0.03, somewhat below the 5% band anchor, because the
posture and the alternative prejudice holding are the kind of defects that
turn a plausible split into a denial, and because the grant path requires
a CFR that has not yet appeared. I would not go much lower: a real split
with a recent Supreme Court hook and paid counsel keeps a live tail.

**Other claims.** Relist-increment 0.22: roughly 0.18 for a call for a
response (which redistributes), plus small contributions from a reschedule
before first consideration (the harness counts it as a distribution) and a
relist without CFR. CVSG-increment 0.01: no federal interest. Summary route
0.15 conditional on a grant: no intervening decision to GVR against, and a
summary reversal in this posture is unusual; the residual covers an
unforeseen Confrontation Clause decision this Term. Dissent-from-denial
0.04: the issue has drawn no writing in its recent cert appearances.

**Big-case score 0.30.** If decided, a ruling on investigative-background
testimony would reach a recurring practice in criminal trials nationwide,
which is significant to the criminal bar but carries little public salience.

**Where to discount me.** I have no brief in opposition (Kansas waived), so
the State's likely emphasis on the confessions and the Bridges testimony is
my inference from the opinion below, not from a filing. The band anchor
pools denial-reweighted estimates and the OT2025 row is the least settled.
I did not read the summaries directory or the earlier arrival-moment cells,
and I forecast from this moment's record only. CourtListener's RECAP index
holds no docket for 26-221, so I confirmed no docket activity beyond the
provisioned snapshot; the snapshot's October 5 date is the baseline I used.

**Inputs read.** `record/snapshots/2026-10-05.json`, `record/context.json`,
`record/documents/questions-presented.txt`, and `record/documents/petition.txt`
(140 pages, text truncated by the pipeline; I read the petition body and
Appendix A, the Kansas Court of Appeals opinion, in full). `documents.json`
shows both documents fetched with text; no brief in opposition exists.
