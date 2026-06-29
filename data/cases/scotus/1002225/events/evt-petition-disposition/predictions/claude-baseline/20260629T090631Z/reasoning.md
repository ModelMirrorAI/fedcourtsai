# Prediction: scotus/1002225 — evt-petition-disposition

## The legal question

Whether the Supreme Court will grant the petition for a writ of certiorari in
*Frank Moore v. Keith E. Olson, Warden* (No. 04-6339), an appeal from the United
States Court of Appeals for the Seventh Circuit. The event's `decision_target`
is the petition's disposition (granted / denied / etc.).

## Governing standard

Review on certiorari "is not a matter of right, but of judicial discretion,"
and is granted "only for compelling reasons" (Supreme Court Rule 10). The Court
typically requires a genuine conflict among the courts of appeals, a conflict
with its own precedent, or an important unsettled question of federal law. The
denominator is enormous and the grant rate is correspondingly low.

## Facts from the snapshot that drive the outcome

- **Posture:** A petition for certiorari before the Supreme Court
  (`court_id: scotus`, event `kind: petition`), arising from a Seventh Circuit
  judgment.
- **Caption:** The respondent is "Keith E. Olson, Warden." A prisoner-versus-
  warden caption is the signature of a habeas / post-conviction matter, almost
  invariably filed pro se and in forma pauperis. The docket number `04-6339`
  falls in the range the Court assigns to IFP ("paupers' docket") petitions,
  which corroborates this.
- **No procedural signals of a grant:** The snapshot shows
  `date_cert_granted: null`, `date_cert_denied: null`, `date_argued: null`,
  empty `docket_entries`, an empty `panel`, and no `date_terminated`. Nothing in
  the record indicates the Court has called for a response, relisted the case,
  requested the record, or scheduled argument — the kinds of activity that
  precede the rare grant.
- **Originating court info:** The underlying Seventh Circuit judgment issued
  2004-05-17 with rehearing denied 2004-06-15; the petition followed on
  2004-09-20. This is an ordinary, timely cert petition from a routine appellate
  affirmance, with no indication of a circuit split or other "compelling reason."

## Reasoning behind the probability

Base rates dominate here. The Supreme Court grants roughly 1% of all paid
petitions and well under 0.5% of IFP petitions; pro se prisoner habeas petitions
— which this caption and docket range strongly indicate — are granted at a rate
near or below one-tenth of one percent. The snapshot contains no
case-specific signal (no CFR, relisting, argument, or split) that would push the
probability above that base rate. Accordingly I predict the petition will be
**denied**, with P(granted) = 0.01, slightly above the IFP base rate only to
account for residual uncertainty about whether this petition raises an issue not
visible in the snapshot.

Cert dispositions are issued by the Court collectively and individual Justice
votes on denial are not recorded, so no per-judge `votes` are provided.

## Caveats

This prediction is made solely from the provisioned snapshot, as required. The
snapshot carries no docket entries or merits briefing, so the assessment rests on
posture, caption, docket-number range, and the governing base rate rather than on
the petition's specific arguments. The conservative call given that limited
record is denial.
