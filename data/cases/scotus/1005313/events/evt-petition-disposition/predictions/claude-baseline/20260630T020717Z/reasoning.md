# Prediction — scotus/1005313 · evt-petition-disposition

## The legal question

This event asks how the Supreme Court of the United States will dispose of the
filing in *Joseph V. Puranda v. Gene M. Johnson, Director, Virginia Department
of Corrections* (No. 04-6725). The event is a `petition` with
`decision_target: disposition` — i.e., will the petition (for a writ of
certiorari) be **granted** or **denied**.

## Governing standard

Review on certiorari is discretionary. Under Supreme Court Rule 10, "[a] petition
for a writ of certiorari will be granted only for compelling reasons" — typically
a genuine conflict among the federal courts of appeals or state courts of last
resort, or an important unsettled question of federal law. The Rule expressly
notes that a petition is "rarely granted when the asserted error consists of
erroneous factual findings or the misapplication of a properly stated rule of
law." The Court grants only a tiny fraction of the petitions filed each Term.

## Facts from the snapshot that drive the outcome

- **Posture.** The case comes to the Court from the United States Court of
  Appeals for the Fourth Circuit (`appeal_from_str`), with an originating-court
  judgment dated 2004-05-20 (docket 04-6371). The respondent is the Director of
  the Virginia Department of Corrections — the case is a state-prisoner
  post-conviction / habeas matter.
- **Docket number 04-6725.** The five-digit-range number (>5000) for the 2004
  Term places this on the Court's *in forma pauperis* ("paupers") docket — a
  pro se, fee-waived filing. The IFP docket is where the overwhelming majority of
  petitions sit, and its grant rate is dramatically lower than the paid docket —
  on the order of one or two tenths of a percent.
- **No grant signal in the record.** `date_cert_granted`, `date_cert_denied`,
  and `date_terminated` are all `null` in this snapshot, so the event is
  genuinely unresolved as of 2026-06-30; the prediction rests on priors, not on
  any docketed disposition. There is no argument date, no panel, and no
  indication the case was distributed for any treatment beyond the routine
  conference list.

## Reasoning behind the probability

The structural features here are the canonical profile of a denied petition: a
pro se IFP prisoner challenging a state criminal/habeas judgment, raising what are
almost always fact-bound or settled-law claims rather than a clean,
acknowledged circuit split. Rule 10's "compelling reasons" bar is rarely cleared
by such petitions. The unconditional base rate for certiorari grants is roughly
1%; for the IFP docket it is far lower still (well under 0.5%). Nothing in the
snapshot lifts this case above that baseline — no recorded split, no call for the
views of the Solicitor General, no relist signal.

I therefore predict the petition will be **denied**: `granted = 0`,
`predicted_disposition = denied`, with `probability` (P(granted)) set to **0.01**
to reflect the small but non-zero residual chance inherent in any cert petition.
Confidence in the denial direction is high (0.97). No per-judge `votes` are
recorded: orders denying certiorari are issued by the Court without a recorded
vote of the individual Justices, so a vote breakdown would be invented rather
than predicted.

## Caveats

The corpus `query` priors available for `scotus` carry opinion-level disposition
labels (`other`, `dismissed`) rather than a clean cert grant/deny signal, so they
do not provide a directly usable petition-disposition base rate; the probability
above is anchored in the well-established public statistics for SCOTUS certiorari
practice and the structural features of this specific filing.
