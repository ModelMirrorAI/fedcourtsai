# Rationale — claude-baseline on scotus/9026000121, evt-petition-arrival-disposition

**P(grant family) = 0.01.** Forward cell, arrival moment: the snapshot shows a
paid petition docketed July 27, 2026 (No. 26-121), zero distributions, response
due August 26, 2026. Frozen context: band `baseline` under `sal-v2`,
`distribution_count` 0, no CVSG, Term 2026.

## Anchor

Per the arrival-moment rule I anchored on the **weakest band's bracketed
`reached` rate** — the whole paid scored segment's grant rate, unconditional on
a trajectory that does not exist yet. The frozen band is `baseline`, which is
that weakest band, and the context's `salience_version` (sal-v2) matches the
statpack table's heading. Pooling the `baseline` bracketed `reached` figures
over every rendered Term (2017–2025, all strictly before this case's Term 2026):
weighted by their n's, ≈ **6.5%** (5.4%–8.0% per Term, n totalling ~13,200).
That is the yardstick this cell is scored against.

## Adjustments — all downward, and substantial

1. **QP 1 is fact-bound.** The Caperton/Williams/Lavoie claim turns on whether
   retired Senior Judge Jackson was "practicing law" (and hence categorically
   ineligible for recall) *when* he signed the December 14, 2023 fee order. The
   Appellate Court of Maryland, quoted in the petition itself, held the
   evidence — a LinkedIn post and a November 2023 employment agreement —
   insufficient to establish that predicate. The Court does not grant cert to
   re-weigh a disputed factual record, and the petition styles the question as
   one "of first impression," i.e. it alleges **no split** of any kind.
2. **Vehicle defects.** The Maryland Supreme Court granted review only on a
   different, state-law question (Rule 1-341 fees) and then dismissed on state
   procedural grounds (Rule 8-602), with the mandate issued. The federal issue
   arrives through an *unreported* intermediate-court opinion, and the petition
   must argue around an adequate-and-independent-state-ground bar — it devotes
   pages to doing so, which signals the problem's size.
3. **QP 2 is not a federal question.** It asks for "summary reversal" because
   the Maryland Supreme Court's own later Sugarloaf decision allegedly vindicates
   an argument made below. A state court's state-law ruling cannot support
   certiorari, let alone summary reversal.
4. **Stakes and presentation.** A private dispute over fee awards downstream of
   a $140,000 fraud verdict; solo-practitioner counsel; diffuse, error-correction
   style drafting. None of the usual grant machinery (amici, repeat SCOTUS
   counsel, government involvement) is present or likely.

Against that, one modest upward consideration: the underlying irregularity — a
one-page order, nearly verbatim from respondents' ex-parte-served proposed
order, signed by a retired judge days from (or into) full-time work as a county
attorney — is genuinely colorful, and the judicial-ethics theme occasionally
draws attention. It is not enough to move the number materially: petitions that
end in the `baseline` band grant at ~0.8–1.2% (plus ~0.4% GVR), and this one is
weaker than that population's average on every grant-relevant axis except
color. **0.01** sits between the ended-baseline rate and the unconditional
6.5% anchor, far closer to the former, which is where the specifics put it.

## Claims

- `disposition` 0.01 — identical to the top-level probability, as required.
- `relist-increment` 0.96 — the snapshot shows zero distributions, so the claim
  resolves true on *any* future distribution. A docketed paid petition with a
  response date set is nearly certain to reach at least one conference; the
  complement covers withdrawal, Rule 46 dismissal, or a docket-capture gap.
- `cvsg-increment` 0.005 — the paid-segment CVSG rate is ~1.3% and this
  all-private, state-law case sits far below it.

## Uncertainties and discounts

- **No brief in opposition exists yet** (response due August 26, 2026), so I am
  reading the petition unopposed; a BIO could only strengthen the deny case,
  so the asymmetry is small.
- The provisioned `questions-presented.txt` and `petition.txt` carry OCR
  spacing artifacts, but the text is fully legible; no content was inferred
  from a blank file (`empty_text` false on both).
- The corpus `query` surface filters on structured fields only, so I could not
  retrieve Caperton-adjacent priors specifically; the statpack carried the
  base-rate weight instead (see `retrieval.md`).
- Read where to discount me: if the respondents waive and the petition draws an
  unexpected relist, the trajectory conditional on that would sit above this
  number; nothing in today's record predicts it.
