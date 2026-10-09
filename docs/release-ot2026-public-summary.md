# Public summary: the OT2026 long conference

The reader-facing layer of Release 1. It sits beside
[release-ot2026-long-conference.md](release-ot2026-long-conference.md), which is
the audit record; this page is what goes on the fedcourts.ai Results page and
into funder outreach.

**It is committed before the conference (2026-09-28)** so that what gets shown,
and how, is fixed before any outcome exists. It adds no numbers of its own:
every figure is copied from the filled audit write-up or from the release's
dataset export (the predictions table built from the tagged commit and deposited
on Zenodo as the release's dataset record), and a figure that is in neither does
not appear here.

Placeholders use the same single guillemets (U+2039 and U+203A) as the audit
write-up, and the same rule holds: **no placeholder is ever replaced by an
estimate**, and the page is not publishable while

```bash
grep -n "$(printf '\u2039')" docs/release-ot2026-public-summary.md
```

returns anything — written with an escape, as in the audit write-up, so that it
does not match itself.

---

## Draft

### Three AI models forecast which petitions the Supreme Court would take up at its 2026-09-28 conference; on the 97 scored petitions it has decided (91 of them pre-registered), the Court granted 3, two of them sent back for reconsideration, too few to measure a difference between the models.

**What this is.** Before the Supreme Court's first conference of the term, three
frontier AI models each forecast whether the Court would take up a set of
pending cases. Every forecast for that pre-registered set was merged into a
public ledger before the Court met, so anyone can check that it came first.
Six further petitions in the scores were first forecast only after the
conference had met, though before the Court acted on them (see *What this
does and doesn't show*). This is the first scored result.

### What was predicted, and when

- **Cases forecast:** 110 petitions distributed for the 2026-09-28 conference
  when the cohort was registered, plus 10 where the Court had asked for the
  Solicitor General's views — the cohort registered before any outcome existed
  (section 5 of the audit write-up). Of those, 91 of the 110 distributed
  petitions and none of the 10 Solicitor General petitions had been decided
  and scored when this page was written.
- **Models:** `claude-baseline` ran `claude-fable-5-1`, `codex-baseline` ran
  `gpt-6-astra` and `gemini-baseline` ran `gemini-3.1-pro-preview`, under the
  same instructions and with the same case materials, though not under
  identical conditions (see *The models did not run side by side* below).
- **Last forecast for the pre-registered set:** merged into `main` at
  2026-09-19 19:45:51 UTC
  ([pull request #1921](https://github.com/ModelMirrorAI/fedcourtsai/pull/1921)).
  **The Court acted:** 2026-10-01 (one grant) and 2026-10-05 (the order list
  carrying the other 90 decided pre-registered petitions, and the six
  late-forecast ones).
- **Check it yourself:** every forecast is a file in the public repo. The proof
  of timing is the time GitHub recorded when the forecast's pull request merged
  into `main`, and the `prereg/proc-v8` tag that fixed the rules beforehand;
  a commit's own date is set by whoever made it and proves nothing. For
  example, the three models' forecasts for No. 25-901 arrived in
  [pull request #1845](https://github.com/ModelMirrorAI/fedcourtsai/pull/1845),
  merged 2026-09-16 18:43:21 UTC; the Court acted on that petition in its
  2026-10-05 order list.

These were not all the petitions at the conference. The set was chosen by a
pre-registered ranking that favours petitions showing signs of the Court's
interest — being relisted, or a request for the Solicitor General's views — and
petitions brought by the federal government, so it leans toward cases more
likely to be granted. It is not a random sample, and the results below say
nothing about the conference as a whole.

### How it went

Every figure below is from forecasts made before their outcome existed.

Most petitions are denied, so a forecaster that always says "deny" is right
most of the time. Each row shows what "always deny" scored on exactly the same
petitions, and the lift is the difference, because beating that is the actual
test.

The rows are the ranking's bands. **Baseline** petitions had not been relisted
when they were ranked; **elevated** petitions had been relisted. Each band
has its own historical grant rate, and the skill column is measured against it.

| Model | Band | Petitions scored | Right calls | "Always deny" on the same petitions | Lift | Skill vs. history |
| --- | --- | --- | --- | --- | --- | --- |
| claude-baseline | elevated | 28 | 96.4% | 92.9% | +3.6 | +0.40 |
| codex-baseline | elevated | 28 | 92.9% | 92.9% | +0.0 | +0.13 |
| gemini-baseline | elevated | 28 | 85.7% | 92.9% | −7.1 | −0.60 |
| claude-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | +0.50 |
| codex-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | +0.12 |
| gemini-baseline | baseline | 67 | 100.0% | 100.0% | +0.0 | −0.33 |

Every petition in both bands carries a scored forecast from all three models:
28 of 28 elevated and 67 of 67 baseline. Among the elevated petitions the
Court granted 2, where the band's historical rate expected about 4.8; among
the baseline petitions it granted none, where about 3.4 were expected.

Petitions the Court relisted or held are not scored yet, and relisted petitions
are granted more often than others, so the petitions scored so far lean toward
denials. That raises what "always deny" scores and lowers each band's realized
grant share below its historical rate, which moves the skill column too, in
favour of lower forecasts.

A **right call** is a forecast whose named outcome matched the Court's action
exactly. So a "grant" call on a petition the Court sent back for
reconsideration (a GVR) counts as a miss here, even though sent-back petitions
count as grants in the probability scores and the calls below. In this set no
model made a plain "grant" call on either GVR: the right calls on them
(claude-baseline on both, codex-baseline on one) were forecasts that named a
GVR. **Skill vs.
history** compares each model's probabilities with the band's historical grant
rate: above 0 means the forecasts beat that rate, and a model that just
repeated the rate would score 0.

On the 67 baseline petitions the Court denied every one, so every model's
right calls equal "always deny" exactly, and only the skill column differs
there: +0.50, +0.12 and −0.33. With every baseline petition denied, that
column rewards forecasting low rather than telling grants from denials, and
because the likelier-granted relisted and held petitions are still pending,
the shortfall currently favours whichever model forecast lowest. On the 28 elevated petitions, one model's
right calls beat "always deny" by 3.6 points, one matched it and one fell 7.1
points below it — one or two petitions either way, out of 28.

Bands with only one petition (high and federal on distribution; the one state
petition is still pending) are left out of the table because a single case
cannot measure anything; each such petition appears in the calls below
whatever its outcome.

**Where the Court had asked for the Solicitor General's views.** These
petitions are scored on their own and never mixed into the table above. They
are read per band like the rest, so a row is one band. None of the 10 has
been acted on yet, so none is scored and this table has no rows; they are
counted under *Still pending* below.

### The calls

Every probability here is copied from the release's dataset export. Where a
forecast was set aside, its probability is not shown: the cell reads "set
aside" with the reason and a link to the ledger. A forecast is set aside when
its record claims it was made before an outcome that had in fact already
happened, or when every judge that graded it found it may have seen its own
outcome. A forecast that some but not all of its judges flagged in that way
keeps its probability, marked "flagged by one judge" (or two), and is scored
only through the judges that did not flag it. Where a model produced no
forecast for a petition, the cell reads "no forecast".

**Petitions the Court granted,** in any form — granted, granted in part, sent
back for reconsideration (GVR) or summarily reversed — with each model's
forecast probability of a grant:

Petitions are named by docket number, each linked to its ledger event.

| Case | Arm | Court's action | claude-baseline | codex-baseline | gemini-baseline |
| --- | --- | --- | --- | --- | --- |
| [No. 25-1131](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281619/events/evt-petition-disposition) | distribution | granted (2026-10-01, limited to Question 1) | 0.30 | 0.30 | 0.05 |
| [No. 25-901](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73280412/events/evt-petition-disposition) | distribution | GVR (2026-10-05) | 0.60 | 0.84 | 0.15 |
| [No. 25-918](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73280426/events/evt-petition-disposition) | distribution | GVR (2026-10-05) | 0.55 | 0.30 | 0.25 |

Both GVRs sent the case back for reconsideration in light of the same
intervening decision, *Louisiana v. Callais*. The one full grant, No. 25-1131,
drew no model's forecast above 0.30. No petition was sent back only because
the case became moot.

**The highest grant forecasts among denied petitions:** each model's three
highest grant forecasts among the distribution-arm petitions the Court denied,
merged into one list, with every petition tied at a model's third place
included. A 30% forecast is expected to be denied most of the time, so these
are not errors on their own; they are shown so that a model's confident misses
are as visible as its hits.

| Case | claude-baseline | codex-baseline | gemini-baseline |
| --- | --- | --- | --- |
| [No. 25-1105](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281388/events/evt-petition-disposition) | 0.14 | 0.22 | **0.55** |
| [No. 25-1141](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281628/events/evt-petition-disposition) | **0.30** | **0.38** | 0.15 |
| [No. 25-1191](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281673/events/evt-petition-disposition) | 0.08 | 0.05 | **0.40** |
| [No. 25-1197](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281703/events/evt-petition-disposition) | 0.18 | **0.36** | 0.11 |
| [No. 25-1208](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281694/events/evt-petition-disposition) | **0.25** | **0.36** | **0.82** |
| [No. 25-1210](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73281693/events/evt-petition-disposition) | **0.35** | 0.26 | 0.07 |
| [No. 25-1256](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73302615/events/evt-petition-disposition) | 0.21 | 0.14 | **0.40** |

A bold figure is one of that model's top three; gemini-baseline's third place
is a tie at 0.40, so it has four. All seven petitions are in the elevated
band and were denied on 2026-10-05. Two of gemini-baseline's, No. 25-1208 at
0.82 and No. 25-1105 at 0.55, were calls that the petition would be granted.

**Petitions left out of the table above:** every petition in a band too small to
score, and every Solicitor General petition not already listed, with its action
and each model's forecast:

| Case | Arm and band | Court's action | claude-baseline | codex-baseline | gemini-baseline |
| --- | --- | --- | --- | --- | --- |
| [No. 25-901](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73280412/events/evt-petition-disposition) | distribution, high | GVR (2026-10-05) | 0.60 | 0.84 | 0.15 |
| [No. 25-1219](https://github.com/ModelMirrorAI/fedcourtsai/tree/results/ot2026-longconf/data/cases/scotus/73248556/events/evt-petition-disposition) | distribution, federal | denied (2026-10-05) | 0.07 | 0.18 | 0.05 |

No. 25-901 is also in the granted list above. No Solicitor General petition has
been acted on, so none is listed here.

**Still pending:** 19 petitions on the distribution arm were relisted, held
or rescheduled, and 10 petitions where the Court had asked for the Solicitor
General's views have not yet been acted on; none of them is scored yet. They
will be scored when the Court acts. No petition in either group has been
acted on without its forecasts being graded, and every one of the 120 carries
a forecast from all three models.

### What this does and doesn't show

- **It's small.** In each band the Court granted only a handful of the scored
  petitions (the counts are under the table), set against what the band's
  historical rate over the eight Terms OT2017–OT2024 (a ten-Term lookback
  that the records available shorten to eight; OT2017–OT2025 for the seven
  petitions docketed in OT2026) expected.
  One or two cases can reorder the models, so any ordering points to a possible
  difference rather than measuring one.
- **It's a selected set,** not the conference and not a random sample.
- **Deciding which cases to hear is the warm-up.** The project also forecasts
  how the Court decides the cases it takes — whether it leaves the lower court's
  judgment standing — and those forecasts resolve as decisions come out through
  June 2027. Forecasts of the vote split and of who writes are pre-registered
  but not yet scored.
- **The models did not run side by side.** In every run the three models'
  forecasts started in a fixed order, so the last model ran later and after
  the others had used part of a shared research allowance. That may have
  helped or hurt it, and nothing here corrects for it (*Comparing the engines*
  in section 3 of the audit write-up). How often each model's research
  requests were turned away for lack of allowance cannot be measured from the
  logs, so no such figure is given.
- **Some petitions asked for something rarer than review.** Two of the
  petitions (Nos. 25-1252 and 25-1315, both baseline band, both denied) asked
  the Court to order a lower court to act (a writ of mandamus), which it
  almost never does; they are scored like the others, against the ordinary
  historical rate (section 5 of the audit write-up). Without them the
  baseline row covers 65 petitions, the right calls and "always deny" are
  unchanged at 100%, and the skill column reads +0.49, +0.12 and −0.37
  instead of +0.50, +0.12 and −0.33.
- **Some forecasts on the wider board came late.** Six petitions (Nos. 26-66,
  26-79, 26-80, 26-95, 26-121 and 26-183, all baseline band, all denied) were
  first forecast only on 2026-10-04, after their conference had met but the
  day before the order list that denied them; they are not among the cases
  this page lists, but they are in the scores (section 5 of the audit
  write-up). They are why the table counts 67 baseline petitions where the
  pre-registered set has 61 decided. Without them the baseline row covers 61
  petitions, the right calls and "always deny" are unchanged at 100%, and the
  skill column reads +0.56, +0.13 and −0.38 instead of +0.50, +0.12 and
  −0.33; the elevated row does not change.
- **The historical rates were worked out by the graders.** Each grader
  worked out and wrote down the band's historical rate it scored against;
  across all 873 gradings of the 291 scored forecasts none differs from the exact rate by more
  than 0.34% of that rate, and skill recomputed against the exact rates moves
  no row of the table by more than 0.001.
- **Two of the three grants were sent back, not taken up.** Both GVRs turned
  on one intervening decision, and the one petition the Court actually agreed
  to hear drew no model's forecast above 0.30. So the right calls on granted
  petitions here measure whether a model spotted a send-back, not whether it
  spotted a case the Court would hear (section 3 of the audit write-up).
- **Nothing was set aside.** No forecast on this page was excluded or flagged
  by any judge as possibly having seen its own outcome.

### Go deeper

- Full audit write-up, with every denominator:
  [docs/release-ot2026-long-conference.md at `results/ot2026-longconf`](https://github.com/ModelMirrorAI/fedcourtsai/blob/results/ot2026-longconf/docs/release-ot2026-long-conference.md)
- The ledger: [fedcourts.ai/ledger](https://fedcourts.ai/ledger/)
- The exact data behind this page: [10.5281/zenodo.23263986](https://doi.org/10.5281/zenodo.23263986) ·
  the code that produced it: tag `results/ot2026-longconf`, in
  [10.5281/zenodo.22966596](https://doi.org/10.5281/zenodo.22966596)

---

## Where the timing and links come from

The merge time, the example link and the order-list date have no figure in the
audit write-up to copy, so each comes from the fill export (section 8, step 2 of
the audit write-up), with the cohort's rows picked out by the cohort cut section
5 reads. Run the cut from the same checkout and corpus the fill export was built
from, with the content store wired, so its run ids are the export's and its
`conference_fallbacks` reads 0:

```bash
# 0. The cohort's counted forecasts: the cut's registered cert events
#    (distribution and Solicitor General views), each predictor's counted run.
uv run fedcourts conference-set --counted --registered-at 2026-09-15 > cut.json
jq '.conference_fallbacks' cut.json   # must be 0
jq -r '.events[] | select(.registered and .stage == "cert") | .case_id as $c
  | .event_id as $e | .cells[] | [$c, $e, .predictor_id, .run_id] | @tsv' \
  cut.json > cohort.tsv
# 1. The latest landing commit among them.
python3 -c 'import csv, sys
cohort = {tuple(line.rstrip("\n").split("\t")) for line in open(sys.argv[2])}
rows = [r for r in csv.DictReader(open(sys.argv[1]))
        if (r["case_id"], r["event_id"], r["predictor_id"], r["run_id"]) in cohort]
last = max(rows, key=lambda r: r["ledger_committed_at"])
print(len(rows), last["ledger_commit"], last["case_id"], last["event_id"])' \
  <fill-dir>/predictions.csv cohort.tsv
# 2. The pull request that landed it on main, with GitHub's merge time and link.
gh api repos/ModelMirrorAI/fedcourtsai/commits/<ledger_commit>/pulls \
  --jq '.[] | select(.base.ref == "main") | [.number, .merged_at, .html_url] | @tsv'
# 3. The order-list date(s): the export's resolution dates over the same rows.
python3 -c 'import collections, csv, sys
cohort = {tuple(line.rstrip("\n").split("\t")) for line in open(sys.argv[2])}
dates = {(r["case_id"], r["event_id"]): r["resolved_at"]
         for r in csv.DictReader(open(sys.argv[1]))
         if (r["case_id"], r["event_id"], r["predictor_id"], r["run_id"]) in cohort
         and r["resolved_at"]}
print(sorted(collections.Counter(dates.values()).items()))' \
  <fill-dir>/predictions.csv cohort.tsv
```

Step 1 prints how many rows it matched, which is three per cohort event with a
full grid, and reads `ledger_committed_at` only to pick the row; the time quoted
is step 2's `merged_at`, under the timing rule below. Step 3's dates are the
outcomes' own `resolved_at`, as the export carries them; the order list itself
is the Court's page for that date, which a reader checks by hand.

## Rules for filling this in

- **Copy, don't compute.** Band figures come from the filled audit write-up;
  per-case probabilities, model names, landing commits and set-aside marks come
  from the dataset export, and a merge time from GitHub's record of the pull
  request that commit landed. The page is filled from the export built at the
  metrics refresh, and the tag waits until the build at the tagged commit
  agrees with it on every row the page quotes (section 8 of the audit
  write-up). If this page and either
  source disagree, the source wins and this page is corrected; if the export
  and the audit write-up disagree, the audit write-up wins.
- **Band rows need a per-band producer.** A band row exists only where section 3
  publishes that band's figures from the board's own per-band cut. A pooled
  per-model row never stands in for band rows, and a band section 3 cannot fill
  leaves its rows out with a sentence saying so.
- **Petitions, not gradings.** "Petitions scored", "Right calls", "Always deny"
  and "Lift" are the per-petition figures section 3 publishes, each petition
  counted once. The board's grading-weighted figures (`accuracy_scored` and
  `skill_scored` count one grading per judge) stay in the audit write-up
  beside the panel depth.
- **The floor is realized, not historical.** "Always deny on the same
  petitions" is always-deny's accuracy over exactly the cells behind that row's
  right calls, scored by the same exact-match rule; the lift is the difference
  between the two. Both are copied from section 3, which takes them from the
  board's per-band cut. The registered historical floors are the skill column's
  anchor and appear only in the audit write-up.
- **Expected grants are per band and paired.** A band's realized grant count is
  quoted only over the petitions its expected count covers, both from section
  3; no cross-band expected total appears on this page.
- **Plain words, same claims.** Wording may be simpler than the audit
  write-up but never stronger. "Skill vs. history" is the population Brier
  skill score section 3 publishes, a ratio of sums over the row's cells; if it
  is null for a row, the cell reads "not measured", not 0.
- **Forward forecasts only.** Every figure is from the forward stratum at frozen
  process scope, the only population section 3 counts. In the export that is
  the `stratum` column, never `mode`: `mode` is the harness's claim, and a
  forecast stamped on the day its outcome landed claims `forward` while
  counting as retrospective.
- **One forecast per model per petition.** The forecast for a model and
  petition is the export's `scored` or `set_aside` row, not its
  `staged` one. Where two rows are scored for one model and petition, both are
  shown, labelled by run, rather than one being picked.
- **Timing comes from GitHub's merge record.** A merge time is the landing pull
  request's recorded merge time on `main`. The export's `ledger_commit` locates
  that commit, and it and `ledger_committed_at` are usable only in an export
  whose manifest reads `source_on_main_first_parent: true`; its `ledger_committed_by_github` flag is
  necessary but not sufficient, since a commit made from a Codespace carries
  the same committer. Comparisons with an outcome date are at day grain.
- **No pooled number.** No single number across bands, across the
  distribution and Solicitor General tables, or across models goes in the
  headline or anywhere else. That includes averaging the models'
  probabilities: the denied list is each model's own top three, merged.
- **The headline may rank only what every row agrees on.** It may order two
  models only if that order holds on both lift and skill in every row of both
  tables, with no row reading "not measured", and only in bands where every
  model's petitions scored equals the band's complete-grid count, which is what
  certifies the same petitions; otherwise it describes the result without
  ranking. An order it does state says, in the same sentence, that it
  points to a possible difference rather than measuring one, and links the
  write-up's run-order disclosure (*Comparing the engines* in
  [release-ot2026-long-conference.md](release-ot2026-long-conference.md)):
  the models did not run under identical conditions.
- **Sensitivity lines stay beside, never instead.** Where the audit write-up
  gives a figure a sensitivity line, the table shows the registered figure and
  the line appears only in the plain sentence that discloses it; no sensitivity
  figure is put in a table cell or the headline.
- **The post-hoc benchmark stays in the audit write-up.** The in-sample skill
  figure section 3 labels post-hoc is neither registered nor a sensitivity
  line, so it goes in no table cell, no headline and no model comparison; if
  the page mentions it at all, it is one plain sentence that names it as
  chosen after the outcomes were known and links section 3.
- **Every number keeps its `n`** in the table or the sentence carrying it.
- **Same page for everyone.** No outside party sees the filled page before it
  publishes.

## Pre-publication checklist

1. The audit write-up's placeholder grep returns nothing and its
   `stats-reviewer` pass is resolved.
2. This page's placeholder grep returns nothing.
3. Every figure here was checked against its source in the audit write-up or
   the export.
4. The headline was written last and checked against the ranking rule and the
   caveats.
5. The `results/ot2026-longconf` tag points at a commit carrying this filled
   page, the filled audit write-up, and the metrics refresh they both quote,
   the tag is published as a Release, and the dataset record's manifest names
   that tagged commit. Before the tag, that commit's build was checked against
   the export this page was filled from.
