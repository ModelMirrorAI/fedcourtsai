# Release write-up: the executive branch on the emergency docket

The audit write-up for the project's second results release, Release 2
(`ot2026-interim-exec`). It reproduces, from the Court's own dockets, the
analysis in Adam Feldman's SCOTUSblog column of 2026-10-19, ["Where the Supreme
Court favors Trump on the emergency docket – and where it doesn't"](https://www.scotusblog.com/2026/10/where-the-supreme-court-favors-trump-on-the-emergency-docket-and-where-it-doesnt/): how often
the federal executive prevailed on emergency applications involving general
federal executive actions, by administration, from 2017-01-20 through
2026-10-12. The column defines what is measured. None of its data is ingested,
and it lists no applications, so the comparison below is between totals.

**This release scores no forecast.** Release 1 graded forecasts committed before
the Court acted. This one measures the Court's record itself, with committed
rules, and sets it beside a published tally. Nothing a predict or evaluate cell
reads is derived from these figures.

**Written by AI.** This document was written by an AI agent: Claude
(Anthropic), working in Claude Code under the maintainer's direction. It ran
every command named below and copied each figure from that command's output.
The hand adjudication in section 4 is also an AI agent's, as are the hand
labels the rules read. AI reviewer agents checked the statistics and the prose
against the code and the data (section 6), and the maintainer reviewed it
before it was published.

**The public page.** [release-ot2026-interim-exec-public-summary.md](release-ot2026-interim-exec-public-summary.md)
is the reader-facing layer. It copies its figures from this document, adds none
of its own, and yields to this document on any disagreement.

**What comes later.** The column compares the executive's success with no
account of which cases reach the Court. A selection-adjusted reading, bounds on
the executive's advantage given which lower-court orders are brought up, is a
later release. The column's per-Justice support figures are not reproduced
here either.

## How to read this document

Each section says what the release states and gives the command or committed
artifact behind it. Every unfilled value is a placeholder wrapped in single
guillemets (U+2039 and U+203A). **No placeholder is ever replaced by an
estimate.** The draft is not publishable while

```bash
grep -n "$(printf '‹')" docs/release-ot2026-interim-exec.md docs/release-ot2026-interim-exec-public-summary.md
```

returns anything. The command is written with an escape so that it does not
match itself.

**Two kinds of figure, and which leads.** The **rule figures** come from the
committed rules alone and are the headline. Anyone with corpus access can
reproduce them from the tag with one command. The **adjudicated figures** (section
4) apply a hand adjudication on top. That adjudication was made with the
column's figures in view, so part of its closeness to the column is by
construction. They are quoted second, labeled as not blind, and never as the
headline. Their hand codes are not committed, so they cannot be reproduced from
the repository.

**Counts before rates.** Most cells hold a few dozen applications at most, and
no interval is reported. A cell under about fifteen decided applications is
quoted as its pair, not as a percentage.

## 1. What was read, and from where

**The command.** Every rule figure in sections 2 and 3 is printed by one
read-only command, run where the corpus can be read:

```bash
FEDCOURTS_CORPUS_BACKEND=ranged uv run fedcourts executive-success \
  --as-of filed --since 2017-01-20 --through 2026-10-12 > executive-success.json
```

It prints an `ExecutiveSuccess` to stdout and the human cut, with the corpus
vintage, to stderr. Its reading rules are in
[metrics/README.md](../metrics/README.md), *What may be claimed from the
executive success cut*, and its options in [cli.md](cli.md).

**The rules.** Scope `exec-action-v2` (over `party-v2` and `sg-office-v1`),
controversy grouping `controversy-v2`, hand-labeled policy keys
`policy-key-v1`, and policy areas `policy-area-v2`, with the `finer` reading
of stored dispositions.

**The window.** Applications filed 2017-01-20 through 2026-10-12, each
attributed to the administration in office on its filing date (`--as-of
filed`). A disposition dated after 2026-10-12 reads as pending, as the column's
cut-off requires.

