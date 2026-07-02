# Lambert's Lessee v. Payne — evt-petition-disposition

## The legal question posed by the event

The event asks for the disposition of a **petition** in `scotus/1013133`
(`decision_target: disposition`), with the quantitative output framed as
P(granted) — i.e. the modern certiorari-style question of whether the Court
grants the petition.

## What the snapshot actually shows

The 2026-07-01 snapshot is a bare CourtListener docket shell:

- Caption: *Lambert's Lessee v. Payne* (SCOTUS).
- **No docket entries**, no docket number, no filing/argument/termination
  dates, no cert-granted or cert-denied dates, no parties beyond the caption,
  no assigned judges or panel.
- One linked opinion cluster, which indicates the case produced a published
  Supreme Court opinion.

The caption form ("X's Lessee v. Y" — the fictional-lessee style of an
ejectment action) and the sparse legacy-import shape of the record identify
this as an **early-nineteenth-century case**. Cases of that era reached the
Supreme Court by **writ of error as of right**, not by petition for
certiorari: there was no discretionary cert petition to grant or deny. The
"petition disposition" framing therefore does not map cleanly onto this case,
and the snapshot contains no petition, motion papers, or procedural history
from which a petition-stage outcome could be reasoned. I have flagged this in
`flags.json` (`data-quality`).

## Governing standard and how I applied it

With no case-specific facts to reason from, the contract calls for the most
conservative reasonable call, anchored on corpus base rates rather than a
wide guess:

- `fedcourts stats --court scotus` over resolved corpus events: **other
  78.4%**, dismissed 15.9%, denied 4.4%, **granted 1.4%** (296 resolved).
- `fedcourts query --court scotus` priors confirm the resolved historical
  SCOTUS records in the corpus are predominantly merits decisions
  (affirm/reverse on appeal or writ of error), which the disposition
  vocabulary captures as **`other`** — not grant/denial of a petition.
- The one substantive signal in the snapshot — a linked published opinion
  cluster — points the same way: the case was decided on the merits, which
  in this labeling scheme is an affirmance/reversal (`other`), not a
  "granted" petition.

## Prediction

- **`predicted_disposition: other`** — a merits disposition
  (affirmance/reversal) is by far the most likely realized label for a
  writ-of-error-era case with a published opinion, and it is also the modal
  label (≈78%) among resolved SCOTUS events in the corpus.
- **`granted: 0`, `probability: 0.02`** — P(granted) slightly above the
  corpus base rate of 1.4% to account for labeling uncertainty, but low:
  nothing in the snapshot supports a discretionary grant, and the era makes
  the grant/deny frame inapplicable.
- **`confidence: 0.4`** — deliberately modest. The disposition call rests on
  era inference and base rates, not on case facts, because the snapshot
  supplies none.
- **No per-judge votes** — the snapshot identifies no panel or assigned
  justices, so any vote list would be invented.
