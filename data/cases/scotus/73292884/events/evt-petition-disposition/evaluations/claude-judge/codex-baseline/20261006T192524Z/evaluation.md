# Evaluation — codex-baseline

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
*Rio Grande Foundation v. Toulouse Oliver*, No. 25-1248, was **denied** on the
October 5, 2026 order list after the September 28 long conference, with two
distributions on the docket and no noted dissent (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | predicted `denied` against actual `denied` |
| `brier_score` | 0.0196 | (0.14 − 0)² |
| `segment_base_rate` | 0.1722 | sal-v4 `elevated`, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 |
| `base_rate_basis` | `risk_set` | the prediction froze `band` elevated **and** `salience_version` sal-v4; the statpack table heading names sal-v4 |
| `brier_skill_score` | 0.339 | 1 − 0.0196 / 0.1722² |
| `reasoning_quality` | 0.80 | see below |

**Baseline detail.** The prediction's frozen context is band `elevated`,
`salience_version` `sal-v4`, Term 2025. The committed `metrics/statpack.md`
band table is headed `(sal-v4)`, so the version matches and the risk-set
basis applies. The table renders the most recent 10 of 10 Terms; the Terms
strictly before 2025 carrying a sal-v4 elevated row are OT2017–OT2024, the
pack holds nothing earlier, so the rendered window and the in-code ten-Term
lookback coincide and no window divergence needs flagging. Pooling the
bracketed figures weighted by their `n` gives 484 weighted grants over 2,810,
or 0.1722 (0.172242 from the unrounded `prefix_*` fields in
`statpack.json`, the figure recorded). No `vote_accuracy`,
`judgment_correct`, or `semantic_grades`: all are off-stage on a cert cell.

## What the prediction got right

The call (deny, 0.14) and the forecast (denial without opinion following the
September 28 conference, disposition in early October, zero further
distributions as the modal path) both landed. The number sits just under the
band anchor and earns a Brier skill of 0.34 against it.

## Reasoning quality (0.80)

A careful, well-bounded analysis, graded on `reasoning.md` alone.

- **The anchor is exactly right and its provenance is stated.** The
  sal-v4 elevated reached figure pooled over OT2017–OT2024 from the
  unrounded statpack fields (484 / 2,810 = 17.22%) is the cut this cell is
  scored against, and the author says which Terms, which fields, and which
  artifact vintage went into it, and that no own-Term row entered. The
  broader cuts are correctly treated as shape checks, and the second
  distribution is correctly read as straddling a response request rather
  than evidencing a substantive relist.
- **The information boundary is stated precisely.** Snapshot date, latest
  proceeding, fetch dates for the briefs, and the unavailability of the
  reply and appendix are all laid out, with an explicit statement that no
  outcome was sought or carried. That discipline is worth something on a
  forward cell.
- **The downward adjustments are sourced to the record with page cites.**
  The missing circuit split, the Tenth Circuit's narrowing construction, the
  forfeiture of the major-purpose argument, and the facial-record problems
  are each tied to the opposition's pages, and each is labelled as an
  advocacy position rather than an adjudicated finding, which is the
  honest epistemic status.
- **The NRSC reference is handled with restraint**: it is traced to the
  provisioned opposition, not independently verified, and given no
  decisive weight.

What keeps it below claude-baseline: the analysis is more descriptive than
diagnostic. It catalogues the vehicle objections and the attention signals
and reports the net, but it does not say which fact it expects the Court to
act on, or why the response request should be discounted (claude-baseline's
point that it came at the first distribution before most amici filed is
the kind of specific inference this document lacks). The external
retrieval of *AFPF v. Bonta* failed and the author correctly fell back on
the briefs, but that leaves the doctrinal discussion resting entirely on
party characterizations. The number itself is identical to claude-baseline's,
so the gap between the two grades is about the reasoning's incisiveness,
not its result.

## Leakage

Forward cell. The provisioned snapshot was dated 2026-09-17 with the
August 12 distribution as its last entry; the October 5 denial did not yet
exist when the cell ran. The captured calls are all shell reads of the
prompt, schemas, snapshot, provisioned briefs, and statpack. The four
web-search rows are `unobserved`, so they are graded on their queries: two
name the official *AFPF v. Bonta* opinion PDF and the other two a Rule 10
phrase and the same PDF; none names this petition, its caption, docket
number, or outcome. No retrieved document is dated on or after resolution.
`retrieved_outcome_material` false, `influenced_prediction`
not_applicable, `leakage_suspected` false. The candidate's `flags.json` is
not staged, so this rests on the log and the prose.

## Big-case read

My own read is 0.45: a real but mid-band case whose realized disposition was
a silent denial. The predictor's 0.70 is not graded here; the leaderboard
grades it by rank-agreement.
