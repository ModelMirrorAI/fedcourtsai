# Prediction reasoning — scotus/1005202, evt-petition-disposition

## The legal question

The event is a `petition` disposition before the Supreme Court of the United
States: whether the Court will grant the petition for a writ of certiorari in
*Snyder v. Sumner, Warden* (No. 93-7131). The decision target is the disposition
of the petition (granted vs. denied).

## Governing standard

Certiorari is discretionary. Under Supreme Court Rule 10, review "is not a matter
of right, but of judicial discretion," and is granted "only for compelling
reasons" — chiefly a genuine conflict among lower courts or an important,
recurring, unsettled federal question. The overwhelming default disposition for
any cert petition is **denial**: the Court grants on the order of ~1% of all
petitions, and the rate is far lower for the *in forma pauperis* docket, and
lower still for state-prisoner habeas petitions, the category to which this case
belongs.

## Facts from the snapshot

- **Court / posture.** SCOTUS docket 1005202, docket number **93-7131**, October
  1993 Term. A docket number in the 7000+ range for a Term is the *in forma
  pauperis* ("paupers") sequence — i.e. this is an IFP petition, the category
  with the lowest historical grant rate (well under 0.1%).
- **Parties.** The caption *Snyder v. Sumner, **Warden*** identifies the
  respondent as a prison warden, which marks this as a **state-prisoner habeas /
  post-conviction** petition (an individual inmate challenging the custody
  authority). Such petitions, on the IFP docket, are the least likely of all
  cert petitions to be granted; the practical grant rate approaches zero absent
  an apparent circuit split or a clean, important federal question.
- **Record.** The snapshot carries **no docket entries**, no `date_argued`, and
  no opinion clusters beyond a single linked cluster reference. There is nothing
  to suggest the Court called for a response, requested the views of the
  Solicitor General, relisted the case, or otherwise flagged it for the kind of
  scrutiny that precedes a grant.
- **Resolution fields.** `date_cert_granted`, `date_cert_denied`, and
  `date_terminated` are all `null` in this snapshot, so I do not treat the case
  as already resolved; I predict from posture and base rates only, as the
  contract requires (no new facts fetched).

## Reasoning behind the probability

Every signal available in the snapshot points the same way as the base rate: an
individual prisoner petitioner against a warden, on the IFP docket, with no
indication in the record of a circuit conflict, a question of national
importance, or any procedural sign of heightened Court interest. There is no
compelling Rule 10 reason apparent. I therefore predict **denied**, with
`granted = 0`.

I set `probability` (P(granted)) at **0.004** — below the ~1% all-cases grant
rate to reflect the IFP state-prisoner-habeas posture, but not at zero because
the snapshot is thin and I cannot fully rule out an unseen cert-worthy feature
(e.g. a question the Court was independently holding for). Confidence in the
denial call is high (**0.97**).

## Votes

SCOTUS does not publish per-Justice votes on certiorari (the "rule of four" tally
is not disclosed on the public docket), and the snapshot lists no panel, so I
record no per-judge votes.
