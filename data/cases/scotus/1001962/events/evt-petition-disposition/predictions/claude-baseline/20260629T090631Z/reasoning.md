# Prediction reasoning — scotus/1001962, evt-petition-disposition

## The legal question

What is the disposition of the petition in *Tindal v. Wesley* (Supreme Court
docket No. 281)? The event's `decision_target` is the petition's **disposition**;
for these SCOTUS petition events "granted" denotes that review was granted and the
case carried to a merits disposition rather than refused.

## Governing standard

The ordinary base rate for a modern discretionary certiorari petition is
overwhelming denial — review is "not a matter of right, but of judicial
discretion" (Sup. Ct. R. 10), and the Court grants on the order of ~1% of
petitions. **That base rate does not govern this case.** Two features of the
snapshot place it outside the modern discretionary-cert regime, and the
snapshot-specific signal controls over the generic prior.

## Facts from the snapshot that drive the outcome

Reasoning rests solely on the provisioned snapshot
(`data/cases/scotus/1001962/record/snapshots/2026-06-29.json`):

- **A decided opinion cluster is linked.** The `clusters` field contains one
  entry (`.../clusters/1446533/`). In CourtListener's model an opinion cluster is
  created for a case that was **decided with an opinion**. A refused/denied
  petition does not generate an opinion cluster — it appears only as a line in an
  orders list. The presence of a cluster is therefore a strong, direct signal
  that this case was taken up and resolved on the merits, i.e. review was
  *granted/exercised*, not refused.
- **The docket number is old-style ("281"), not a modern cert number.** Modern
  cert petitions carry numbers like `01-7700`; a bare low integer such as `281`
  is consistent with a pre-1925 case that reached the Court by **writ of error or
  appeal as of right** under the Judiciary Acts, before the discretionary
  certiorari regime created by the Judiciary Act of 1925. Under that earlier
  regime there was no discretionary "grant" to refuse — the Court heard the case
  and rendered a merits judgment. (*Tindal v. Wesley* is the well-known
  sovereign-immunity decision at 167 U.S. 204 (1897), reviewed on writ of error
  from a state court and decided on the merits — legal context consistent with the
  snapshot, not a new case fact.)
- **The remaining fields are sparse but non-contradictory.** `date_argued`,
  `date_cert_granted`, and `date_cert_denied` are all null and `docket_entries`
  is empty — typical of a thin historical import. `date_created` (2014) is the
  CourtListener import date, not a litigation date, and carries no weight. None of
  these absences cut against the cluster signal; they merely reflect an incomplete
  historical record.

## Probability and disposition

The decisive, snapshot-grounded fact is the linked opinion cluster, which
indicates the case was decided on the merits — review was granted/exercised
rather than refused. I therefore predict **disposition = granted**
(`granted = 1`).

I set **P(granted) = 0.80** rather than near-certainty because of a genuine
framing ambiguity: this petition-disposition event template is oriented to the
modern discretionary-cert binary, while this is a pre-1925 mandatory-jurisdiction
case whose merits result (an affirmance on writ of error) does not map cleanly
onto the granted/denied/dismissed enum. The cluster reliably tells us the case
was decided; how that maps to the event's "granted" label is the residual
uncertainty captured in the probability. **Confidence is moderate (0.6)** for the
same reason — the underlying decided-on-the-merits signal is strong, but the
label mapping for a pre-cert-era case is not airtight.

## Votes

No panel, judge assignment, or per-Justice vote breakdown is present in the
snapshot (the `panel` list is empty), and historical merits votes are not
recorded here, so no per-judge votes are emitted.

## Note on data quality

This is a pre-1925 SCOTUS case carrying a generic `evt-petition-disposition`
event whose granted/denied framing assumes the modern discretionary-certiorari
regime. The mapping of a writ-of-error merits disposition onto the petition
disposition enum is imperfect; a maintainer may wish to model pre-cert-era
review separately. This is flagged here rather than treated as a blocker — the
snapshot is sufficient to make the reasonable call above.
