# Prediction reasoning — scotus/1001370, evt-petition-disposition

## The legal question

The event `evt-petition-disposition` (kind: `petition`, decision_target:
`disposition`) asks how the Supreme Court disposed of the petition in *Davis v.
Wechsler* (docket no. 70). `granted = 1` denotes that the Court took up and
decided the matter in the petitioner's favor; `granted = 0` denotes a denial.

## The governing standard

The Supreme Court's review of a petition turns on its discretionary
certiorari jurisdiction (and, for the pre-1925 era, its then-mandatory
appellate jurisdiction over writs of error). The unconditional base rate for a
modern cert petition is overwhelmingly *denied* — well over 95% of petitions
are turned away without a merits decision. That prior is the starting point and
is only displaced by case-specific signal.

## What the snapshot actually contains

The provided snapshot
(`data/cases/scotus/1001370/record/snapshots/2026-06-29.json`) is unusually
thin. It carries docket metadata only:

- `case_name`: "Davis v. Wechsler", `docket_number`: "70", `court_id`: `scotus`.
- `date_created`: 2014-10-30 (a bulk import), `date_modified`: 2023-08-02.
- **No docket entries** (`docket_entries: []`).
- **No disposition dates**: `date_cert_granted`, `date_cert_denied`,
  `date_argued`, `date_filed`, and `date_terminated` are all `null`.
- An empty `panel` and `panel_str`, so no individual Justices are identifiable.

There is, however, one substantive signal: the docket links to an **opinion
cluster** (`clusters: [".../clusters/100264/"]`). A petition that is simply
denied does not, as a rule, generate a full merits opinion cluster. The
presence of a cluster is therefore evidence that the Court resolved this matter
with an opinion rather than a bare denial — i.e., that review was granted and
the case decided on the merits.

## How I weigh it

Two forces pull in opposite directions:

1. The strong unconditional prior that SCOTUS petitions are denied.
2. The cluster reference in the snapshot, which is characteristic of cases the
   Court *did* take and decide.

The cluster signal is the more probative of the two for this specific docket: a
linked opinion cluster is hard to reconcile with a plain denial. The docket
number ("70") and the bulk-import provenance are also consistent with an old,
fully-adjudicated case (the historical *Davis v. Wechsler* reached a merits
disposition on a writ of error), where the Court's jurisdiction was mandatory
rather than discretionary — further raising the probability that the matter was
decided rather than denied. Treating the case caption and outcome as anything
beyond the snapshot would be fetching new case facts, which the contract
forbids; I therefore rest the call on the cluster signal and base rates that are
present in or derivable from the snapshot.

I resolve toward `granted` (disposition reached, petitioner-favorable), but with
restrained confidence because the snapshot lacks the explicit disposition
fields (`date_cert_granted`/`date_cert_denied`) that would normally confirm it,
and because a cluster could in rare cases attach to an opinion respecting a
denial.

## Conclusion

- `predicted_disposition`: **granted**
- `granted`: **1**
- `probability` (P(granted)): **0.75** — above the deny-heavy prior, driven by
  the opinion-cluster signal, but held back by the missing disposition fields.
- `confidence`: **0.45** — the snapshot is sparse; the call rests on a single
  indirect signal.
- `votes`: none — the snapshot's `panel` is empty, so no per-Justice votes can
  be responsibly assigned.

### Caveat on input quality

The snapshot is largely empty of the docket entries and disposition dates a
predictor would normally use. The prediction is the most conservative
reasonable inference from the one substantive signal available (the opinion
cluster) plus base rates. A richer snapshot with docket entries or the cert
disposition dates would materially sharpen both the probability and the
confidence.