**What this fill was read from.** Code at commit
`8f6df69d9` (the release's pull request branch, `staging` plus the reading fix
below), against the corpus blob `main` pointed to at the time, sha256
`97b2bc8b70d35a63396d88c0e36867a625bdbe9b131ab1ba964222ce94c46a75`:
`corpus-info`'s newest pull **2026-11-08**, newest stored snapshot row
**2026-07-13**. The stored rows are older than the window's end, but the
re-read below reads each application's own live snapshot, and none was
unobservable. The same command against the previous blob (sha256
`60b7c2e6…aa4dc`, pull 2026-11-08 07:22 UTC) printed identical cells.

**The population.** 1,912 applications filed in the window were read for
scope, after 10,962 extensions of time and 4 duplicate docket rows were left
out. 456 had no docketed date and were dated by their first proceeding entry;
9 of those are in scope. 19 requests to file over the word or page limit were
set out of scope as `procedural-request`.

**The reading.** The `finer` reading re-read 193 stored denials and grants
from their live snapshots and relabeled 24, with 0 unobservable and 0 decided
after the cut. Two of the relabels matter to the figures: 12 OSHA companion
applications stored as granted were "dismissed in light of the relief
granted" in *NFIB v. Department of Labor*, and now read as moot (10 of them in
scope), and the two OT2016 travel-ban stays (16A1190, 16A1191) read as granted
in part, still wins for the government.

## 2. Executive success by application (rule figures, the headline)

**State.** A government application granted, in whole or in part, and a
challenger's application denied are both the executive's win. The rate is wins
over substantively decided applications; withdrawn, moot and pending ones sit
beside it, as in the column.

**Evidence.** `cells` in `executive-success.json`, also printed to stderr.

| | Column | Rule figures |
|---|---|---|
| **Trump I**, applications | 39 (34 by the government) | 45 (39 by the government) |
| Trump I, government as applicant | **25 of 33** | **26 of 34** |
| Trump I, challengers' applications | | 6 of 6 |
| **Biden**, applications | 81 (18 by the government, 63 by challengers) | 71 (22 by the government, 49 by challengers) |
| Biden, government as applicant | **10 of 15** | **12 of 20** |
| Biden, challengers' applications | | 28 of 37 |
| **Trump II**, applications | 45 (42 by the government) | 47 (42 by the government) |
| Trump II, government as applicant | **27 of 33** | **27 of 33** |
| Trump II, challengers' applications | | 5 of 5 |

Beside each government pair:
- **Trump I:** 39 applications; 3 pending, 2 withdrawn, 2 with an ask the
  parser could not read (counted like any other).
- **Biden:** 22 applications; 2 pending, 2 unreadable asks.
- **Trump II:** 42 applications; 2 pending at the cut (filed 2026-09-28 and
  2026-10-08, decided after it), 4 withdrawn, 3 dismissed or denied as moot,
  4 unreadable asks.

Beside the challengers' Biden pair: 49 applications, 2 withdrawn, 10 moot (the
OSHA companions above), 3 unreadable asks.

