# Hopt v. Territory of Utah — evt-petition-disposition

## The legal question

The event asks for a petition disposition — in the modern discretionary-cert
framing, P(the Court grants review). That framing does not fit this case: the
respondent is the *Territory* of Utah (Utah became a state in 1896), so this
docket predates the Judiciary Act of 1925 and reached the Supreme Court under
its **mandatory jurisdiction** (writ of error), heard as of right. There was no
cert petition to grant or deny. The repository's own scope model
(`is_historical_mandatory`) excludes exactly this class of case from predict
scope, but the exclusion predicates key off a bare sequential docket number or a
pre-1925 `date_filed`, and this corpus row has an empty docket number and null
dates, so the case fell through the gate. See `flags.json`.

## Facts from the snapshot

The snapshot (`record/snapshots/2026-07-04.json`) is nearly bare:

- No docket entries, no docket number, and every activity date is null
  (`date_filed`, `date_argued`, `date_terminated`, cert dates).
- The one substantive signal: the docket links an opinion cluster
  (`clusters/91057`). An attached opinion means the Court **decided the case on
  the merits** — consistent with the mandatory-jurisdiction era, where matters
  taken up ended in affirmance or reversal rather than a grant/deny order.

## Legal context (not new case facts)

Hopt v. Utah is the well-known line of 1880s capital-murder writs of error from
Utah Territory (104 U.S. 631; 110 U.S. 574; 114 U.S. 488; 120 U.S. 430) — the
Court reversed the conviction three times and affirmed on the fourth. The
snapshot does not say which trip this docket is, but every one of them ended in
a **merits disposition** (reversed or affirmed), never a cert-style
granted/denied label.

## Base rates

`fedcourts stats --court scotus --resolved-only` over the corpus (296 resolved
cases, dominated by the same historical era): **other 78.4%**, dismissed 15.9%,
denied 4.4%, **granted 1.4%**. No finer cut is available — the row has no topic,
no term year, and no originating court.

## Prediction

- **`predicted_disposition: other`** — the case was decided on the merits (the
  snapshot's opinion cluster), and a merits outcome (affirmed/reversed) maps to
  `other` in this pipeline's disposition labels; this also matches the dominant
  base rate for this stratum of the corpus.
- **`granted: 0`, `probability: 0.02`** — under mandatory jurisdiction a
  "granted" label essentially cannot arise; 2% leaves headroom only for
  labeling/reconciliation noise, close to the 1.4% corpus-wide granted share.
- **`confidence: 0.6`** — the legal-historical read is firm, but the dominant
  residual uncertainty is how the outcome reconciler will label a
  120-year-resolved merits case (`other` vs `dismissed`, or never resolvable
  from this bare record).
- **No per-judge votes** — the snapshot carries no panel and the event targets
  disposition only.
