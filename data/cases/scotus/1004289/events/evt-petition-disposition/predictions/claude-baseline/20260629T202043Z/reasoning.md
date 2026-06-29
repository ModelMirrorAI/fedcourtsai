# Prediction reasoning — scotus/1004289, evt-petition-disposition

## The legal question

The event (`kind: petition`, `decision_target: disposition`) asks for the
**disposition** of the petition in *Harris v. United States*, a Supreme Court of
the United States matter (docket number `93-7515`). The outcome space is the
standard disposition enum (granted / denied / granted-in-part / dismissed /
withdrawn / other); `granted` is the binary target and `probability` is
P(granted). At this posture the petition is a petition for a writ of certiorari,
so "granted" means **cert granted**.

## What the snapshot tells me

I predict only from the provisioned snapshot
(`data/cases/scotus/1004289/record/snapshots/2026-06-29.json`). I did not fetch
new docket facts or look up the historical outcome — that outcome is exactly the
quantity under evaluation. The snapshot is a bare metadata stub:

- `docket_entries: []` — no filings, no petition text, no order text.
- `date_argued`, `date_filed`, `date_cert_granted`, `date_cert_denied`,
  `date_terminated`, `date_reargued` are all `null` — no recorded grant signal.
- No `nature_of_suit`, no `cause`, no question presented, no merits argument.

A few **structural** identifiers visible on the face of the snapshot carry real
signal and are not "new facts":

- **Docket number `93-7515`.** Within a SCOTUS Term, docket numbers above
  ~5000 are the **in forma pauperis (IFP) / "pauper" docket**; numbers below
  that are the paid docket. `7515` places this squarely on the IFP docket for
  October Term 1993.
- **Party posture.** The respondent is the **United States** and the petitioner
  (Harris) is the moving party — the classic profile of a pro se criminal
  defendant / post-conviction petitioner seeking review of a federal conviction
  or sentence.

## How I reach a probability

The governing reality is the **base rate**, which is general legal context
rather than a case-specific fact. The Supreme Court grants certiorari on only a
small fraction of the petitions it receives — on the order of 3–5% of *paid*
petitions in a typical Term. The grant rate on the **IFP docket**, where this
petition sits, is dramatically lower — well under 1% (roughly one in several
hundred to one in a thousand). Pro se criminal petitions against the United
States are the modal IFP filing and almost uniformly denied without comment on
an order list.

The snapshot supplies no countervailing signal that would lift this case out of
the base rate: no argument date, no cert-granted date, no question presented
flagged as cert-worthy, no indication of a circuit split or government
acquiescence. Absent any such signal, the most probable disposition by a wide
margin is **denied**.

I therefore predict:

- `predicted_disposition`: **denied**
- `granted`: **0**
- `probability` (P granted): **0.01** — pinned near the IFP grant base rate,
  floored slightly above zero to acknowledge the irreducible residual chance any
  given petition is the rare grant.
- `confidence`: **0.2** — the *direction* (denial) is held with high conviction,
  but the snapshot is too thin to support a sharply calibrated probability, so I
  keep stated confidence modest. The `probability` already encodes strong
  certainty of denial.

No per-judge `votes` are recorded: cert dispositions on the order list are not
individually attributed, and the snapshot lists no panel.

## Caveats

The prediction rests almost entirely on structural base rates because the
snapshot carries no substantive docket content (empty `docket_entries`, null
dates). This is expected for an older SCOTUS docket stub and is not a defect in
the run, but it does mean the estimate cannot be refined beyond the IFP base
rate. I record this in `flags.json` as an informational data-quality note.
