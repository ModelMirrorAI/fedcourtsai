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
The hand reading of scope the rules apply (section 4) is AI agents' too, as
are the hand labels of policy area and policy key. AI reviewer agents checked the statistics and the prose
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
grep -n "$(printf '\u2039')" docs/release-ot2026-interim-exec.md docs/release-ot2026-interim-exec-public-summary.md
```

returns anything. The command is written with an escape so that it does not
match itself.

**Two readings of scope, and which leads.** The headline applies scope rule
`exec-action-v3`: the caption rule, with a committed hand reading of scope
taking its place for every application the reading lists (section 4). In this
window the hand reading places every counted application, and the caption
rule only sets aside the ones the reading does not list. The reading is
committed in the tag, so anyone with corpus access can reproduce every
headline figure with one command. Part of it was settled with the column's
figures in view, so part of its closeness to the column is by construction,
and section 4 says where, cell by cell. The **caption rule alone**
(`exec-action-v2`), which applies no hand code, is quoted beside it for that
reason.

**Counts before rates.** Most cells hold a few dozen applications at most, and
no interval is reported. A cell under about fifteen decided applications is
quoted as its pair, not as a percentage.

## 1. What was read, and from where

**The command.** Every headline figure in sections 2 and 3 is printed by one
read-only command, run where the corpus can be read:

```bash
FEDCOURTS_CORPUS_BACKEND=ranged uv run fedcourts executive-success \
  --as-of filed --since 2017-01-20 --through 2026-10-12 > executive-success.json
