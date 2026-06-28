# Prediction reasoning — scotus/1001152 / evt-petition-disposition

## The legal question

The event `evt-petition-disposition` (kind: `petition`, decision target:
`disposition`) asks how the Supreme Court of the United States will dispose of a
petition for a writ of certiorari in *Roberts v. United States*. "Granted" here
means the Court grants the petition (grants certiorari, i.e. agrees to review the
case); "denied" means it declines review.

## Governing standard

Certiorari is wholly discretionary. Under Supreme Court Rule 10, review "is not a
matter of right, but of judicial discretion," and is granted "only for compelling
reasons" — typically a genuine, entrenched conflict among the courts of appeals
or state courts of last resort, or an important unsettled question of federal
law. The overwhelming default disposition of a cert petition is **denial**:
across recent Terms the Court receives on the order of 7,000–8,000 petitions and
grants roughly 1–2% of them. The grant rate is far lower still for petitions
filed *in forma pauperis* (the unpaid docket), which are granted only a fraction
of one percent of the time.

## Facts from the snapshot that drive the outcome

Predicting only from the latest snapshot
(`record/snapshots/2026-06-28.json`):

- **Court / posture.** `court_id` is `scotus`; the originating court is the U.S.
  Court of Appeals for the Fourth Circuit (`original_court_info`). So this is a
  cert petition seeking review of a Fourth Circuit judgment.
- **Docket number `01-7733`.** This is an October Term 2001 number, and the high
  four-digit serial (`7733`) is characteristic of the Court's *in forma pauperis*
  / pro se docket rather than the paid docket (paid cases carry much lower
  serials). IFP petitions have the lowest grant rate of any category.
- **No signals of a grant.** The snapshot shows `date_cert_granted: null`,
  `date_argued: null`, and `date_reargued: null`. There is no argument date, no
  panel, and no assigned Justice — none of the indicia that accompany a granted,
  argued case.
- **No merits-stage activity.** `docket_entries` is empty, `date_terminated` is
  null, and there is no nature-of-suit or cause recorded. Nothing in the
  point-in-time record suggests the case advanced to plenary review.
- A `clusters` reference is present, but I do not fetch its contents: that would
  be acquiring a new case fact beyond the snapshot, which the predictor contract
  forbids. (For SCOTUS, an opinion cluster can attach to an ordinary order-list
  denial as readily as to a merits decision, so its mere presence is not
  probative of a grant.)

## Reasoning behind the probability

The base rate for a SCOTUS cert petition is denial, and every case-specific
signal available in the snapshot points the same way: an IFP/pro-se-style docket
number, no argument or grant date, no panel, and no merits activity. None of the
"compelling reasons" indicia under Rule 10 are visible in the record I am
permitted to use. I therefore predict **denied**.

I set `probability` (P(granted)) at **0.02** — slightly above the raw IFP grant
rate to leave room for the residual uncertainty inherent in reasoning from a thin
snapshot, but firmly on the denial side. `granted = 0`,
`predicted_disposition = "denied"`, with `confidence = 0.85`.

No per-judge votes are predicted: cert denials are typically unsigned order-list
dispositions with no recorded vote breakdown, and the snapshot names no Justices,
so `votes` is empty.
