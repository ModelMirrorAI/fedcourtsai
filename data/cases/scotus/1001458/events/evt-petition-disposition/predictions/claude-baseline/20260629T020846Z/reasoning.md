# Harrell v. Maryland — petition disposition

## The legal question

The event `evt-petition-disposition` asks how the Supreme Court of the United
States will dispose of the petition in *Antonio Donatea Harrell v. Maryland*
(docket no. 01-8077). The decision target is the disposition of the petition —
in practice, whether the Court **grants** review (certiorari) or **denies** it.
I predict P(granted).

## Governing standard

Review on certiorari is wholly discretionary. Under Supreme Court Rule 10, cert
is "not a matter of right, but of judicial discretion," granted "only for
compelling reasons" — most commonly an entrenched conflict among the federal
courts of appeals or among state courts of last resort on an important federal
question, or a question of national importance the Court has not settled. The
votes of four Justices are needed to grant. The overwhelming default outcome for
any petition is denial.

## Facts from the snapshot that drive the outcome

Predicting only from the provisioned snapshot
(`record/snapshots/2026-06-29.json`):

- **Court / posture.** A SCOTUS docket, on appeal from the Court of Appeals of
  Maryland (the State's highest court) — i.e., a petition for a writ of
  certiorari to a state court of last resort.
- **Docket number 01-8077.** The high four-digit suffix in the October 2001
  Term places this on the *in forma pauperis* (IFP) docket — the unpaid,
  typically pro se, petitions. The petitioner's individually-named, three-part
  caption (*Antonio Donatea Harrell*) against a State is consistent with a pro se
  criminal petitioner. IFP petitions are granted at a far lower rate than paid
  ("paying") petitions.
- **Subject.** An individual versus a State, arising from Maryland's high court —
  the classic shape of a state criminal/post-conviction matter.
- **No grant/denial dates recorded.** `date_cert_granted` and
  `date_cert_denied` are both null, and `date_terminated` is null; the snapshot
  does not state the outcome. There is one associated cluster reference, but the
  snapshot does not disclose its content, so I do not rely on it as a fact.
- **No indicia of cert-worthiness in the snapshot.** Nothing in the record
  signals a circuit/state split, a question the Court has flagged, a call for the
  views of the Solicitor General, or any other feature that lifts a petition
  above the baseline.

## Reasoning behind the probability

The dominant signal is the base rate. The Court receives several thousand
petitions per Term and grants on the order of ~1%. The IFP docket — to which
no. 01-8077 belongs — grants at a small fraction of even that rate (historically
well under 0.5%, on the order of 0.1–0.2%). Absent any snapshot feature
suggesting a compelling reason under Rule 10, there is no basis to deviate
upward from that base rate.

I therefore predict the petition is **denied**, with **P(granted) = 0.01** — a
deliberately conservative figure that sits at or slightly above the IFP base
rate to leave room for the unobserved possibility of merit not visible in the
snapshot. Binary `granted = 0`; predicted disposition `denied`; confidence in
the denial call is high (0.95).

No per-Justice votes are predicted: cert dispositions do not record individual
votes (a grant requires four; denials are issued without attributed votes), so a
judge-vote breakdown is not meaningful for this event.
