# No. 92-7301 (scotus/1057937) — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.005, predicted
disposition `denied`, confidence 0.6.**

## What the snapshot contains

The 2026-07-08 snapshot is a sparse historical CourtListener docket (bulk
import, created 2014, no PACER lineage). It carries a caption that is nothing
but the docket number — "No. 92-7301" — plus one associated opinion cluster,
and **no parties, no lower court, no filing/argument/decision dates, no docket
entries, and no petition documents**. Every case-specific fact available is:
Supreme Court of the United States, docket No. 92-7301, decided in some form
(a cluster exists). I deliberately did not open the associated cluster: for a
decided historical case it would reveal the realized disposition, which the
contract forbids retrieving.

## What the docket number tells us

Under the Supreme Court's numbering convention, October Term 1992 paid cases
run from 92-1 upward and in forma pauperis (IFP) cases start at 92-5001. So
**No. 92-7301 is an IFP petition from October Term 1992**, roughly the 2,300th
IFP filing of the Term — on the volume of that era, filed around the winter or
spring of 1993. IFP petitions of that period were overwhelmingly pro se
prisoner filings (habeas and § 1983 appeals from summary circuit affirmances).

## Legal question and governing standard

The event asks for the disposition of the petition — for a Term-numbered
docket, certiorari (or its equivalent). Review is purely discretionary under
Supreme Court Rule 10: the Court grants only where there is a circuit conflict,
a conflict with its own precedent, or an important unsettled federal question.
The snapshot supplies no caption, no question presented, no lower court, and no
signal of any certworthiness factor (no conflict, no CVSG, no amici — nothing).

## Base rates and calibration

With zero case-specific facts, this prediction is a base-rate exercise for an
OT1992 IFP petition:

- In OT1992 the Court received roughly 7,200 petitions, over half IFP, and
  granted plenary review in about 100 cases. Paid petitions were granted at
  roughly 3–4%; **IFP petitions at a few tenths of one percent** (on the order
  of 10–15 IFP grants per Term). Including summary GVR orders, favorable action
  on a random IFP petition still sits under ~1%.
- The committed statpack's corpus cuts add little here: the early-1990s Terms
  have almost no resolved labels (OT1992: 3 resolved, all `other`), and the
  corpus-wide resolved-SCOTUS base rate (`other` 78.4%, `dismissed` 15.9%,
  `denied` 4.4%, `granted` 1.4%) blends merits-era dockets where grant/deny is
  not the live question. The statpack section for modern Term-prefixed
  discretionary-cert dockets referenced in the predict prompt is not present in
  the committed `metrics/statpack.md` (flagged).
- An era-restricted corpus query for 1990s SCOTUS priors surfaced only
  mislabeled 19th-century material (see `retrieval.md` and `flags.json`), so
  retrieved priors contribute no usable signal.

**P(granted) = 0.005** reflects the IFP base rate with a small allowance for a
GVR being labeled as a grant. **`denied`** is the modal disposition by a wide
margin: the realistic alternatives are a Rule 39/46 dismissal or a labeling of
`other` by the reconciler, and the residual probability mass sits there rather
than on `granted`.

- `granted = 0`: clear at these odds.
- `confidence = 0.6`: the binary call (not granted) is near-certain; the
  moderate confidence prices the *label-mapping* risk that this old
  cluster-backed docket reconciles to `other` (the dominant realized label
  among resolved SCOTUS corpus rows) rather than `denied`, and the smaller
  risk that 92-7301 is not a cert docket at all (e.g. an original habeas
  application — which would also be denied).
- **No per-judge votes.** Cert denials are unsigned orders; predicting nine
  individual votes on an anonymous petition would be noise, so `votes` is
  omitted.

## Data-quality note

The snapshot alone cannot support a case-specific prediction — there is no
caption to reason from. The honest output is the era- and filing-class base
rate, which is what this is. See `flags.json`.
