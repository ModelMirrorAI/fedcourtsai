# Prediction reasoning — scotus/1002345, evt-petition-disposition

## The legal question

The event is a **petition disposition** at the Supreme Court of the United States
(`kind: petition`, `decision_target: disposition`) for the docket
*Martin v. McKune Warden* (No. 92-8777). The question is whether the petition — a
petition for a writ of certiorari — is **granted** (the Court agrees to hear the
case) versus denied/dismissed/withdrawn.

## Governing standard

Certiorari is discretionary (Sup. Ct. R. 10). The Court grants review only for
"compelling reasons" — typically an entrenched circuit split, an important
unsettled question of federal law, or a decision in conflict with the Court's
precedent. The unconditioned base rate of a cert grant is very low (a few percent
of paid petitions), and it is far lower still for *in forma pauperis* (IFP)
petitions, the overwhelming majority of which are denied. A disposition prediction
must therefore start from a strong presumption of denial and update only on
case-specific signal.

## Facts available from the snapshot

The provisioned snapshot (`record/snapshots/2026-06-29.json`) is sparse, but three
structural facts are decisive:

- **Docket number 92-8777.** Supreme Court docket numbers below roughly 5000 in a
  Term are the paid/regular docket; numbers at or above 5000 are the *in forma
  pauperis* (paupers) docket. The "8777" places this firmly on the IFP docket for
  the 1992 Term.
- **Respondent is "McKune Warden."** A warden as respondent identifies this as a
  prisoner petition (habeas/civil-rights posture), almost always filed pro se. The
  combination of an IFP docket number and a warden respondent is the canonical
  profile of a pro se prisoner cert petition — the category with the lowest
  observed grant rate.
- **No grant/merits signals.** `date_cert_granted`, `date_cert_denied`,
  `date_argued`, and `date_terminated` are all **null**, and `docket_entries` is
  **empty**. `panel`, `assigned_to`, and `referred_to` are empty/null, so no
  judge-level information is available for per-judge votes.

The docket does link to one opinion `clusters` entry (`.../clusters/113321/`). On a
SCOTUS docket a linked cluster can indicate a merits decision, but it can equally
correspond to an order-list entry (including the order **denying** certiorari) or a
denial accompanied by a statement/dissent. Given the strong IFP-prisoner profile
here, the cluster link is weak and ambiguous evidence of a grant and does not
overcome the denial presumption.

## Reasoning

Predicting only from the snapshot, the decisive signals — IFP docket number, a
warden respondent (pro se prisoner posture), and the absence of any cert-granted or
argument date — all point to **denial**, which is the disposition of the great
majority of petitions in this category. I do not treat the linked opinion cluster
as evidence of a grant the way it might be for a paid government petition, because
for an IFP prisoner matter a cluster most plausibly reflects the order-list
disposition (typically the denial) rather than a merits opinion.

I set **P(granted) = 0.03** — slightly above a pure IFP-prisoner base rate to leave
room for the residual ambiguity of the cluster link and the thinness of the
snapshot — predict the **denied** disposition, and report **confidence 0.72**: the
structural profile is a strong and consistent signal toward denial even though the
snapshot lacks an explicit disposition order to read directly.

I record **no per-judge votes**: cert denials are not accompanied by recorded
Justice-level votes, and the snapshot exposes no panel or Justice-level
information. The prompt forbids fetching new case facts to fill that gap.

## Limitations

This prediction is constrained to the provisioned snapshot, which lacks the docket
entries and conference/order dates that would normally confirm a cert disposition.
The estimate rests on the structural inference from the docket number and party
posture. No external case facts were retrieved.