**Unknown scope is not zero.** The rule leaves 17 Trump I, 24 Biden and 7
Trump II applications unplaced (a named individual with "et al." against an
officer, or a row only the counsel entries put on the government's side). They
are in no cell above and are listed in `review_rows`. Every in-scope
application in the window has an administration.

**What this shows.** The rule's government pair matches the column exactly for
Trump II and comes within one application for Trump I. For Biden it counts
five more decided government applications than the column, two of them wins.
The totals agree in ratio, not membership. The column lists no applications,
so which applications differ cannot be checked against it.

## 3. By controversy, and by policy area (rule figures)

**Controversies.** Applications the record links (the same case below, one
order, one-day orders that read alike, or government captions naming the same
parties within 210 days) count once, and a controversy takes the executive's
result in its last substantively decided application. The column groups
"related applications" but does not say how, or how it scores a controversy.

**Evidence.** `controversy_cells` (`controversy-v2`) and
`policy_controversy_cells` (`policy-key-v1`) in `executive-success.json`.

| | Column | Rule (`controversy-v2`) | With policy keys (`policy-key-v1`) |
|---|---|---|---|
| Trump I, every filer | 18 of 24 | 29 of 36 (40 controversies) | 23 of 27 (30 controversies) |
| Biden, every filer | 29 of 39 | 24 of 37 (41 controversies) | 24 of 37 |
| Biden, controversies challengers brought | 21 of 27 | 14 of 19 (21 controversies) | 14 of 19 |
| Trump II, every filer | 23 of 30 | 29 of 34 (41 controversies) | 29 of 34 |

The column counts 109 controversies, 93 of them determinate. The rule counts
122, 107 of them determinate. The policy keys are a committed hand grouping
made by one AI grouper, not blind to outcomes and with the column in view; they
join 10 Trump I controversies and none after it, since no key reaches a Trump
II application. A keyed pair that matches the column is therefore not an
independent replication of it. The Biden challenger cell counts controversies
challengers alone filed in; the column's "challenger-initiated" may differ.

**Policy areas, government as applicant.** Areas are the committed hand labels
(`policy-area-v2`; every in-scope application carries one, so no labeler area
is used and `policy_unlabeled` is 0). Applications, then decided pairs:

| Area | Column | Rule figures |
|---|---|---|
| Trump I immigration | 12 filed, won 11 of 12 | 13 filed, won 11 of 12 |
| Trump I federal executions | 8 filed, 7 favorable | 10 filed, won 8 of 9 |
| Trump I foreign affairs | 4 filed | none |
| Trump I elections and census | 4 filed | 4 filed, won 2 of 4 |
| Trump I health | won 1 of 2 | 4 filed, won 1 of 2 |
| Biden immigration | 4 filed, won 2 of 4 | 4 filed, won 1 of 4 |
| Biden education | 5 filed, won 0 of 3 | 5 filed, won 2 of 5 |
| Biden health | 5 filed, won 4 of 4 | 5 filed, won 3 of 3 |
| Biden firearms | 2 filed, won 2 of 2 | 2 filed, won 2 of 2 |
| Trump II immigration | 14 filed, won 11 of 12 | 13 filed, won 11 of 11 |
| Trump II personnel and removal | 10 filed | 11 filed, won 6 of 9 |
| Trump II education | won 2 of 2 | 2 filed, won 2 of 2 |
| Trump II health | won 1 of 1 | 2 filed, won 1 of 1 |

On the challengers' side under Biden, the column counts 25 health and 23
environment and energy applications of 63. The rule figures count 18 health
and 23 environment and energy of 49. The raters marked a label uncertain on 42
of the 163 in-scope applications, 7 of them among the 10 Trump I execution
applications and all 5 of the Trump II elections and census ones; each
per-area pair carries `policy_uncertain` on its review rows.

## 4. The hand adjudication (second, not blind)

**State.** What a hand reading of scope changes, and why it cannot stand as the
headline.

**What was done.** Two AI raters, blind to each other but not to outcomes (the
docket entries carry the orders), coded the applications for scope, the
government's side and policy area: every federal-side application of the
OT2023–OT2024 cut, every OT2016–OT2022 application the rule reads as in scope
or unknown, and the out-of-scope rows naming a federal agency or officer. The
authoring session adjudicated their disagreements with the column's figures in
view, and on three points overrode both raters, two of them chosen to match the
column's universe:
1. a government application defending a policy is in scope, including through
   mandamus, and so is one defending the federal execution schedule;
2. a request to file over the word or page limit is out;
3. "dismissed in light of the relief granted" is moot.

The rules now carry the second and third points, so the remaining difference
is mostly scope. Agreement between the raters on the OT2017–OT2022 round was
151 of 154 on side (κ 0.97), 136 of 154 on scope (κ 0.79) and 146 of 154 on
policy area (κ 0.94).

**Evidence.** A session script over the uncommitted hand codes, which are kept
with the project's files and not in the repository; no command in the tag
reproduces it. Its output was re-cut for this release so that the two Trump II
government applications decided after 2026-10-12 (26A416, 26A476) read as
pending, as the window requires.

| | Column | Rule figures | Adjudicated (not blind) |
|---|---|---|---|
| Trump I, government as applicant | 25 of 33 | 26 of 34 | 26 of 34 (39 filed of 49) |
| Biden, government as applicant | 10 of 15 | 12 of 20 | 10 of 15 (16 filed of 83) |
| Trump II, government as applicant | 27 of 33 | 27 of 33 | 26 of 32 (41 filed of 50) |
| Trump I, controversies | 18 of 24 | 29 of 36 | 23 of 27 |
| Biden, controversies | 29 of 39 | 24 of 37 | 31 of 45 |
| Biden, controversies challengers started | 21 of 27 | 14 of 19 | 23 of 32 |
| Trump II, controversies | 23 of 30 | 29 of 34 | 29 of 36 |

**Where the rule and the adjudication differ.** They share 154 in-scope
applications. The rule alone puts 9 in scope that the adjudication leaves out,
among them a preemption suit, a bankruptcy trustee's objection and one
person's removal case. The adjudication puts 28 in scope that the rule leaves
out or unknown, every one a challenger's application: among them the CDC mask
mandate, the Air Force vaccine mandate, three OSHA applications and an EPA
power-plant application. Under Biden the rule's government pair carries six
applications the adjudication sets aside or reads as a challenger's (two wins,
three losses and one pending), which is the whole gap between 12 of 20 and
10 of 15.

