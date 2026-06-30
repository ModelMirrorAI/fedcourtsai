# Prediction reasoning — scotus/1005618, evt-petition-disposition

## The legal question

The event asks for the **disposition** of a petition (`kind: petition`,
`decision_target: disposition`) in *Ex Parte Transportes Maritimos*, a Supreme
Court of the United States matter. The outcome space is the standard disposition
enum (granted / denied / granted-in-part / dismissed / withdrawn / other), with
`granted` as the binary target and `probability` as P(granted).

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1005618/record/snapshots/2026-06-30.json`). I did not fetch
new docket facts and did not resolve the linked opinion cluster, because the
realized disposition is exactly the quantity under evaluation. The snapshot is a
bare metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated` are all `null` — no recorded disposition in this snapshot.
- No `nature_of_suit`, no `cause`, no question presented, no merits argument.
- `clusters` lists one opinion cluster, indicating an opinion exists, but I do
  not open it (that would be reading the outcome).

Two **structural** identifiers on the face of the snapshot carry real signal and
are not "new facts":

- **Docket number `26, Original`.** This is an **original-jurisdiction** matter,
  not a certiorari petition. SCOTUS original-docket cases are heard under the
  Court's Art. III, §2 original jurisdiction and, for applications by private
  parties, almost always require **leave of the Court** to file.
- **Case caption begins "Ex Parte."** An *ex parte* application at this posture
  is characteristically a petition for **leave to file an extraordinary writ**
  (mandamus or prohibition) invoking the Court's original jurisdiction.

## How I reach a probability

With no merits-specific signal, the defensible anchor is the **base rate** for
the docket type the snapshot does reveal:

- The Court's original jurisdiction is exercised sparingly. Ex parte
  applications by private litigants for leave to file extraordinary writs
  (mandamus/prohibition) are **denied in the overwhelming majority** of cases —
  the writ is a "drastic and extraordinary remedy" reserved for exceptional
  circumstances where there is no other adequate means of relief and the right
  to it is clear and indisputable (the *Cheney v. U.S. Dist. Court* / *Kerr v.
  U.S. Dist. Court* standard).
- The modal outcome for such a petition is therefore **denied** (whether by
  denying leave to file or by denying the writ itself).

I set `predicted_disposition = denied`, `granted = 0`, and `probability = 0.07`.
I anchor slightly above the ~1% cert-denial floor because original-jurisdiction
ex parte applications are a smaller, more heterogeneous population than the IFP
cert docket and occasionally secure the relief sought, so the residual
uncertainty around the grant tail is wider — but the directional call (denied)
remains secure.

`confidence = 0.2` reflects that the directional call is well-anchored in the
posture, but the snapshot carries no merits facts, so the precise probability
rests on base rates rather than case-specific reasoning. I report no per-judge
`votes`: original-docket dispositions of this kind are typically entered as a
per curiam order without recorded individual Justice votes, and the snapshot
identifies no panel.
