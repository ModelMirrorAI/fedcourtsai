# Peyton v. Brooke — `evt-petition-disposition`

## The legal question

The event asks for the **disposition** of the petition in this Supreme Court
matter (`scotus/1013114`, *Peyton v. Brooke*). The prediction is the categorical
outcome (granted / denied / granted-in-part / dismissed / withdrawn / other)
plus P(granted).

## What the snapshot tells me — and what it does not

I predict only from the latest provisioned snapshot
(`data/cases/scotus/1013114/record/snapshots/2026-07-01.json`). It is a
bulk-import docket shell with essentially no procedural record:

- `docket_entries: []` — no filings, no petition text, no order text.
- Every date field is null: `date_filed`, `date_argued`, `date_terminated`,
  and — notably — `date_cert_granted` and `date_cert_denied` are both null.
- No docket number, no nature of suit, no cause, no panel or assigned judge.
- The only substantive signals are the adversarial party-v-party caption
  ("Peyton v. Brooke") and a single linked opinion cluster.

I did not open the linked cluster and did not fetch any new facts about this
case: the realized disposition is exactly the quantity under evaluation, so
resolving the opinion would be reading the answer. For the same reason, while I
recognize the caption as matching a reported early Marshall-era case, I rely
only on the **era inference** that recognition supports — not on any remembered
outcome or holding.

## Governing context and the right reference class

Two pieces of legal context (not new case facts) frame the prediction:

1. **Era and jurisdictional regime.** This docket sits in CourtListener's
   historical bulk import (created 2014, no PACER linkage, no cert dates). The
   corpus's decided SCOTUS priors are overwhelmingly matters from the era of
   **mandatory appellate jurisdiction** — writ of error and direct appeal —
   rather than modern discretionary certiorari. A party-v-party caption of this
   vintage, carrying a reported opinion cluster, is characteristic of a case
   that reached the Court as of right and was decided **on the merits**
   (affirmed or reversed). The familiar "~99% of cert petitions are denied"
   base rate is the wrong prior for this reference class.

2. **Corpus base rates** (`fedcourts stats --court scotus`, 296 resolved
   priors):

   | disposition | share |
   |-------------|-------|
   | other       | 78.4% |
   | dismissed   | 15.9% |
   | denied      |  4.4% |
   | granted     |  1.4% |

   "other" — the natural label for a writ-of-error or appeal resolved on the
   merits — is the modal outcome by a wide margin, and an outright "granted"
   disposition is rare. I also sampled resolved priors with
   `fedcourts query --court scotus`; they confirm the same picture (mostly
   "other", a minority "dismissed", with no per-case features recorded that
   would distinguish this matter).

## Reasoning to the prediction

The snapshot offers no case-specific merits signal to move off the
reference-class base rate, so I predict the modal outcome of that class,
nudged slightly by the one structural fact the snapshot does carry: the
existence of a reported opinion cluster makes a merits disposition ("other")
somewhat more likely, and a summary cert-style denial less likely, than the
unconditional base rate already implies.

- `predicted_disposition`: **other** — the modal label for a historical
  party-v-party SCOTUS matter with a reported opinion.
- `granted`: **0** — a "granted" disposition carries only ~1.4% prior weight
  and nothing in the snapshot raises it.
- `probability` (P(granted)): **0.03** — anchored just above the ~1.4% base
  rate to leave room for label-mapping uncertainty on a fact-free snapshot,
  but kept low.
- `confidence`: **0.55** — I am fairly confident the outcome is not "granted",
  but the exact categorical label ("other" vs. "dismissed") is genuinely
  uncertain when the snapshot records no posture at all.

No per-judge `votes` are offered: the snapshot carries no panel or Term
information, so any vote slate would be fabricated.

## Caveats

This is a low-information, reference-class prediction. If a richer snapshot
later adds docket entries, the case's Term, or the opinion's posture, the
categorical label could shift (e.g. toward "dismissed" for a jurisdictional
disposition) even though P(granted) would remain low. See `flags.json` for the
data-quality note on the empty snapshot.
