# Public summary: the executive branch on the emergency docket

The reader-facing page for Release 2 (`ot2026-interim-exec`). fedcourts.ai
shows the *Draft* section below, read at the release's tag. Every figure in it
is copied from the audit write-up,
[release-ot2026-interim-exec.md](release-ot2026-interim-exec.md), and this page
yields to that document on any disagreement.

## Draft

### Rebuilt from the Supreme Court's own dockets, a published count of the government's emergency-application wins holds for Trump's second term, comes within one for his first, and diverges for Biden's.

**What this is.** On 2026-10-19 Adam Feldman's SCOTUSblog column, "Where the
Supreme Court favors Trump on the emergency docket – and where it doesn't",
counted how often the federal executive prevailed on emergency applications
about federal executive actions, from 2017-01-20 to 2026-10-12. The column
gives totals, not a list of cases. This release rebuilds those totals from the
Court's own dockets, using rules committed to a public repository, so anyone
with the code can see exactly which applications were counted and how.

Unlike Release 1, this release scores no AI forecast. It checks a published
analysis of what the Court has already done.

**Written by AI.** This page, like the audit write-up behind it, was written by
an AI agent (Claude, from Anthropic) under the project maintainer's direction,
and the agent copied each figure from the audit write-up. The rules that decide
which applications count were also written by AI agents, and AI raters labeled
the policy areas. AI reviewer agents checked the figures, and the maintainer
reviewed the page before it was published.

### How it compares

When the government asked the Court for emergency relief, how often did it get
it? Each pair is wins over applications the Court decided; withdrawn, moot and
undecided applications are left out, as the column leaves them out.

| | The column | This release's rules |
|---|---|---|
| Trump, first term | 25 of 33 | 26 of 34 |
| Biden | 10 of 15 | 12 of 20 |
| Trump, second term | 27 of 33 | 27 of 33 |

The rules could not place every application. They leave 17 applications from
Trump's first term, 24 from Biden's and 7 from Trump's second term unplaced,
where the docket does not make clear whether the case challenges a federal
action, so each pair above could move by more than its gap from the column.

The totals of applications differ more than the rates do. The rules count 163
applications in all against the column's 165: 45 under Trump's first term (39
by the government) against the column's 39 (34), 71 under Biden (22 by the
government) against 81 (18), and 47 under Trump's second term (42 by the
government) against 45 (42).

**By policy area**, the comparison is mixed, and most areas hold only a
handful of applications. Immigration matches the column closely: the
government won 11 of 12 decided in Trump's first term and 11 of 11 in his
second, against the column's 11 of 12 in each. Under Biden the rules give 2 of
2 firearms applications and 3 of 3 health applications, against the column's
2 of 2 and 4 of 4. They part on Biden's education applications, which the
column has the government losing all 3 decided and the rules have it winning 2
of 5, and on Biden's immigration applications, 1 of 4 against 2 of 4. The areas
are hand labels, and the raters marked some of them uncertain.

**Counting cases rather than applications.** One policy can produce several
applications, so the column also groups them into "controversies". The
column does not say how it groups them, and the rules here group them more
finely, so these figures differ more: for Trump's second term the rules count
29 of 34 against the column's 23 of 30.

### A second count, which saw the answer

Two AI raters also coded the applications by hand, and the AI agent that wrote
this release settled their disagreements. It did so with the column's figures
in view, and some of its calls were chosen to match the column's choices, so
its closeness to the column is partly by design and it is not an independent
check. It gives 26 of 34 for Trump's first term, 10 of 15 for Biden (the
column's figure exactly), and 26 of 32 for the second term. Its hand codes are
not published, so unlike the rule figures it cannot be re-run.

### What this does and doesn't show

- **It matches totals, not cases.** Because the column lists no cases, a
  matching total could still hide different cases on each side.
- **Biden is where the two counts part.** The hand reading sets aside or
  re-reads six of the government applications the rules count under Biden,
  among them a bankruptcy trustee's objection and a suit over a state law, and
  that closes the whole gap between 12 of 20 and 10 of 15.
- **It is not a measure of favoritism.** Which disputes reach the Court
  depends on who chooses to apply and on what the lower courts did. A count of
  wins does not adjust for that; a later release will.
- **The rules and labels are AI-built.** Their errors cannot be separated from
  disagreements with the column.

### Go deeper

- Full audit write-up, with every denominator:
  [docs/release-ot2026-interim-exec.md at `results/ot2026-interim-exec`](https://github.com/ModelMirrorAI/fedcourtsai/blob/results/ot2026-interim-exec/docs/release-ot2026-interim-exec.md)
- The column: [SCOTUSblog, 2026-10-19](https://www.scotusblog.com/2026/10/where-the-supreme-court-favors-trump-on-the-emergency-docket-and-where-it-doesnt/)
- The code that produced it: tag `results/ot2026-interim-exec`, in
  [10.5281/zenodo.22966596](https://doi.org/10.5281/zenodo.22966596). This
  release deposits no dataset: its figures are read from the Court's dockets
  as the project stores them, which only the project can access.

---

## Rules for filling this in

1. Every figure is copied from the audit write-up. The page adds none of its
   own and computes nothing.
2. The headline names the rule figures, never the adjudicated ones.
3. Wherever an adjudicated figure appears, the same paragraph says it was
   made with the column in view and cannot be re-run.
4. Pairs, not percentages: no cell here is large enough for a rate to carry
   more than its pair.

## Pre-publication checklist

1. The audit write-up's placeholder grep returns nothing and its
   `stats-reviewer` pass is resolved.
2. This page's placeholder grep returns nothing.
3. Every figure here was checked against its source in the audit write-up.
4. The column link opens the column itself, checked by hand.
5. The `results/ot2026-interim-exec` tag points at the candidate commit the
   audit write-up's section 7 checked, and the tag is published as a Release.
