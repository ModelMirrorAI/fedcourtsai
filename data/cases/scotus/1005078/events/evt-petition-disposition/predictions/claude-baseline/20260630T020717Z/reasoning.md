# Prediction reasoning — scotus/1005078, evt-petition-disposition

## The legal question

The event (`kind: petition`, `decision_target: disposition`, title *Myers v.
Ohio*) asks for the **disposition** of a petition before the Supreme Court of
the United States. The outcome space is the standard disposition enum (granted /
denied / granted-in-part / dismissed / withdrawn / other), with `granted` as the
binary target and `probability` as P(granted). For a SCOTUS matter at this
posture the petition is a petition for a writ of certiorari, so "granted" means
**cert granted**.

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1005078/record/snapshots/2026-06-30.json`) and did not fetch
new docket facts or look up the historical outcome (the very quantity under
evaluation). The snapshot is a bare metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_argued`, `date_cert_granted`, `date_cert_denied`, `date_terminated` are
  all `null` — no recorded disposition in this snapshot.
- No `nature_of_suit`, no `cause`, no question presented, no merits argument.

Despite the thin record, several **structural** identifiers on the face of the
snapshot carry real signal (these are not "new facts"):

- **Docket number `02-9866`.** SCOTUS docket numbers above ~5000 within a Term
  are the **in forma pauperis (IFP) / "pauper" docket**; numbers below that are
  the paid docket. `9866` places this squarely on the IFP docket for October
  Term 2002.
- **Posture.** The petitioner (David L. Myers) proceeds against **Ohio**, with
  the case originating from the **Supreme Court of Ohio** (`appeal_from_str`),
  originating-court docket `99-395`. This is the classic profile of a pro se
  petition seeking review of a state-court (very likely post-conviction or
  criminal) judgment.
- `date_filed: 2003-04-01`, consistent with an OT2002 IFP petition.

## How I reach a probability

With no merits-specific signal to move the prediction, the defensible anchor is
the **base rate** of SCOTUS petition dispositions, conditioned on the docket
type the snapshot reveals:

- Across all petitions, the Court grants certiorari in roughly **1%** of cases —
  the modal outcome is overwhelmingly **denied**.
- That overall rate is dominated by the paid docket (a few percent). The **IFP
  docket grants at a far lower rate — on the order of 0.1–0.2%.** Pro se
  petitions challenging state-court judgments are denied in the overwhelming
  majority of cases.

Given the IFP docket number and the pro se state-prisoner-style posture, the
conservative and well-calibrated call is the modal outcome — **denied** — with a
P(granted) at or below the all-petitions ~1% prior. I set `probability = 0.01`,
`predicted_disposition = denied`, `granted = 0`.

`confidence = 0.2` reflects that while the directional call (denied) is very
secure, the snapshot carries no merits facts, so the precise probability rests
on base rates rather than case-specific reasoning. I report no per-judge `votes`
because cert grants/denials are not recorded as individual Justice votes in this
record and the snapshot identifies no panel.