## 5. Deltas the release cannot close

- **No application list.** The column publishes totals only, so every match
  above is a match of totals. Membership cannot be verified.
- **Trump I foreign affairs.** The column counts 4 government applications;
  the hand labels place none there.
- **Biden education.** The column has 0 of 3 decided; the rule figures have 2
  of 5. The column leaves two of its five undecided.
- **Biden's challenger population.** The rule counts 49 challengers'
  applications against the column's 63, and the adjudication 67.
- **Controversy grouping.** Neither the column's grouping nor how it scores a
  controversy is stated, so the controversy pairs are comparisons of
  conventions as much as of records.
- **AI coders throughout.** The scope rule, the policy labels, the policy keys
  and the adjudication were all built or coded by AI agents. Rater error and
  rule error cannot be separated.

## 6. The `stats-reviewer` pass

**State.** That the figure set, with its denominators, was reviewed before
publication, and what the reviewer found. A blocker is fixed or rebutted in
writing.

**Pass run** ‹date of the pass over the filled documents›. Verdict:
‹verdict›. Disposition: ‹each finding and what was done›.

## 7. The publishing tag

**State.** That the published figures correspond to an exact commit on `main`.

The documents and the reading fix reach `main` by promotion. The promotion
merge that lands them is the *candidate commit*. Every step is the
maintainer's, in this order:

1. **Check the candidate.** From a checkout of the candidate, re-run the
   command in section 1 against the corpus `main` points to, and compare its
   stderr with the one this fill was read from:

   ```bash
   git switch --detach <candidate-commit>
   FEDCOURTS_CORPUS_BACKEND=ranged uv run fedcourts executive-success \
     --as-of filed --since 2017-01-20 --through 2026-10-12 \
     > candidate.json 2> candidate.txt
   jq '.corpus_sha256, .latest_pull, .reread_rows, .reread_changed' candidate.json
   ```

   Every cell line must match the figures in sections 2 and 3. The corpus is
   refreshed several times a day and the window is closed, so a newer blob
   should print the same cells; a cell that moved is a re-fill, with the new
   blob stated in section 1, and the candidate check again.
   Candidate commit: ‹candidate commit›; blob it was checked against:
   ‹sha256, newest pull›; result: ‹identical, or what moved›.
2. **Tag.** Only once both documents' placeholder greps return nothing and the
   section 6 pass is resolved, since the `results/` namespace blocks update and
   deletion:

   ```bash
   git tag -a results/ot2026-interim-exec -m "Executive-action emergency docket replication" <candidate-commit>
   git push origin results/ot2026-interim-exec
   ```

3. **The software record.** The tag is published as a GitHub Release, and
   Zenodo's GitHub integration archives the repository at that tag as a new
   version of the project's software record, cited by its concept DOI
   `10.5281/zenodo.22966596` beside the tag.
4. **The dataset record.** ‹whether this release deposits a dataset, and if so
   what it holds›.
