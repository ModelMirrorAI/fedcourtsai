# Prediction reasoning — scotus/1000145, evt-petition-disposition

## The legal question

The event is a **petition disposition** at the Supreme Court of the United States
(`kind: petition`, `decision_target: disposition`) for the docket
*United States v. One Assortment of 89 Firearms* (No. 82-1047). The question is
whether the petition — a petition for a writ of certiorari — is **granted** (i.e.
the Court agrees to hear the case) versus denied/dismissed/withdrawn.

## Governing standard

Certiorari is discretionary (Sup. Ct. R. 10). The Court grants review only for
"compelling reasons" — typically an entrenched circuit split, an important
unsettled question of federal law, or a lower-court decision in conflict with the
Court's precedent. The unconditioned base rate of a cert grant is very low (on the
order of a few percent of paid petitions). A disposition prediction must therefore
start from a strong presumption of denial and update only on case-specific signal.

## Facts available from the snapshot

The provisioned snapshot (`record/snapshots/2026-06-28.json`) is sparse:

- `docket_entries` is **empty** — there are no docketed orders, no conference
  dates, no distribution entries to read directly.
- `date_cert_granted` and `date_cert_denied` are both **null**, and
  `date_argued` / `date_terminated` are null.
- `panel`, `assigned_to`, and `referred_to` are empty/null, so no judge-level
  information is available for per-judge votes.
- The one substantive signal is `clusters`: the docket links to an **opinion
  cluster** (`.../clusters/111103/`). The docket number (82-1047) places the case
  in the early-1980s Terms, consistent with a fully resolved historical matter.

## Reasoning

Predicting only from the snapshot, the decisive signal is the presence of a linked
**opinion cluster**. At the Supreme Court, a docket that carries an opinion cluster
almost always reflects a case the Court took and decided on the merits — which
presupposes that certiorari was **granted**. That conditioning flips the analysis
away from the low unconditioned cert-grant base rate and toward a granted
disposition.

I temper the probability rather than pushing it to near-certainty because the
snapshot itself is thin: with empty docket entries and null cert dates, I cannot
read a grant order directly, and a small fraction of opinion clusters on SCOTUS
dockets correspond to orders accompanied by opinions (e.g., a denial with a written
dissent or statement) rather than a merits grant. Those cases would make the
disposition something other than "granted." Weighing the strong cluster signal
against that residual ambiguity, I set **P(granted) = 0.85**, predict the
**granted** disposition, and report a moderate **confidence (0.55)** to reflect the
limited procedural detail in the snapshot.

I record **no per-judge votes**: the snapshot exposes no panel or Justice-level
information, and the prompt forbids fetching new case facts to fill that gap.

## Limitations

This prediction is constrained to the provisioned snapshot, which lacks the docket
entries and conference/order dates that would normally confirm a cert disposition.
The estimate leans on the structural inference from the linked opinion cluster. No
external case facts were retrieved.
