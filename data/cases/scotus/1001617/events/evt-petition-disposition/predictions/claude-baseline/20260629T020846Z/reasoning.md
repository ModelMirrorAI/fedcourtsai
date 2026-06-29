# Prediction reasoning — scotus/1001617, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *Hanson v. Moore, Secretary, Florida
Department of Corrections*, a Supreme Court of the United States matter. The
outcome space is the standard disposition enum (granted / denied /
granted-in-part / dismissed / withdrawn / other), with `granted` as the binary
target and `probability` as P(granted). For a SCOTUS matter at this posture the
petition is a petition for a writ of certiorari, so "granted" means cert
granted.

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1001617/record/snapshots/2026-06-29.json`), and I did not
fetch new docket facts or look up the historical outcome (which is exactly the
quantity under evaluation). The snapshot is essentially a bare metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null` — no recorded disposition in this snapshot.
- No `nature_of_suit`, no `cause`, no question presented, no merits argument.

Despite the thin record, a few **structural** identifiers carry real signal and
are not "new facts" — they are on the face of the snapshot:

- **Docket number `01-8079`.** SCOTUS docket numbers above ~5000 within a Term
  are the **in forma pauperis (IFP) / "pauper" docket**; numbers below that are
  the paid docket. `8079` places this squarely on the IFP docket for October
  Term 2001.
- **Party posture.** The petitioner (Oscar Andrew Hanson) is an inmate
  proceeding against the **Secretary of the Florida Department of Corrections**,
  with the case originating from the U.S. Court of Appeals for the Eleventh
  Circuit (`original_court_info.docket_number`). This is the classic profile of
  a pro se prisoner/post-conviction petition.

## How I reach a probability

With no merits-specific signal to move the prediction, the defensible anchor is
the **base rate** of SCOTUS petition dispositions, conditioned on the docket
type that the snapshot does reveal:

- Across all petitions, the Court grants certiorari in roughly **1%** of cases —
  the modal outcome is overwhelmingly **denied**.
- That overall rate is dominated by the paid docket (a few percent). The **IFP
  docket grants at a far lower rate — on the order of 0.1–0.2%.** Pro se
  prisoner petitions of this kind are denied in the overwhelming majority of
  cases.

Given the IFP docket number and the pro se prisoner posture, the conservative
and well-calibrated call is the modal outcome — **denied** — with a P(granted)
**below** the all-petitions ~1% prior. I set `probability = 0.01`,
`predicted_disposition = denied`, `granted = 0`.

`confidence = 0.2` reflects that while the directional call (denied) is very
secure, the snapshot carries no merits facts, so the precise probability rests
on base rates rather than case-specific reasoning. I report no per-judge `votes`
because cert grants/denials are not recorded as individual Justice votes in this
record and the snapshot identifies no panel.
