# Public summary: the executive branch on the emergency docket

The reader-facing page for Release 2 (`ot2026-interim-exec`). fedcourts.ai
shows the *Draft* section below, read at the release's tag. Every figure in it
is copied from the audit write-up,
[release-ot2026-interim-exec.md](release-ot2026-interim-exec.md), and this page
yields to that document on any disagreement.

## Draft

### Rebuilt from the Supreme Court's own dockets with fixed, public rules, a published count of how often the federal government won its emergency applications holds for President Trump's second term (27 of 33) and comes within one for his first (26 of 34 against 25 of 33), but not for President Biden's (12 of 20 against 10 of 15).

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
which copied each figure from the audit write-up. The rules that decide which
applications count were also written by AI agents, and AI raters labeled the
policy areas. AI reviewer agents checked the figures, and the maintainer
reviewed the page before it was published.

### How it compares

When the government asked the Court for emergency relief, how often did it get
it? Each pair is wins over applications the Court decided; withdrawn, moot and
still-pending applications are left out, as the column leaves them out.

| | The column | This release's rules |
|---|---|---|
| Trump, first term | 25 of 33 | 26 of 34 |
| Biden | 10 of 15 | 12 of 20 |
| Trump, second term | 27 of 33 | 27 of 33 |

The totals of applications differ more than the rates do. The rules count 45
applications under Trump's first term (39 by the government) against the
column's 39 (34), 71 under Biden (22 by the government) against 81 (18), and
47 under Trump's second term (42 by the government) against 45 (42).

**By policy area**, the pattern the column describes is there too.
Immigration is where the government did best under Trump: 11 of 12 decided in
the first term and 11 of 11 in the second, against the column's 11 of 12 in
each. Under Biden, the government won 2 of its 2 decided firearms applications
and 3 of its 3 decided health applications, as the column reports, though the
column counts four decided health applications. The areas are hand labels, and
most hold only a handful of applications.

**Counting cases rather than applications.** One policy can produce several
applications, so the column also groups them into "controversies". The
column does not say how it groups them, and the rules here group them more
finely, so these figures differ more: for Trump's second term the rules count
29 of 34 against the column's 23 of 30.

### A second count, which saw the answer

An AI reviewer also coded the applications by hand and settled the hard cases.
That review was done with the column's figures in view, and some of its calls
were chosen to match the column's choices, so its closeness to the column is
partly by design and it is not an independent check. It gives 26 of 34 for
Trump's first term, 10 of 15 for Biden (the column's figure exactly), and 26 of
32 for the second term. Its hand codes are not published, so unlike the rule
figures it cannot be re-run.

### What this does and doesn't show

- **It matches totals, not cases.** Because the column lists no cases, a
  matching total could still hide different cases on each side.
- **Biden is where the two counts part.** The rules count five more decided
  government applications under Biden than the column, among them a
  bankruptcy objection and a suit over a state law, which a hand reading sets
  aside.
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
  [10.5281/zenodo.22966596](https://doi.org/10.5281/zenodo.22966596)
- ‹the dataset record, if this release deposits one›

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
