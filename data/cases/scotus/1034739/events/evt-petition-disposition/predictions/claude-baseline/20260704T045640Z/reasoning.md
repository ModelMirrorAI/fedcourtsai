# Charles W. Castleman, a[?] in Bankruptcy — evt-petition-disposition

## The legal question posed by the event

The event asks for the disposition of a **petition** in `scotus/1034739`
(`decision_target: disposition`), with the quantitative output framed as
P(granted) — the modern certiorari-style question of whether the Court grants
the petition.

## What the snapshot actually shows

The 2026-07-04 snapshot is a bare CourtListener docket shell:

- Caption: *Charles W. Castleman, a in Bankruptcy* (SCOTUS). The caption is
  visibly OCR-mangled; the underlying style is almost certainly of the form
  *In the matter of Charles W. Castleman, a Bankrupt* or *Charles W.
  Castleman, in Bankruptcy*.
- **No docket entries**, no docket number, no filing/argument/termination
  dates, no cert-granted or cert-denied dates, no parties beyond the caption,
  no assigned judges or panel.
- One linked opinion cluster, which indicates the matter produced a published
  opinion rather than an unexplained order.
- Legacy bulk-import provenance (`source: 16`, created in the 2014 import) —
  the shape of a scanned-reporter record, not a live docket.

## Identifying the matter from the caption

The "*X, a Bankrupt* / *in Bankruptcy*" caption style belongs to in-re
bankruptcy administration proceedings under the Bankruptcy Act of 1867 or the
early decades of the 1898 Act — a nineteenth- or very-early-twentieth-century
matter. Unlike some prior cells in this pipeline where the caption alone
identified a known reported decision, I do not recognize a Supreme Court case
captioned *Castleman* in bankruptcy from background legal knowledge, so no
case-specific identification informs the number. (Consistent with the rules, I
fetched no new facts about this case — I did not follow the opinion-cluster
link and did not query the corpus for this case's own row, which is the
ground-truth source.)

Two structural observations still carry weight:

1. **Era.** In the pre-1925 (Judiciary Act / Certiorari Act) era, and
   especially for bankruptcy administration under the 1867 Act, Supreme Court
   review was by writ of error, appeal, or certificate — largely mandatory
   jurisdiction. A discretionary cert petition to be "granted" or "denied" in
   the modern sense likely never existed for this matter, so the petition
   framing does not map cleanly onto the record.
2. **A published opinion exists.** Whatever happened, the matter resolved in a
   written decision. When the reconciler codes such historical records, the
   disposition overwhelmingly lands on **other** (a merits or supervisory
   decision) or **dismissed** (want of jurisdiction — common for old
   bankruptcy appeals, given the sharply limited Supreme Court bankruptcy
   jurisdiction of that era), not on granted/denied.

It is also possible this record is misattributed to SCOTUS entirely — the
legacy import contains state-court records filed under the SCOTUS docket (a
corpus prior, `scotus/1006`, is a New York Court of Appeals decision judged by
Folger). That possibility further supports a conservative, base-rate-anchored
call and is noted in `flags.json`.

## Base rates and priors

- `fedcourts stats --court scotus` over the pulled corpus: 296 resolved SCOTUS
  events — **other 78.4%**, dismissed 15.9%, denied 4.4%, **granted 1.4%**.
  The resolved set is dominated by exactly this kind of historical record, so
  unlike a modern paid cert petition (where the few-percent grant rate is the
  anchor), the relevant anchor here is the historical-record coding
  distribution itself.
- `fedcourts query --court scotus --topic bankruptcy` returned no resolved
  bankruptcy priors; the unfiltered SCOTUS priors confirm the resolved
  historical records are predominantly merits decisions coded "other".

## Probability, disposition, confidence

- **P(granted) = 0.02.** Slightly above the raw 1.4% resolved-corpus grant
  share to allow for the small chance the record turns out to be a
  certiorari-era petition that was granted (the published opinion makes a
  grant marginally more likely than for a bare stub with no cluster), but
  well below any modern cert-grant anchor since a discretionary petition
  probably never existed here.
- **predicted_disposition = other** — the modal coding for a resolved
  historical SCOTUS record with a published opinion (78% base rate), with
  "dismissed" (16%) the main alternative.
- **granted = 0**, consistent with the above.
- **confidence = 0.35** — the call is base-rate-driven with no case-specific
  facts; the main uncertainty is other-vs-dismissed coding, not
  granted-vs-not.
- **No judge votes**: the snapshot names no judges or panel, and I have no
  identification of the deciding bench.