```

The caption-rule figures in section 4 are the same command with
`--scope-rule exec-action-v2`, read from the same commit and blob. It prints an `ExecutiveSuccess` to stdout and
the human cut, with the corpus vintage, to stderr. Its reading rules are in
[metrics/README.md](../metrics/README.md), *What may be claimed from the
executive success cut*, and its options in [cli.md](cli.md).

**The rules.** Scope `exec-action-v3` (the hand reading over
`exec-action-v2`, which reads `party-v2` and `sg-office-v1`), controversy
grouping `controversy-v2`, hand-labeled policy keys `policy-key-v1`, and
policy areas `policy-area-v2`, with the `finer` reading of stored
dispositions.

**The window.** Applications filed 2017-01-20 through 2026-10-12, each
attributed to the administration in office on its filing date (`--as-of
filed`). A disposition dated after 2026-10-12 reads as pending, as the column's
cut-off requires.

**What this fill was read from.** Code at commit `21be424e0` (the release's
pull request branch: `staging` plus the hand reading), against the corpus blob
`main` pointed to at the time, sha256
`405d1a4b5714fd007699eb4edf9c93965c523312a9e9f514d644b646a87b59de`:
`corpus-info`'s newest pull **2026-11-09**, newest stored snapshot row
**2026-07-13**. The stored rows are older than the window's end, but every
stored denial and grant in the cut was re-read from its own live snapshot
(below), and none was unobservable.

**Coverage.** The blob holds every Term the window touches: the Court's
application records from OT2016 on are back-filled, and the earliest in-scope
application is 16A1190, filed 2017-06-01. So the three administrations are
read from one complete record, and the comparison across them is not bounded
by coverage.

**The population.** 1,912 applications filed in the window were read for
scope, after 10,962 extensions of time and 4 duplicate docket rows were left
out. 456 had no docketed date and were dated by their first proceeding entry;
8 of those are in scope. The hand reading lists 298 of the 1,912 and decides
their scope; the caption rule places the rest, and leaves none of them unknown.

**The reading.** The `finer` reading re-read 168 stored denials and grants
from their live snapshots and relabeled 21, with 0 unobservable and 0 decided
after the cut. Thirteen of the relabels are Biden challengers' applications
stored as granted that were "dismissed in light of the relief granted", the
OSHA companions of *NFIB v. Department of Labor* among them, which now read as
moot. Five stored grants and denials read as granted in part, the two OT2016
travel-ban stays (16A1190, 16A1191) among them, all wins for the government,
and three Trump II denials read as moot.

## 2. Executive success by application (the headline)

**State.** A government application granted, in whole or in part, and a
challenger's application denied are both the executive's win. The rate is wins
over substantively decided applications; withdrawn, moot and pending ones sit
beside it, as in the column. An application with no disposition stored counts
as pending; for the five filed before 2023 that is a gap in the stored record,
not a live application, and each stays outside its pair.

**Evidence.** `cells` in `executive-success.json`, also printed to stderr.

| | Column | This release |
|---|---|---|
| **Trump I**, applications | 39 (34 by the government) | 49 (39 by the government) |
| Trump I, government as applicant | **25 of 33** | **26 of 34** |
| Trump I, challengers' applications | | 9 of 9 |
| **Biden**, applications | 81 (18 by the government, 63 by challengers) | 83 (16 by the government, 67 by challengers) |
| Biden, government as applicant | **10 of 15** | **10 of 15** |
| Biden, challengers' applications | | 38 of 52 |
| **Trump II**, applications | 45 (42 by the government) | 50 (41 by the government) |
| Trump II, government as applicant | **27 of 33** | **26 of 32** |
| Trump II, challengers' applications | | 7 of 9 |

Beside each government pair:
- **Trump I:** 39 applications; 3 with no disposition stored (17A655,
  17A1379, 18A276), 2 withdrawn, 2 with an ask the parser could not read
  (counted like any other).
- **Biden:** 16 applications; 1 with no disposition stored (21A477), 1
  unreadable ask.
- **Trump II:** 41 applications; 2 with no disposition stored at the cut
  (26A416 and 26A476, filed 2026-09-28 and 2026-10-08), 4 withdrawn, 3
  dismissed or denied as moot, 4 unreadable asks.

Beside the challengers' Biden pair: 67 applications, 1 with no disposition
stored (20A150), 1 withdrawn, 13 moot (the relabels above), 9 unreadable asks.
An unreadable ask is one the parser could not read (`unknown_ask`), counted
like any other.

**Unknown scope.** Two Biden applications are unplaced (23A60 and 23A138,
which the hand reading codes unclear). They are in no cell above and are
listed in `review_rows`. Every in-scope application in the window has an
administration.

**Totals.** This release puts 182 applications in scope, against the column's
165.

**What this shows.** The government pair matches the column exactly for
Biden and comes within one application for each Trump administration, one
more for Trump I and one fewer for Trump II. The Biden match rests partly on
codes made with the column in view (section 4). The totals agree in ratio, not
membership: the column lists no applications, so which applications differ
cannot be checked against it, and the totals of applications differ more than
the pairs do (section 5).

## 3. By controversy, and by policy area

**Controversies.** Applications the record links (the same case below, one
order, one-day orders that read alike, or government captions naming the same
parties within 210 days) count once, and a controversy takes the executive's
result in its last substantively decided application, ordered by stored
decision date. Every grouped application has a live snapshot
(`controversy_unlinked` 0). The column groups
"related applications" but does not say how, or how it scores a controversy.

**Evidence.** `controversy_cells` (`controversy-v2`) and
`policy_controversy_cells` (`policy-key-v1`) in `executive-success.json`.

| | Column | Rule (`controversy-v2`) | With policy keys (`policy-key-v1`) |
|---|---|---|---|
| Trump I, every filer | 18 of 24 | 31 of 37 (42 controversies) | 23 of 27 (31 controversies) |
| Biden, every filer | 29 of 39 | 30 of 44 (47 controversies) | 30 of 44 |
| Biden, controversies challengers brought | 21 of 27 | 22 of 31 (33 controversies) | 22 of 31 |
| Trump II, every filer | 23 of 30 | 30 of 37 (44 controversies) | 30 of 37 |

The column counts 109 controversies, 93 of them determinate. The rule counts
133, 118 of them determinate. The policy keys are a committed hand grouping
made by one AI grouper, not blind to outcomes and with the column in view; they
join 11 Trump I controversies and none after it. A keyed pair that matches the
column is therefore not an independent replication of it. The Biden challenger
cell counts controversies challengers alone filed in; the column's
"challenger-initiated" may differ.

**Policy areas, government as applicant.** Areas are the committed hand labels
(`policy-area-v2`). Two in-scope applications carry no label
(`policy_unlabeled` 2, both challengers', so no government cell below moves).
Applications, then decided pairs, then how many of the cell's labels the
raters marked uncertain:

| Area | Column | This release | Uncertain |
|---|---|---|---|
| Trump I immigration | 12 filed, won 11 of 12 | 13 filed, won 11 of 12 | 2 of 13 |
| Trump I federal executions | 8 filed, 7 favorable | 10 filed, won 8 of 9 | 7 of 10 |
| Trump I foreign affairs | 4 filed | none | |
| Trump I elections and census | 4 filed | 4 filed, won 2 of 4 | 3 of 4 |
| Trump I health | won 1 of 2 | 4 filed, won 1 of 2 | 3 of 4 |
| Biden immigration | 4 filed, won 2 of 4 | 3 filed, won 1 of 3 | 0 of 3 |
| Biden education | 5 filed, won 0 of 3 | 5 filed, won 2 of 5 | 0 of 5 |
| Biden health | 5 filed, won 4 of 4 | 4 filed, won 3 of 3 | 1 of 4 |
| Biden firearms | 2 filed, won 2 of 2 | 2 filed, won 2 of 2 | 0 of 2 |
| Trump II immigration | 14 filed, won 11 of 12 | 12 filed, won 10 of 10 | 0 of 12 |
| Trump II personnel and removal | 10 filed | 11 filed, won 6 of 9 | 1 of 11 |
| Trump II education | won 2 of 2 | 2 filed, won 2 of 2 | 0 of 2 |
| Trump II health | won 1 of 1 | 2 filed, won 1 of 1 | 1 of 2 |

Set against the column's pattern: Trump I immigration matches, and so do
Biden's firearms pair and Trump II's education and health pairs. Trump II
immigration is 10 of 10 against the column's 11 of 12, Biden's health pair is
3 of 3 against 4 of 4, Biden immigration is 1 of 3 against 2 of 4, and Biden
education, where the column has the government losing all 3 decided, is 2 of
5 here. Summed, the four Biden areas are 8 of 13 in both, so Biden's
government pair matches the column's in total and in these areas' sum while
the areas themselves do not, which is one more sign that a matching total can hold different
applications.

On the challengers' side under Biden, the column counts 25 health and 23
environment and energy applications of 63. This release counts 25 health and
28 environment and energy of 67. The raters marked a label uncertain on 45 of
the 182 in-scope applications, counted per government cell above and flagged
`policy_uncertain` on each review row.

## 4. The hand reading, and the caption rule without it

**State.** What the hand reading is, how much of it saw the column, and what
the caption rule gives without it.

**What was done.** Two AI raters, blind to each other but not to outcomes (the
docket entries carry the orders), coded the applications for scope, the
government's side and policy area, in three rounds:
- every federal-side application filed from OT2023 through 2026-10-12, which
  covers most of Trump II, with a seeded sample of 60 others (scope agreement
  263 of 292, κ 0.81);
- every OT2017–OT2022 application the rule reads as in scope or unknown, with
  the out-of-scope rows from any Term naming a federal agency or officer (side
  151 of 154, κ 0.97; scope 136 of 154, κ 0.79; policy area 146 of 154,
  κ 0.94);
- the 13 OT2016 applications filed from 2017-01-20 that the rule reads in
  scope or that name a federal party and ask for more than an extension (all
  sides and scope calls agreed).

The authoring session adjudicated their disagreements with the column's
figures in view, and on three points overrode both raters, two of them chosen
to match the column's universe:
1. a government application defending a policy is in scope, including through
   mandamus, and so is one defending the federal execution schedule;
2. a request to file over the word or page limit is out;
3. "dismissed in light of the relief granted" is moot.

The caption rule carries the second point and the reading carries the third,
so what the hand reading adds is mostly scope.

**The committed reading.** `src/fedcourtsai/exec_action_hand.json` holds 298
applications, 182 in scope, 114 out and 2 unclear, each with the government's
side where it is in scope and the basis of its code: 216 where the raters
agreed, 29 the session adjudicated, 26 where it overrode both raters, and 27
requests to file over the limit, set out as procedural. The 29 adjudicated and
26 overridden codes were made with the column in view, and so was the
decision to set the 27 procedural requests out: 82 codes in all. Of the 182
applications in scope, 29 rest on such a code (9 adjudicated, 20 overridden)
and the other 153 on the raters' agreement. The raters' own codes and their
agreement figures above are kept with the project's files, not in the
repository; the reading names dockets and judgments only, and no docket text.

**Evidence.** The section 1 command, under each scope rule.

| | Column | This release (`exec-action-v3`) | Caption rule alone (`exec-action-v2`) |
|---|---|---|---|
| Trump I, government as applicant | 25 of 33 | 26 of 34 | 26 of 34 |
| Biden, government as applicant | 10 of 15 | 10 of 15 | 12 of 20 |
| Trump II, government as applicant | 27 of 33 | 26 of 32 | 27 of 33 |
| Trump I, controversies | 18 of 24 | 31 of 37 | 29 of 36 |
| Biden, controversies | 29 of 39 | 30 of 44 | 24 of 37 |
| Biden, controversies challengers brought | 21 of 27 | 22 of 31 | 14 of 19 |
| Trump II, controversies | 23 of 30 | 30 of 37 | 29 of 34 |
| Applications in scope (column: 165) | | 182 | 163 |
| Applications left unknown | | 2 | 48 (17 Trump I, 24 Biden, 7 Trump II) |

**Where the two differ.** They share 154 in-scope applications. The caption
rule alone puts 9 in scope that the hand reading leaves out, among them a
preemption suit, a bankruptcy trustee's objection and one person's removal
case. The hand reading puts 28 in scope that the caption rule leaves out or
unknown, every one a challenger's application: among them the CDC mask
mandate, the Air Force vaccine mandate, three OSHA applications and an EPA
power-plant application. Under Biden the caption rule's government pair
carries six applications the hand reading sets aside or reads as a
challenger's (two wins, three losses and one with no disposition stored),
which is the whole gap between 12 of 20 and 10 of 15. Four of the six rest on
codes made with the column in view (21A85, 21A272, 23A87 and 23A814, among
them a bankruptcy trustee's objection and a suit over a state law), and two
on the raters' agreement (22A230 and 24A407). With the four left to the
caption rule, the Biden pair would be 11 of 18. Under Trump II it runs the
other way: the caption rule alone matches the column exactly, and the hand
reading moves it one off by setting aside one government win, one person's
removal case (24A949), on an adjudicated code where the raters split.

**What the caption rule still misses.** The hand reading covers the
applications it lists, and every other application, including every one filed
after the window, falls to the caption rule. The patterns behind the
differences above, a government side the caption misreads, a suit over a
state law, a bankruptcy trustee's objection, and a challenger the rule's word
list does not name, are not rules of this release. `exec-action-v4`, which
this release does not apply and whose figures it does not quote, leaves the
first two unknown, sets the third out of scope, and adds one word to the list.

## 5. Deltas the release cannot close

- **No application list.** The column publishes totals only, so every match
  above is a match of totals. Membership cannot be verified, and the policy
  areas (section 3) suggest some members differ.
- **Totals of applications.** This release counts 49 Trump I applications
  against the column's 39, 83 Biden against 81, and 50 Trump II against 45;
  by the government, 39 against 34, 16 against 18 and 41 against 42.
- **Trump I foreign affairs.** The column counts 4 government applications;
  the hand labels place none there.
- **Biden education.** The column has 0 of 3 decided; this release has 2 of
  5. The column leaves two of its five undecided.
- **Controversy grouping.** Neither the column's grouping nor how it scores a
  controversy is stated, so the controversy pairs are comparisons of
  conventions as much as of records.
- **AI coders throughout.** The scope rule, the hand reading, the policy
  labels and the policy keys were all built or coded by AI agents. Rater error
  and rule error cannot be separated.

## 6. The `stats-reviewer` pass

**State.** That the figure set, with its denominators, was reviewed before
publication, and what the reviewer found. A blocker is fixed or rebutted in
writing.

**Pass run 2026-11-09** over both filled documents, with every figure checked
against the saved output of the section 1 command under both scope rules and
against the committed hand reading. Verdict: **changes needed**. No quoted
number was found wrong. Disposition:

1. *Blocker:* the caption-rule figures were read from an earlier blob than the
   headline. **Fixed:** re-run on the section 1 blob and commit; every field
   was identical, and section 1 says so.
2. *Blocker:* the Biden exact match rests partly on codes made with the column
   in view, and neither document said which. **Fixed:** section 4 names the
   four of six such codes and gives the pair without them (11 of 18), and the
   public page says the same.
3. *Recommended:* the count of column-in-view codes left out the procedural
   requests. **Fixed:** section 4 counts 82.
4. *Recommended:* the documents overstated the caption rule's role under
   `exec-action-v3`. **Fixed:** both say every counted application rests on a
   hand code, and section 4 splits the 182 by basis.
5. *Recommended:* say that the caption rule alone matches Trump II exactly.
   **Fixed,** in section 4 and on the public page.
6. *Recommended:* "decided after the cut" for 26A416 and 26A476 was not shown
   by the output. **Fixed:** "no disposition stored at the cut".
7. *Recommended:* the rater agreement figures had no stated source.
   **Fixed:** section 4 says they are kept with the project's files.
8. *Nits:* "unreadable ask" defined against `unknown_ask`, one name for the
   Biden challenger row, and the Biden areas' equal sum. **All fixed.**


## 7. The publishing tag

**State.** That the published figures correspond to an exact commit on `main`.

The documents and the hand reading reach `main` by promotion. The promotion
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
   Candidate commit: `8c154564e` (promotion 2026-11-09); blob it was checked against:
   `265e345d5851b56697ce330e5ecb9210bb43b35024e7ce8d794e0b7ce84e2c68`, newest pull 2026-11-09; result: identical.
2. **Tag.** Only once both documents' placeholder greps return nothing and the
   section 6 pass is resolved, since the `results/` namespace blocks update and
   deletion. The candidate cannot carry its own check, so the tag goes on the
   later promotion merge that carries the filled line above, once step 1's
   command prints the same cells there; that merge is the `<candidate-commit>`
   below:

   ```bash
   git tag -a results/ot2026-interim-exec -m "Executive-action emergency docket replication" <candidate-commit>
   git push origin results/ot2026-interim-exec
   ```

3. **The software record.** The tag is published as a GitHub Release, and
   Zenodo's GitHub integration archives the repository at that tag as a new
   version of the project's software record, cited by its concept DOI
   `10.5281/zenodo.22966596` beside the tag.
4. **No dataset record.** The release deposits no dataset: its figures come
   from the access-gated corpus through the command in section 1, and its hand
   reading is committed in the code the tag archives. `data_doi` stays null in the manifest.
