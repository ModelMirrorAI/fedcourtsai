# Public summary: the OT2026 long conference

The reader-facing layer of Release 1. It sits beside
[release-ot2026-long-conference.md](release-ot2026-long-conference.md), which is
the audit record; this page is what goes on the fedcourts.ai Results page, the
first newsletter post and funder outreach.

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
grep -n "$(printf '‹')" docs/release-ot2026-public-summary.md
```

returns anything — written with an escape, as in the audit write-up, so that it
does not match itself.

---

## Draft

### ‹headline — one sentence, written last, in the form the rules below allow, and no stronger than the weakest caveat›

**What this is.** Before the Supreme Court's first conference of the term, three
frontier AI models each forecast whether the Court would take up a set of
pending cases. Every forecast was merged into a public ledger before the Court
met, so anyone can check that it came first. This is the first scored result.

### What was predicted, and when

- **Cases forecast:** 110 petitions pending at the 2026-09-28 conference, plus
  10 where the Court had asked for the Solicitor General's views — the cohort
  registered before any outcome existed (section 5 of the audit write-up). Of
  those, ‹n resolved and scored, per arm, from section 5's graded side› had been
  decided and scored when this page was written.
- **Models:** ‹predictor ids and the resolved model each ran, from the export's
  predictions table›, each run the same way, under the same instructions and
  with the same case materials.
- **Last forecast in the ledger:** ‹the latest time a counted prediction
  merged into `main`, from the export›. **The Court acted:** ‹order list
  date(s)›.
- **Check it yourself:** every forecast is a file in the public repo. The proof
  of timing is the time GitHub recorded when the forecast's pull request merged
  into `main`, and the `prereg/proc-v8` tag that fixed the rules beforehand;
  a commit's own date is set by whoever made it and proves nothing.
  ‹one-line recipe: a link to an example forecast's merged pull request, beside
  the order list›.

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
when they were ranked; **elevated** petitions had been relisted once. Each band
has its own historical grant rate, and the skill column is measured against it.

| Model | Band | Petitions scored | Right calls | "Always deny" on the same petitions | Lift | Skill vs. history |
| --- | --- | --- | --- | --- | --- | --- |
| ‹model› | elevated | ‹n› | ‹accuracy› | ‹always-deny accuracy› | ‹points› | ‹skill› |
| ‹model› | baseline | ‹n› | ‹accuracy› | ‹always-deny accuracy› | ‹points› | ‹skill› |
| ‹…one row per model per band, from section 3 of the audit write-up› | | | | | | |

‹per band: how many of its petitions carry a scored forecast from all three
models, and,
over the petitions carrying a historical rate, how many the Court granted
against how many that rate expected — from section 3›

Petitions the Court relisted or held are not scored yet, and relisted petitions
are granted more often than others, so the petitions scored so far lean toward
denials. That raises what "always deny" scores and lowers each band's realized
grant share below its historical rate, which moves the skill column too.

A **right call** is a forecast whose named outcome matched the Court's action
exactly. So a "grant" call on a petition the Court sent back for
reconsideration (a GVR) counts as a miss here, even though sent-back petitions
count as grants in the probability scores and the calls below. **Skill vs.
history** compares each model's probabilities with the band's historical grant
rate: above 0 means the forecasts beat that rate, and a model that just
repeated the rate would score 0.

‹one or two plain sentences on what the table shows, each figure with its `n`›

Bands with only one or two petitions (‹list, e.g. high, federal and state on
distribution›) are left out of the table because a single case cannot measure
anything; each such petition appears in the calls below whatever its outcome.

**Where the Court had asked for the Solicitor General's views.** These
petitions are scored on their own and never mixed into the table above. They
are read per band like the rest, so a row is one band:

| Model | Band | Petitions scored | Right calls | "Always deny" on the same petitions | Lift | Skill vs. history |
| --- | --- | --- | --- | --- | --- | --- |
| ‹model› | ‹band› | ‹n› | ‹accuracy› | ‹always-deny accuracy› | ‹points› | ‹skill› |

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

| Case | Arm | Court's action | ‹model A› | ‹model B› | ‹model C› |
| --- | --- | --- | --- | --- | --- |
| ‹caption, linked to its ledger event› | ‹distribution or SG views› | ‹G, GIP, GVR or SR› | ‹p› | ‹p› | ‹p› |

A petition sent back only because the case became moot is listed with its
action and marked "not scored": that kind of order says nothing about whether
the Court would have taken the case.

**The highest grant forecasts among denied petitions:** each model's three
highest grant forecasts among the distribution-arm petitions the Court denied,
merged into one list, with every petition tied at a model's third place
included. A 30% forecast is expected to be denied most of the time, so these
are not errors on their own; they are shown so that a model's confident misses
are as visible as its hits.

| Case | ‹model A› | ‹model B› | ‹model C› |
| --- | --- | --- | --- |
| ‹caption› | ‹p› | ‹p› | ‹p› |

**Petitions left out of the table above:** every petition in a band too small to
score, and every Solicitor General petition not already listed, with its action
and each model's forecast:

| Case | Arm and band | Court's action | ‹model A› | ‹model B› | ‹model C› |
| --- | --- | --- | --- | --- | --- |
| ‹caption› | ‹arm, band› | ‹action› | ‹p› | ‹p› | ‹p› |

**Still pending:** ‹n, from section 5's reconciliation› petitions were relisted
or held and are not scored yet. They will be scored when the Court acts.

‹optional: two or three sentences on one instructive call, drawn from the
model's committed reasoning file and quoted from it, not paraphrased into
something stronger›

### What this does and doesn't show

- **It's small.** In each band the Court granted only a handful of the scored
  petitions (the counts are under the table), set against what the band's
  historical rate over ‹the base-rate lookback window, from section 3› expected.
  One or two cases can reorder the models, so any ordering points to a possible
  difference rather than measuring one.
- **It's a selected set,** not the conference and not a random sample.
- **Deciding which cases to hear is the warm-up.** The project also forecasts
  how the Court decides the cases it takes — whether it leaves the lower court's
  judgment standing — and those forecasts resolve as decisions come out through
  June 2027. Forecasts of the vote split and of who writes are pre-registered
  but not yet scored.
- ‹any exclusion or coverage gap the audit write-up reports that changes how a
  reader should take the table, in one plain sentence each›

### Go deeper

- Full audit write-up, with every denominator: ‹link to the tagged doc›
- The ledger: ‹link to the Ledger page›
- The exact data behind this page: ‹the dataset record's reserved DOI link› ·
  the code that produced it: tag `results/ot2026-longconf`, in ‹the software
  record's concept DOI link›
- Follow along: ‹newsletter link›

---

## Rules for filling this in

- **Copy, don't compute.** Band figures come from the filled audit write-up;
  per-case probabilities, model names, merge times and set-aside marks come
  from the dataset export built at the tagged commit. If this page and either
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
- **One forecast per model per petition.** A per-case probability is the
  export's `scored` or `set_aside` row for that model and petition, not its
  `staged` one. Where two rows are scored for one model and petition, both are
  shown, labelled by run, rather than one being picked.
- **Timing comes from GitHub's merge record.** A merge time is the landing pull
  request's recorded merge time on `main`. The export's `ledger_committed_at`
  locates that commit, and is usable only in an export whose manifest reads
  `source_on_main_first_parent: true`; its `ledger_committed_by_github` flag is
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
  points to a possible difference rather than measuring one.
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
   that tagged commit.
