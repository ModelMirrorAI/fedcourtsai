# Prediction — scotus/1004993, evt-petition-disposition

**Case:** Hoffman v. United States (No. 93-7788)
**Court:** Supreme Court of the United States
**Event:** `evt-petition-disposition` — disposition of the petition (cert).

## The legal question

Will the Supreme Court grant the petition in this case? The event's
`decision_target` is `disposition`; the binary outcome is whether the petition is
granted (i.e., certiorari granted / set for plenary consideration) versus denied.

## Governing standard

Review on certiorari is discretionary (28 U.S.C. § 1254; Sup. Ct. R. 10).
Certiorari "is not a matter of right, but of judicial discretion" and is granted
"only for compelling reasons" — typically a genuine, acknowledged conflict among
the circuits or state courts of last resort, or an important unsettled question of
federal law. The overwhelming majority of petitions present none of these and are
denied without comment. The unconditional base rate of a cert grant is on the
order of ~1%, and substantially lower for in-forma-pauperis petitions.

## Facts from the snapshot that drive the outcome

Predicting strictly from the provisioned snapshot
(`record/snapshots/2026-06-30.json`):

- **Docket number 93-7788.** The high four-digit suffix places this on the Court's
  *in forma pauperis* docket — overwhelmingly pro se petitioners, frequently
  criminal defendants. The IFP cert-grant rate is far below the already-low overall
  rate (well under 0.1% historically).
- **Hoffman v. United States** — a private petitioner against the United States,
  the posture of a criminal/collateral petitioner seeking review of an adverse
  federal judgment. Such petitions are the modal denied petition.
- **`date_argued`, `date_cert_granted`, `date_reargued` are all null**, and there
  are **no docket entries** in the snapshot. Granted petitions are calendared for
  argument and acquire a cert-grant date; the absence of any of these signals is
  consistent with a routine denial rather than a grant.
- No nature-of-suit, no flagged circuit split, no amicus or merits activity in the
  snapshot — nothing indicating the "compelling reasons" Rule 10 requires.

## Calibration from corpus priors

A `fedcourts query --court scotus` pull over decided priors shows grants are rare
relative to other dispositions (≈4 of 244 decided rows carried a `granted` label;
the dispositions skew to merits/`other` and `dismissed`/`denied`). That corpus is
weighted toward older argued opinions rather than the IFP miscellaneous docket, so
if anything it *overstates* the grant rate for a petition like this one.

## Probability and disposition

Nothing in the snapshot rebuts the strong prior that an IFP cert petition is
denied. I predict **denied**, with **P(granted) = 0.01** — at the high end of what
the IFP base rate alone would justify, left slightly above the raw ~0.1% floor only
to hedge against the snapshot's sparseness (a single point-in-time record with no
docket entries). Confidence is high (0.85): the structural signals (IFP docket,
pro-se-style posture, no argument/grant dates) all point one direction, and the
only uncertainty is the thinness of the snapshot itself.

No per-judge votes are predicted: cert denials are issued by the Court without a
recorded vote breakdown, so `votes` is left empty.
