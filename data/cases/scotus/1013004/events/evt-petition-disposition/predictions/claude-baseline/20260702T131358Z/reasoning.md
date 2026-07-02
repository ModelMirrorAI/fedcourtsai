# Prediction reasoning — scotus/1013004, evt-petition-disposition

## The legal question

The event asks for the disposition of a petition before the Supreme Court of
the United States in *Riche and Richards v. Broadfield* (docket 1013004):
granted, denied, dismissed, or otherwise resolved, with P(granted).

## Governing standard

For a modern discretionary petition (a writ of certiorari), review is granted
only for "compelling reasons" (Sup. Ct. R. 10) — a circuit split, an important
unsettled federal question, or a departure from the Court's precedent — and the
empirical grant rate is on the order of a few percent. For cases that reached
the Court before the Judiciary Act of 1925, however, jurisdiction was largely
mandatory (writ of error or appeal), so a "petition disposition" framing maps
onto how the Court ultimately disposed of the matter rather than a
grant/deny gate.

## Facts available from the snapshot

The latest snapshot (`record/snapshots/2026-07-01.json`) is a CourtListener
bulk-import stub and carries almost no predictive features:

- `docket_entries` is empty — no motions, briefs, orders, or scheduling.
- Every date field is null: `date_filed`, `date_argued`, `date_cert_granted`,
  `date_cert_denied`, `date_terminated`.
- No docket number, `nature_of_suit`, `cause`, or jurisdiction/appeal metadata,
  and no panel or assigned judges — so no per-judge votes can be predicted.
- `date_created` = `date_modified` = 2014-10-30, i.e. the docket was created in
  a bulk import and never enriched afterwards.
- The one substantive signal is a single linked opinion cluster (a low-numbered
  cluster id, consistent with the historical SCOTUS opinion corpus). Its
  existence indicates the matter produced a reported decision, but the snapshot
  does not expose the decision's content or direction, and I may not fetch new
  case facts to resolve it.

The caption (two private petitioners against a private respondent, no docket
number, opinion-derived record) is consistent with a 19th- or early
20th-century case that reached the Court on mandatory review.

## Base-rate context from the corpus

`fedcourts stats --court scotus --resolved-only` over the corpus — whose
resolved SCOTUS cases are drawn from the same bulk-import population as this
docket, with dispositions reconciled from the linked opinion — gives:

| Disposition | Share |
|-------------|-------|
| other       | 78.4% |
| dismissed   | 15.9% |
| denied      | 4.4%  |
| granted     | 1.4%  |

`fedcourts query --court scotus` priors confirm the pattern: sparse
opinion-derived dockets of this vintage overwhelmingly resolve as merits
decisions (affirmed/reversed → labeled `other`), with a substantial minority
dismissed for want of jurisdiction, and `granted`/`denied` labels rare.

## Reasoning behind the probability

The snapshot contributes essentially nothing case-specific beyond the linked
opinion cluster, so the calibrated prediction is the base rate for this exact
population, nudged by the one available signal:

- The linked cluster means a reported decision exists, which points **away**
  from a summary `denied` label and **toward** a merits disposition (`other`)
  or a `dismissed` (e.g., for want of jurisdiction) — exactly the two labels
  that dominate the resolved-corpus distribution.
- **Predicted disposition: `other`** — the modal label at ~78%, and the most
  likely reconciliation of a historical merits opinion.
- **P(granted) = 0.02, `granted` = 0** — near the corpus rate for a `granted`
  label (~1.4%) and consistent with the low modern cert-grant anchor; nothing
  in the snapshot supplies a cert-worthiness signal that would move it up.
- **Confidence = 0.5** — the label distribution is well characterized, but the
  mapping from this particular opinion to a reconciled label is not observable
  from the snapshot, and `dismissed` remains a live (~16%) alternative.

No per-judge `votes` are predicted because the snapshot exposes no panel or
assigned judges.

A `flags.json` accompanies this prediction: the snapshot is a bare bulk-import
stub (data-quality), and the case appears to predate the discretionary
certiorari regime, making it a candidate for the pre-1925
mandatory-jurisdiction predict-scope exclusion (scope).
