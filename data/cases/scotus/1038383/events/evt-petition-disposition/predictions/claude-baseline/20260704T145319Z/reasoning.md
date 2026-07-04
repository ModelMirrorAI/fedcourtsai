# Prediction reasoning — scotus/1038383, evt-petition-disposition

## Legal question

The event is a `petition` with `decision_target: disposition`: predict how the
Supreme Court disposed of the petition for review in *United States v. Hodge* —
granted (taken up for plenary review) versus denied/dismissed/withdrawn/other.

## Governing standard

Modern review by certiorari is discretionary and the grant rate is a few
percent, which anchors any petition drawn at random. But that framework is
displaced when the record shows the case is not a modern cert-docket petition
at all — which is what this snapshot shows.

## Facts from the snapshot

The provisioned snapshot (`record/snapshots/2026-07-04.json`) is a near-empty
docket shell:

- Caption **"United States v. Hodge"** in the Supreme Court.
- **One linked opinion cluster** (`clusters: [.../clusters/86456/]`) — a very
  low cluster id, consistent with an early-era published opinion. The docket
  exists because CourtListener scraped a decided opinion, not because it tracks
  a live cert petition.
- **Everything else is empty**: no docket entries, no docket number, no
  filed/argued/terminated dates, no cert-granted or cert-denied dates, no
  panel, no originating court.

I predict only from this snapshot; I did not fetch the cluster contents or any
new docket facts.

## Recognition of the case (and a candor note)

The caption matches antebellum-era Supreme Court litigation my legal-background
knowledge recognizes: *United States v. Hodge*, 44 U.S. (3 How.) 534 (1845),
and a related sequel at 47 U.S. (6 How.) 279 (1848), disputes with a New
Orleans postmaster's sureties over a mail-carriage bond. The snapshot does not
say which (it has no docket number, date, or citation), so I do not rest the
prediction on identifying one of them. What matters, and holds for either
candidate, is the era: cases of that period reached the Court on **writ of
error — mandatory review — not by petition for certiorari**. There was no
cert-stage grant/deny decision to make; the Court simply heard the case and
issued a merits opinion, which is exactly what the linked opinion cluster
shows. Because these are decided historical cases, any recognition is
training-data leakage; flagged in `flags.json`.

## Base rates consulted

`fedcourts stats --court scotus` on the pulled corpus: of 296 resolved SCOTUS
cases, the realized labels are **`other` 78.4%**, `dismissed` 15.9%, `denied`
4.4%, `granted` 1.35%. Grouping by `term_year` returned no populated buckets
(these historical dockets carry no filed dates), so no era-specific cut was
available. `fedcourts query --court scotus` shows the resolved set is made of
exactly this case's shape — sparse historical docket shells with an opinion
cluster — and they overwhelmingly resolve to `other`.

## Probability and prediction

Two independent lines converge:

1. **Substance.** A writ-of-error era case with a published merits opinion has
   no certiorari grant/denial; a petition-disposition label for it most
   naturally falls outside granted/denied — i.e. `other`.
2. **Labeling empirics.** The corpus's resolved SCOTUS cases of this exact
   shape are labeled `other` at ~78%, with `granted` at ~1.4%.

I set `predicted_disposition = other`, `granted = 0`, and
`probability` (P(granted)) = **0.05** — slightly above the 1.35% resolved base
rate because the case *did* receive plenary consideration and a merits
opinion, so a labeler that codes "the Court took the case up" as `granted`
would code this one that way. `confidence = 0.55`: the modal class is fairly
clear from the corpus's own labeling behavior, but the snapshot carries almost
no case-specific signal and the label mapping for historical merits cases is
the dominant uncertainty (the residual non-`other` mass mostly belongs to
`dismissed`, the second-most-common label).

No per-judge votes: the snapshot exposes no panel, and per-justice votes on
taking up a writ-of-error case were not a recorded decision in that era.
