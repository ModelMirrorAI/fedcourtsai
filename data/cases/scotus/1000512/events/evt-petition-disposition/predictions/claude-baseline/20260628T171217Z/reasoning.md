# Prediction reasoning — scotus/1000512, evt-petition-disposition

## The legal question

The event `evt-petition-disposition` for *Estes v. Gunter* is a **petition**
event with `decision_target: disposition`. In the Supreme Court of the United
States (`court_id: scotus`), the petition at issue is a **petition for a writ of
certiorari**. The question to predict is whether the Court will **grant** that
petition (i.e., agree to hear the case) or **deny** it.

## The governing standard

Certiorari is wholly discretionary. Under Supreme Court Rule 10, review "is not a
matter of right, but of judicial discretion," granted "only for compelling
reasons" — typically a genuine, entrenched conflict among the courts of appeals
(or between a state court of last resort and another such court or this Court) on
an important federal question, or a decision so far departing from the accepted
course of judicial proceedings as to call for the Court's supervisory power. The
"rule of four" governs: it takes the votes of four Justices to grant the writ.

The empirical base rate follows directly from that discretion: the Court receives
on the order of 7,000–8,000 petitions per Term and grants roughly 60–80 — i.e.,
well under ~1.5% overall, and lower still for unpaid (in forma pauperis)
petitions. Absent an affirmative, case-specific signal of cert-worthiness, the
overwhelmingly likely disposition of any given petition is **denial**.

## Facts from the snapshot

Per the instruction to predict **only** from the provisioned snapshot
(`record/snapshots/2026-06-28.json`), the available facts are sparse:

- `case_name`: "Estes v. Gunter"; `court_id`: `scotus`; `id`: 1000512.
- `date_argued`, `date_cert_granted`, `date_cert_denied`, `date_terminated`,
  `date_filed`: all **null**.
- `docket_entries`: empty; `panel` / `assigned_to`: empty; `docket_number`: empty.
- One opinion-cluster reference is present in the record, but the snapshot
  exposes no disposition fact (no grant/deny date, no terminated date), and the
  event is unresolved (`event.yaml: resolved: false`). I do **not** fetch or infer
  case facts from that external cluster, per the contract (predict from the
  snapshot; the CourtListener MCP is for legal context only, never new case
  facts). The bare cluster pointer is therefore treated as non-dispositive.

There is **no** affirmative signal of cert-worthiness in the snapshot — no
recorded circuit split, no call for the views of the Solicitor General, no
relisting, no argument date, no granted date. Nothing distinguishes this petition
from the great mass of petitions that are denied.

## Reasoning behind the probability

With no case-specific factor displacing the base rate, the prediction defaults to
that base rate. SCOTUS grants a very small fraction of petitions, and the absence
of any cert-worthiness signal here pushes the estimate toward (not above) the
unconditional grant rate.

- `predicted_disposition`: **denied**.
- `granted`: **0**.
- `probability` (P(granted)): **0.03** — set marginally above the raw ~1% grant
  rate to leave room for unobserved merit signals that a thin snapshot may omit,
  while still reflecting that denial is overwhelmingly likely.
- `confidence`: **0.6** — the directional call (denial) is well supported by the
  base rate, but the snapshot is thin enough that I avoid overstating certainty.

## Votes

The rule of four governs a cert grant, but the snapshot exposes no panel,
assignment, or Justice-level information, and individual Justices' cert votes are
not public. I therefore record **no** per-judge votes (`votes: []`) rather than
fabricate them.

## Headless-run note

This run is headless (CI, non-interactive). The snapshot is valid but sparse; it
is not missing or malformed, so no blocker exists that would warrant a comment on
the triggering issue. The conservative base-rate call above is recorded here in
full for maintainer follow-up.
