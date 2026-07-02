# Siler v. Illinois Central R. Co. — petition disposition

**Case:** `scotus/1017888` · **Event:** `evt-petition-disposition` ·
**Snapshot:** `data/cases/scotus/1017888/record/snapshots/2026-07-02.json`

## Prediction

- **Predicted disposition:** `other` (merits disposition — affirmance or
  reversal — rather than a discretionary grant, denial, or dismissal)
- **P(granted):** 0.02 · **granted:** 0 · **confidence:** 0.6

## What the snapshot shows

The snapshot is sparse but its shape is informative:

- A Supreme Court docket with consolidated docket numbers **"522, 523, 524"** —
  a short, un-prefixed, multi-number format characteristic of the Court's
  pre-modern (early-1900s) docket, not a modern `YY-NNNN` cert docket.
- **One linked opinion cluster** (CourtListener cluster 97007). The docket
  exists in CourtListener because the Court issued a written opinion in the
  case; this is the strongest signal in the snapshot that the matter was
  disposed of by decision rather than left pending or dropped.
- **No cert dates at all** — `date_cert_granted` and `date_cert_denied` are both
  null, consistent with a case that never passed through the certiorari
  gate.
- No docket entries, parties, panel, or filing/decision dates.

## Governing framework

The caption (a state officer versus a railroad) and the docket-number format
place this case in the early twentieth century, before the **Judiciary Act of
1925**. In that era most Supreme Court review — including direct appeals from
circuit courts in railroad rate-regulation cases like this one appears to be —
was **mandatory** (appeal or writ of error as of right), not discretionary.
There was no petition for certiorari to "grant" or "deny": the Court either
decided the case on the merits (affirmed/reversed/modified) or **dismissed**
(typically for want of jurisdiction). The case name matches the Kentucky
railroad-rate litigation of that period (companion to *Siler v. Louisville &
Nashville R.R. Co.*, 213 U.S. 175 (1909), the well-known pendent-jurisdiction
decision) — used here only as context for the era and posture, not as a source
of outcome facts.

Under this pipeline's disposition vocabulary, a merits affirmance or reversal
maps to **`other`**; `granted`/`denied` describe discretionary review, which
does not fit this event.

## Calibration against the corpus

`fedcourts stats --court scotus --resolved-only --group-by disposition` over the
296 resolved SCOTUS events in the corpus (dominated by the same historical,
opinion-backed docket population this case belongs to):

| Disposition | Share |
|---|---|
| other | 78.4% |
| dismissed | 15.9% |
| denied | 4.4% |
| granted | 1.4% |

The presence of an opinion cluster and the absence of any cert-track dates put
this case squarely in the population that resolves as `other`. The realistic
alternative is `dismissed` (want of jurisdiction was a common ground for
disposing of era appeals, and those dismissals also produced opinions), which I
weight at roughly 15–20%. A `granted` label is essentially foreclosed — there
was no discretionary petition to grant — so P(granted) is set at 0.02, at the
corpus base rate.

Approximate outcome distribution: other ≈ 0.75, dismissed ≈ 0.17, denied ≈
0.04, granted ≈ 0.02, remainder ≈ 0.02.

## Votes

No per-judge votes are predicted: the snapshot carries no panel information,
and era merits dispositions of this kind were typically unanimous or
near-unanimous in any event.

## Caveats

- The snapshot has no dates, parties, entries, or lower-court information; the
  prediction leans heavily on structural signals (docket-number format, opinion
  cluster, missing cert dates) plus corpus base rates. See `flags.json` for the
  scope note: a pre-1925 mandatory-jurisdiction case reaching the predict
  matrix may be one the scope filters intend to exclude.
