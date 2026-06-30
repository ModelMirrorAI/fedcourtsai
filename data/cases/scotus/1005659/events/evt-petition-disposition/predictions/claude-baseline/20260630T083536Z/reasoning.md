# Sanders v. Pennsylvania — petition disposition

## The event

`evt-petition-disposition` asks whether the Supreme Court will grant the
petition in *Sanders v. Pennsylvania* (`scotus/1005659`, docket No. 93-7173).
The decision target is the petition's disposition; the event is currently
unresolved. For a Supreme Court petition, "granted" means the Court grants
review (certiorari, or the relief sought by the petition), and "denied" means
the petition is refused.

## Governing standard

Review by the Supreme Court is discretionary. Under Supreme Court Rule 10,
certiorari "is not a matter of right, but of judicial discretion," and is
granted "only for compelling reasons" — typically a genuine conflict among the
courts of appeals or state courts of last resort, or an important unsettled
question of federal law. The Court grants only a small fraction of the
petitions it receives, and the rate is far lower still for in forma pauperis
(IFP) petitions filed on the miscellaneous docket, which are overwhelmingly
pro se prisoner and state-criminal filings.

## Facts from the snapshot

The latest snapshot (`2026-06-30.json`) is sparse, which is itself informative:

- **Court / posture:** `court_id` is `scotus`; the case name is
  *Sanders v. Pennsylvania* — a petitioner against a State, the canonical shape
  of a state-criminal defendant seeking review of a state-court judgment.
- **Docket number 93-7173.** This is an October Term 1993 number, and the high
  sequence number (7173) places it squarely on the Court's *in forma pauperis*
  / miscellaneous docket rather than the paid docket. IFP criminal petitions
  carry the lowest grant rate of any category before the Court (well under 1%).
- **No grant/denial signal recorded.** `date_cert_granted`, `date_cert_denied`,
  `date_argued`, and `date_terminated` are all null, and `docket_entries` is
  empty. There is no indication of a CVSG, a call for a response, relisting, or
  any other marker that distinguishes the rare petition headed toward a grant.

Nothing in the snapshot supplies a compelling-reasons hook (no asserted circuit
split, no flagged question of national importance, no procedural signal of
Court interest). I predict only from this snapshot and do not introduce outside
facts about the underlying case.

## Reasoning behind the probability

The dominant driver is the base rate. The Court denies the overwhelming
majority of petitions, and an IFP petition from a state-criminal petitioner —
which docket 93-7173 and the *Sanders v. Pennsylvania* caption strongly
indicate this to be — sits in the category with the lowest grant rate of all,
denied at well over 99%. The snapshot contains no offsetting signal of Court
interest. Absent any such signal, the conservative and well-calibrated
prediction is denial.

- **`predicted_disposition`: denied**
- **`probability` (P(granted)): 0.01** — a touch above the raw IFP base rate
  only to reflect the thin, late-stage snapshot rather than any affirmative
  reason to expect a grant.
- **`confidence`: 0.95** — high, given the strong base rate and absence of any
  contrary indicator.

## Votes

Denials of certiorari are issued by the Court without a recorded vote and are
typically unsigned; the snapshot identifies no panel or individual Justices.
No per-judge votes are predicted.
