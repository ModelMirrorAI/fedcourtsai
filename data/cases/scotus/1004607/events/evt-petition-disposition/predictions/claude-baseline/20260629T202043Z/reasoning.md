# Keels v. Central R. Co. Of South Carolina — `evt-petition-disposition`

## The legal question

The event asks for the **disposition** of the petition in this Supreme Court
matter (`scotus/1004607`, docket no. "1,207"). The prediction is the categorical
outcome (granted / denied / granted-in-part / dismissed / withdrawn / other) plus
P(granted).

## What the snapshot tells us — and what it does not

I predict only from the latest snapshot (`record/snapshots/2026-06-29.json`). That
snapshot is extremely thin: it is a bulk-import docket shell with **no docket
entries, no dates** (`date_argued`, `date_filed`, `date_cert_granted`,
`date_cert_denied`, `date_terminated` are all null), **no panel, no assigned
judges, no cause or nature-of-suit**. The only substantive signals are the case
name (a litigant v. a South Carolina railroad), the integer-style docket number
"1,207", and a single linked opinion cluster. There is therefore **no
case-specific merits signal** to move off the base rate, and I did not fetch any
new facts about the case (snapshot-only rule).

## Governing context and the right reference class

I used `fedcourts query --court scotus` to pull the corpus's decided SCOTUS priors
for legal context (not new case facts). That reference class is decisive here:
these are **early-twentieth-century Supreme Court matters** — the named justices
across the priors are Holmes, Taft, Brandeis, Van Devanter, Pitney, White,
Sutherland, Butler, etc., and the cases arrive as "ERROR TO" / "APPEAL FROM" the
district courts. This is the era of **mandatory appellate jurisdiction** (writ of
error and direct appeal), not modern discretionary certiorari. The familiar
"~99% of cert petitions denied" base rate does **not** apply; these matters are
overwhelmingly resolved on the merits.

The realized-disposition distribution across 244 decided SCOTUS priors in the
corpus:

| disposition | share |
|-------------|-------|
| other       | 75.0% |
| dismissed   | 18.9% |
| denied      |  4.5% |
| granted     |  1.6% |

"other" (merits affirmance/reversal — the natural label for a writ-of-error or
appeal decided on the merits) is the modal outcome by a wide margin, and an
outright "granted" disposition is rare (1.6%).

## Reasoning to the prediction

With no case-specific facts to distinguish this matter from its reference class, I
predict the modal outcome of that class. "Keels v. Central R. Co. Of South
Carolina" reads as a litigant-versus-railroad matter that, like its peers, would
most plausibly have reached the Court by writ of error/appeal and been decided on
the merits — an **"other"** disposition.

- `predicted_disposition`: **other** — the modal label for this reference class.
- `granted`: **0** — a granted disposition carries only ~1.6% prior weight, and
  nothing in the snapshot raises it.
- `probability` (P(granted)): **0.03** — anchored just above the 1.6% base rate to
  leave room for snapshot uncertainty, but kept low.
- `confidence`: **0.55** — I am fairly confident the outcome is *not* "granted",
  but the exact categorical label (other vs. dismissed) is genuinely uncertain on
  a fact-free snapshot, so confidence is only moderate.

No per-judge `votes` are offered: the snapshot carries no panel, and the corpus
priors show no reliable composition for this matter, so any vote slate would be
fabricated.

## Caveats

This is a low-information prediction driven by the reference-class base rate rather
than case-specific merits. If a richer snapshot later adds docket entries, the
linked opinion's posture, or the disposition language, the categorical label
("other" vs. "dismissed" for want of jurisdiction) could shift even though
P(granted) would remain low. See the accompanying `flags.json` for the
data-quality note on the empty snapshot.
