# Marcellus Henderson v. United States — ca11/66800253, evt-appeal-disposition

**Prediction: disposition `other` (merits affirmance), P(granted) = 0.05, granted = 0.**

## The case as the snapshot shows it

The provisioned snapshot (`record/snapshots/2026-07-10.json`) is sparse but tells
a coherent story:

- Eleventh Circuit docket **21-11740**, *Marcellus Henderson v. United States* —
  an individual appellant against the United States, the caption pattern of a
  federal criminal defendant or federal prisoner (direct criminal appeal or a
  § 2255-type proceeding). No nature-of-suit, panel, or party detail is present.
- The single visible docket entry is **#37, filed 2025-04-10, "Opinion Issued"**
  (PACER doc 011013810898; document not available, no plain text). Entry number 37
  on a docket opened in 2021 indicates a fully briefed appeal, not a summary
  procedural disposition.
- `date_terminated` is null and no disposition field is populated; two opinion
  clusters are linked but were **not** retrieved (see the leakage note below).

Mode is `forward` (`record/context.json`). I predicted as-if-undecided from the
pre-decision record only.

## Leakage discipline

The snapshot itself shows an opinion has issued, so this case's real disposition
almost certainly exists and would be trivially retrievable. Per the contract's
categorical rule ("predict as if undecided — never retrieve this case's
outcome"), I did **not** open the linked opinion clusters, fetch the docket, or
run any web search on this case (any headline or opinion header would reveal the
disposition). I know nothing about how the appeal actually came out. This
tension — a forward-mode cell whose snapshot already contains an "Opinion
Issued" entry — is flagged in `flags.json`.

The fact that the case was resolved *by opinion* is itself part of the
provisioned baseline, and I use it: it moves probability mass away from
procedural endings (dismissal for want of prosecution, voluntary withdrawal)
and onto merits outcomes (affirm / reverse / vacate).

## The legal question and the governing base rates

The event asks for the disposition of a federal criminal/prisoner appeal in the
Eleventh Circuit. Two layers drive the answer:

**1. Merits.** Appeals by criminal defendants and federal prisoners fail at very
high rates. Nationally, reversal (full or partial relief) in criminal appeals
runs in the mid-single digits; the Eleventh Circuit is among the most
affirmance-prone circuits, with a heavy unpublished per-curiam-affirmance
practice. Conditional on the case reaching a full opinion after complete
briefing (as here), the odds of some relief tick up modestly — call it
**~10% for any relief for the appellant**, ~90% straight affirmance.

**2. Label space.** The evaluation scores `predicted_disposition` by exact match
against `outcome.json` and `probability` by Brier against `actual_granted`. How
an appellate merits outcome gets *recorded* matters:

- The corpus normalizer (`normalize_disposition`) maps "affirmed", "reversed",
  and "vacated" to **`other`** — none carries a grant/deny/dismiss/withdraw
  keyword. An `other` disposition is not machine-readable, so this outcome will
  be recorded by a **reconcile agent**, whose instructions say to use `other`
  when none of granted/denied/granted-in-part/dismissed/withdrawn genuinely fit.
  A straight affirmance fits none of them (an appeal is "affirmed", not
  "denied"), so `other` is the most likely recorded label; `denied` is the
  plausible runner-up if the reconciler reads the event as relief-denied.
- The committed statpack's CA11 cut points the same way: of 45 resolved CA11
  corpus rows, **95.6% `other`**, 2.2% denied, 2.2% granted.

Combining the two layers, my distribution over the recorded disposition is
roughly: `other` ~0.80 (affirmance, plus reversals a reconciler still labels
`other`), `denied` ~0.08, `granted`/`granted-in-part` ~0.05 (appellant wins
*and* the reconciler maps the reversal/vacatur to a grant), `dismissed` ~0.05
(residual — e.g. a COA-denial styled as dismissal), `withdrawn` ~0.02.

## The call

- **`predicted_disposition` = `other`** — the modal recorded label for an
  Eleventh Circuit merits opinion in a criminal/prisoner appeal.
- **`probability` (P(granted)) = 0.05** — relief for the appellant is unlikely
  on the merits, and even a win only lands on the `granted` side of the binary
  if the reconciler labels it so.
- **`granted` = 0**, **`confidence` = 0.6** — the label-space reasoning is
  sound but the snapshot is thin (no issue, panel, or briefing detail), and the
  reconciler's affirmance→`other` vs affirmance→`denied` choice is a real
  source of variance.
- No `votes`: the snapshot carries no panel information.

## Degraded retrieval

The cell's configured CourtListener MCP server never connected (no tools were
available), so no CourtListener retrieval informed this prediction — see
`retrieval.md` and `flags.json`. The `fedcourts query` priors for ca11 were
noisy (visibly misjoined rows), so the statpack roll-up carried the base-rate
weight. Neither gap blocks the cell; both degrade it slightly and are flagged.
