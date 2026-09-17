# Rationale for the numbers

**P(grant) = 0.01; predicted disposition: denied.**

## Inputs read

- `record/snapshots/2026-09-17.json` (the provisioned baseline named by
  `context.json`): paid docket 25-1333, docketed June 1, 2026, from the
  Wisconsin Court of Appeals, District II (the Wisconsin Supreme Court denied
  review February 12, 2026). Three entries: petition filed May 13, 2026;
  waiver of right to respond by Wisconsin filed June 2, 2026; distributed
  June 24, 2026 for the Conference of September 28, 2026. No amici, no CVSG,
  no call for response.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  distribution_count 1, cvsg_date null, term 2025, cutoff null,
  signals_observable true.
- `record/documents/questions-presented.txt` and `petition.txt` (44 pages,
  text extracted, not truncated). There is no brief in opposition because the
  State waived; `documents.json` lists only the petition and its QP cut.
- `metrics/statpack.md`: the modern-cert disposition table, the relist and
  CVSG cuts (paid scored segment), and the sal-v4 "Segment base rate by
  salience band" table.

## Anchor

The context band is `baseline` and the statpack's band table is computed under
the same `sal-v4`, so the table is a valid anchor. This is a Term-2025 docket,
so I pool the bracketed `reached` figures for `baseline` over Terms 2017–2024
(the eight rendered Terms strictly before this one):

| Terms pooled | weighted grants | risk-set n | pooled reached rate |
| --- | --: | --: | --- |
| 2017–2024 | ~593 | 11,580 | ~5.1% |

That 5.1% is the grant rate among paid private-petitioner petitions that ever
reached the baseline band, and it is the yardstick the evaluator will score
this cell against. The petitioner is a private criminal defendant and the
State is respondent, so the caption class is private and `baseline` is the
right floor either way.

## Adjustments, all downward

1. **Response waived, no call for response yet.** The Court does not grant
   without a response on file. From a single-distribution, response-waived
   state, a grant requires the Court first to call for a response and then to
   grant; both steps are unlikely for this petition. The relist-count cut
   shows relist-0 petitions in the paid segment grant at about 1.2% plus 0.5%
   GVR, and that bucket is where this petition most likely ends.
2. **No split, and the petition says so.** The reasons for granting concede
   that "there appears to be no clear legal precedent either approving or
   disproving" the practice. The argument is that the practice is common and
   unexamined, which is not a Rule 10 reason.
3. **Vehicle problems visible in the petition itself.** Trial counsel did not
   object to admission of the Dodge County evidence; the issue reached the
   Wisconsin courts partly through an ineffective-assistance claim, and the
   court of appeals held admission proper in that frame. The decision below is
   an unpublished per curiam, and the state supreme court denied review
   without opinion. Preservation and possible independent-state-ground
   questions would deter a grant even if the Court were interested.
4. **The QP is abstract and multi-clause.** It stacks Fifth, Sixth, and
   Fourteenth Amendment theories into one question and adds a structural-error
   argument the Court has never entertained for an evidentiary ruling. The
   Court's existing other-acts framework (Huddleston, Dowling) points the other
   way, so a grant would more likely be to reject the theory than to adopt it,
   and the Court rarely grants an unpreserved, split-free case for that.
5. **Counsel and presentation.** A local Milwaukee firm with no Supreme Court
   practice; the brief is short, has citation errors, and no amicus support.
   These are weak signals individually but correlate with denial.

Against these, the only upward factor is that the petition is paid and
counseled rather than pro se IFP, which the baseline floor already prices in.
I land at 0.01, roughly one-fifth of the band floor. I would not go lower than
about 0.007 because the Court's long conference does occasionally produce a
call for response on a petition like this, and a grant path exists in
principle.

## Claims

- `disposition` 0.01: equals the top-level probability.
- `relist-increment` 0.12: from a one-distribution state. The paid-segment
  relist cut shows about a quarter of resolved petitions ended with at least
  one more distribution, but that terminal figure includes reschedules and
  response-driven redistributions, and this petition lacks the features that
  drive them. I take roughly half of the population rate.
- `cvsg-increment` 0.005: state criminal case, no federal interest.
- `summary-disposition-route` 0.35: conditional on a grant. Among baseline-band
  grants the GVR share is roughly a third (0.4% GVR against 0.8% granted in the
  band table). No intervening decision fits this case, so I stay near that
  population share rather than above it.
- `dissent-from-denial` 0.02: unpublished decision, no split, no evident
  Justice-level interest in the issue.

## Stakes

`big_case_score` 0.08. The question could in principle matter to defendants
facing parallel prosecutions, but this vehicle would resolve it narrowly if at
all, and the case has drawn no outside attention.

## Retrieval and its limits

I ran one `fedcourts query` against the corpus (recent SCOTUS rows); it
returned unrelated interim applications and I did not use its rows. One
CourtListener MCP search for this docket was refused with a 429 rate-limit
error; I did not retry, since the provisioned snapshot is dated today and the
conference is September 28, so the record I hold is current and the case is
undecided. The forecast rests on the provisioned snapshot, the petition text,
and the committed statpack.

## Where to discount me

The main uncertainty is whether the Court calls for a response at the long
conference; that is the one step that would move this petition off the
relist-0 path, and I have no case-specific signal about it beyond the
petition's own weaknesses. I also have not read the Wisconsin Court of Appeals
opinion itself, only the petition's account of it.
