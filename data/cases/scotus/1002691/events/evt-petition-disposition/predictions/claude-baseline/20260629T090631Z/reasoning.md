# Prediction — scotus/1002691, evt-petition-disposition

**Case:** Costco Wholesale Corporation v. Omega, S.A.
**Event:** petition disposition (decision target: `disposition`)
**Snapshot used:** `data/cases/scotus/1002691/record/snapshots/2026-06-29.json`

## The legal question

The event is a Supreme Court **petition** (`kind: petition`), so the disposition
to predict is the Court's action on the petition for a writ of certiorari:
granted (the Court agrees to hear the case) versus denied. The docket is a SCOTUS
docket (`court_id: scotus`) for a case appealed from the Ninth Circuit
(`appeal_from_str: "United States Court of Appeals for the Ninth Circuit"`),
arising from an originating judgment dated 2008-09-03 with rehearing denied
2009-02-17, and filed at the Court on 2009-05-18.

## Governing standard

Certiorari is discretionary (Sup. Ct. R. 10): the Court grants review only for
compelling reasons, most often a genuine circuit split or an important,
recurring question of federal law. The unconditional base rate is very low —
historically only a low single-digit percentage of paid petitions are granted.
A prediction that departs sharply from that base rate needs a strong,
in-snapshot signal.

## Facts from the snapshot that drive the outcome

The decisive signal is in the snapshot itself: the docket carries a linked
**opinion cluster** (`clusters: ["…/clusters/180910/"]`). On a SCOTUS docket an
opinion cluster corresponds to a merits decision, and the Court only reaches the
merits of a case after granting certiorari. The presence of that cluster is
therefore strong evidence that this petition was granted rather than denied —
denied petitions do not generate a merits opinion cluster.

Supporting context consistent with a granted petition: the case has a clean
single question posture coming out of the Ninth Circuit with a final originating
judgment and exhausted rehearing, the kind of cleanly-presented federal question
the Court takes for plenary review.

Some fields that would normally confirm a grant are null in this snapshot
(`date_cert_granted`, `date_argued`, `date_cert_denied` are all `null`). I read
these as incomplete CourtListener metadata rather than as evidence of denial,
because (a) `date_cert_denied` is *also* null — a denial would typically populate
that field — and (b) the merits cluster linkage is affirmative evidence that the
case was decided on the merits. Per the contract I predict only from this
snapshot and do not fetch new docket facts.

## Probability and disposition

Weighing the strong in-snapshot merits-cluster signal against the low cert base
rate and the residual ambiguity from the null cert-status fields, I predict the
petition was **granted**:

- `granted = 1`, `predicted_disposition = "granted"`
- `probability = 0.90` — high, driven by the opinion-cluster signal, but held
  short of certainty to account for the unpopulated cert-status fields and the
  possibility that the cluster linkage does not by itself prove a grant.
- `confidence = 0.80`.

No per-judge votes are predicted: a cert disposition is an order of the Court,
not a recorded merits vote of individual Justices, so `votes` is left empty.
