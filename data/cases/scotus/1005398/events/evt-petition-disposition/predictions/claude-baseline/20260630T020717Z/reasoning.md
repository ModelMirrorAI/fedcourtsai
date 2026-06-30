# Prediction reasoning — scotus/1005398, evt-petition-disposition

## The legal question

The event is a `petition` disposition before the Supreme Court of the United
States: whether the Court will grant the petition for a writ of certiorari in
*Sharon Mavity v. Ann M. Veneman, Secretary of Agriculture* (No. 04-6788). The
decision target is the disposition of the petition (granted vs. denied).

## Governing standard

Certiorari is discretionary. Under Supreme Court Rule 10, review "is not a matter
of right, but of judicial discretion," and is granted "only for compelling
reasons" — chiefly a genuine conflict among the courts of appeals or state courts
of last resort, or an important, recurring, unsettled question of federal law.
The overwhelming default disposition for any cert petition is **denial**: the
Court grants on the order of 1% of all petitions, and the rate is dramatically
lower — well under 0.1% — for the in-forma-pauperis ("paupers") docket.

## Facts from the snapshot

- **Court / posture.** SCOTUS docket 1005398, docket number **04-6788**, filed
  **2004-10-14**. A docket number in the 5001+ range for the October 2004 Term is
  the *in forma pauperis* sequence — this is an IFP petition, the category with
  the lowest historical grant rate.
- **Parties / nature.** An individual petitioner (Sharon Mavity) against the
  **Secretary of Agriculture** — a suit against a federal official, on the facts a
  routine individual federal-employment / civil dispute, not the kind of recurring
  federal question or acknowledged circuit split that draws the Court's
  discretionary review.
- **Below.** Appeal from the **U.S. Court of Appeals for the D.C. Circuit**
  (originating district docket 02-5281); the originating court entered judgment
  **2004-03-31** and **denied rehearing 2004-06-15**. Nothing in the snapshot
  signals a circuit conflict, a federal statutory question of broad importance, a
  dissent below, or a call for the views of the Solicitor General.
- **Resolution fields.** `date_cert_granted`, `date_cert_denied`, and
  `date_terminated` are all `null` in this snapshot, so I do not treat the case as
  already resolved; I predict from posture and base rates only, fetching no new
  facts, as the contract requires.

## Reasoning behind the probability

Every signal available in the snapshot points the same direction as the base
rate. An IFP petition by an individual against a cabinet secretary, arising from a
single D.C. Circuit panel decision with no indicated split, no dissent, and no SG
involvement, is the archetypal cert denial. There is no fact in the snapshot that
would lift this above the base rate; if anything the IFP posture pushes it below
the ~1% all-petitions average.

I therefore predict **denied**, with `granted = 0` and `probability = 0.005`
(P(cert granted)). Confidence in the denial is high (**0.97**): the unpredictable
sliver of cert grants is what keeps the probability nonzero rather than at zero. I
record no per-judge votes — the Court does not report individual Justices' votes
on the order-list disposition of an ordinary cert denial, so any vote split would
be invented rather than predicted.
