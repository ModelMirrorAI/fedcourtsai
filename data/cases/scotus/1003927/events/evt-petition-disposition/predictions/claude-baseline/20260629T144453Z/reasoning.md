# Prediction reasoning — scotus/1003927, evt-petition-disposition

## The legal question

Will the Supreme Court grant the petition in *State of Oklahoma v. State of
Texas (United States, Intervener)*? The event's `decision_target` is the
petition's **disposition**; "granted" means the petition is granted
(`granted = 1`).

## Governing standard

The governing standard turns on which kind of "petition" this is, and the
caption is the decisive signal. This is a controversy **between two States**
(Oklahoma v. Texas) in which the **United States has intervened**. A suit by one
State against another falls within the Supreme Court's **exclusive original
jurisdiction** (U.S. Const. art. III, § 2, cl. 2; 28 U.S.C. § 1251(a)), and is
commenced by a *motion for leave to file a bill of complaint* (Sup. Ct. R. 17),
not an ordinary petition for certiorari.

The discretionary screen for original actions is therefore different from the
Rule 10 certiorari standard. The Court asks whether there is a genuine,
justiciable controversy of the "seriousness and dignity" warranting the exercise
of original jurisdiction (*Mississippi v. Louisiana*, 506 U.S. 73 (1993)).
Boundary, water-rights, and natural-resource disputes between States — the
paradigmatic interstate-controversy category this caption fits — are the core
of that jurisdiction, and leave to file is granted in such genuine disputes at a
far higher rate than the ~1% grant rate for paid certiorari petitions.

## Facts from the snapshot that drive the outcome

Reasoning is based solely on the provisioned snapshot
(`data/cases/scotus/1003927/record/snapshots/2026-06-29.json`):

- **Posture is an original interstate action.** The caption is
  *State of Oklahoma v. State of Texas (United States, Intervener)* with
  `court_id` "scotus" and a one- or two-digit docket number ("13"), consistent
  with an original-docket matter rather than a numbered certiorari petition.
  A State-versus-State controversy with federal intervention is squarely within
  the Court's exclusive original jurisdiction.
- **The category raises the grant likelihood above the cert base rate.** Unlike
  an ordinary civil cert petition (overwhelmingly denied), motions for leave to
  file in genuine interstate disputes are entertained far more often, because the
  Court is the only available forum for such controversies.
- **The record is otherwise sparse.** `date_argued`, `date_cert_granted`,
  `date_cert_denied`, and `date_terminated` are all null; `docket_entries` is
  empty; there is no panel or judge assignment and no docket text. There is thus
  no case-specific signal of justiciability defects, an abstention, or a referral
  to a Special Master that would cut for or against the motion. The prediction
  necessarily leans on the **category's** disposition pattern (interstate
  original action) rather than on case-specific grant signals, which is why
  confidence is low.

## Probability and disposition

Weighing the original-jurisdiction posture — which materially favors granting
leave in a genuine interstate controversy — against the near-total absence of
case-specific facts in the snapshot, I assign **P(granted) = 0.55**, predicting
**disposition = granted** (`granted = 1`). The probability sits only modestly
above a coin flip because the favorable category signal is real but the record is
too thin to confirm the controversy's justiciability or current procedural state.
**Confidence is low (0.35)**: the directional read rests on the caption alone.

## Votes

Dispositions of original-action motions and certiorari petitions are not
accompanied by published per-Justice votes in this record, and the snapshot
contains no panel or judge assignment, so no per-judge votes are recorded.
