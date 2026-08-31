# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2152649 case(s): 52409 resolved, 2100240 open, pulled through 2026-08-31. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 22727 case(s), 21442 resolved — matters read from the Court's own docket pages, the population the cert statistics below draw from. It also carries the interim application rows, which no cert statistic aggregates, so a cert denominator can sit below this count; 45425 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court, the population, and whether its counts are denial-reweighted. That reweighting matters. The historical walk ingests every decided petition except denials, which it samples on a committed frame, so a raw count would badly overstate the grant rate; a reweighted section counts each ingested petition for the number of petitions it stands in for. **Every section here is reweighted**, including the two overview cuts: nearly every labeled SCOTUS row is a sampled one, so a raw disposition split there would overstate the grant family several-fold, while a bulk-import circuit row carries weight 1 and is unchanged by it. So every count is a population **estimate** rather than rows on hand, and every denominator is written `est. n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**In the breakdown tables the estimate does not tell you** how many petitions were actually read to produce it. An `est. n=` of a few hundred rests on a raw row count several times smaller, and a breakdown row carries no raw view of its own — so treat a small reweighted cell as weaker evidence than its denominator suggests, and read a rate against the whole-population figures above it rather than on its own. The per-Term census is the exception and the place to calibrate that gap: it prints the observed `ingested (rows)` beside the reweighted estimate, so the ratio between them is legible for every Term.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — consolidated and prefixed spellings, and dash-variant numbers the Term cut folds and this one does not — land here. A display annotation is not among them: both parses strip it. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are denial-reweighted estimates._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 613817 | 44985 | 568832 | denied 91.0%, granted 5.1%, dismissed 2.1%, gvr 1.3%, other 0.5%, withdrawn 0.0% (est. n=44985) |
| ca9 | 247637 | 1463 | 246174 | other 94.5%, dismissed 2.6%, denied 2.0%, granted 0.8%, withdrawn 0.1% (est. n=1463) |
| ca5 | 203464 | 1502 | 201962 | other 91.0%, dismissed 4.0%, denied 3.5%, granted 1.5% (est. n=1502) |
| ca4 | 187218 | 15593 | 171625 | other 63.2%, dismissed 36.2%, denied 0.4%, granted 0.2%, granted-in-part 0.0% (est. n=15593) |
| ca6 | 142307 | 1320 | 140987 | other 93.9%, dismissed 3.4%, denied 1.4%, granted 1.3% (est. n=1320) |
| ca2 | 120926 | 2510 | 118416 | other 92.1%, dismissed 4.3%, denied 2.5%, granted 1.0%, granted-in-part 0.0%, withdrawn 0.0% (est. n=2510) |
| ca3 | 112971 | 1279 | 111692 | other 93.2%, dismissed 4.5%, denied 1.2%, granted 1.1% (est. n=1279) |
| ca8 | 103363 | 2378 | 100985 | other 89.9%, dismissed 4.4%, denied 2.9%, granted 2.7%, withdrawn 0.0% (est. n=2378) |
| ca11 | 95619 | 45 | 95574 | other 95.6%, denied 2.2%, granted 2.2% (est. n=45) |
| ca7 | 92080 | 895 | 91185 | other 91.4%, dismissed 5.0%, denied 2.1%, granted 1.5% (est. n=895) |
| ca10 | 81534 | 34 | 81500 | other 88.2%, denied 11.8% (est. n=34) |
| cafc | 72586 | 11 | 72575 | other 100.0% (est. n=11) |
| cadc | 57037 | 3042 | 53995 | other 94.3%, dismissed 2.2%, denied 2.0%, granted 1.5% (est. n=3042) |
| ca1 | 45337 | 599 | 44738 | other 86.3%, dismissed 8.0%, denied 5.0%, granted 0.7% (est. n=599) |

## SCOTUS cases by era
_Scope: scotus; includes the frozen bulk import; counts are denial-reweighted estimates._

| era | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 126778 | 267 | 126511 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (est. n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (est. n=13) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (est. n=12) |
| 2010s | 107940 | 17396 | 90544 | denied 95.4%, dismissed 2.0%, gvr 1.4%, granted 1.2% (est. n=17396) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (est. n=1) |
| 2020s | 46259 | 27293 | 18966 | denied 89.1%, granted 7.7%, dismissed 2.0%, gvr 1.2%, withdrawn 0.0% (est. n=27293) |
| 1970s | 36385 | 3 | 36382 | other 100.0% (est. n=3) |
| 1960s | 107 | 0 | 107 | — |
| 1910s | 20 | 0 | 20 | — |
| 1930s | 10 | 0 | 10 | — |
| 1940s | 8 | 0 | 8 | — |
| 1900s | 5 | 0 | 5 | — |
| 1880s | 4 | 0 | 4 | — |
| 1950s | 3 | 0 | 3 | — |
| 1850s | 1 | 0 | 1 | — |
| 1890s | 1 | 0 | 1 | — |

## Modern discretionary-cert petitions by disposition
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| disposition | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| denied | 40520 | 40520 | 0 | denied 100.0% (est. n=40520) |
| (open) | 1268 | 0 | 1268 | — |
| dismissed | 894 | 894 | 0 | dismissed 100.0% (est. n=894) |
| granted | 655 | 655 | 0 | granted 100.0% (est. n=655) |
| gvr | 577 | 577 | 0 | gvr 100.0% (est. n=577) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 11446 | 11078 | 368 | denied 96.5%, dismissed 2.2%, gvr 0.8%, granted 0.6% (est. n=11078) |
| ca9 | 5581 | 5429 | 152 | denied 94.8%, granted 2.2%, dismissed 1.9%, gvr 1.1% (est. n=5429) |
| ca5 | 5284 | 5137 | 147 | denied 94.5%, gvr 2.1%, granted 1.7%, dismissed 1.6% (est. n=5137) |
| ca11 | 3629 | 3540 | 89 | denied 94.4%, dismissed 1.9%, gvr 1.9%, granted 1.7% (est. n=3540) |
| ca4 | 3432 | 3334 | 98 | denied 95.2%, dismissed 2.2%, granted 1.3%, gvr 1.3% (est. n=3334) |
| ca6 | 2943 | 2852 | 91 | denied 95.5%, dismissed 1.6%, granted 1.6%, gvr 1.4% (est. n=2852) |
| ca8 | 2074 | 2025 | 49 | denied 95.2%, dismissed 2.0%, gvr 1.5%, granted 1.3% (est. n=2025) |
| ca2 | 2044 | 1973 | 71 | denied 92.4%, dismissed 2.7%, granted 2.6%, gvr 2.3% (est. n=1973) |
| ca3 | 1940 | 1896 | 44 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 0.9% (est. n=1896) |
| ca7 | 1607 | 1573 | 34 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1573) |
| ca10 | 1424 | 1375 | 49 | denied 93.8%, granted 2.5%, dismissed 2.3%, gvr 1.4% (est. n=1375) |
| cafc | 909 | 878 | 31 | denied 92.3%, dismissed 3.2%, granted 3.1%, gvr 1.5% (est. n=878) |
| ca1 | 903 | 885 | 18 | denied 95.4%, granted 2.5%, dismissed 1.6%, gvr 0.6% (est. n=885) |
| cadc | 640 | 613 | 27 | denied 88.9%, granted 5.5%, dismissed 3.3%, gvr 2.3% (est. n=613) |
| fla | 25 | 25 | 0 | denied 96.0%, gvr 4.0% (est. n=25) |
| texcrimapp | 7 | 7 | 0 | denied 85.7%, gvr 14.3% (est. n=7) |
| alacrimapp | 5 | 5 | 0 | denied 100.0% (est. n=5) |
| cal | 5 | 5 | 0 | denied 80.0%, dismissed 20.0% (est. n=5) |
| ariz | 3 | 3 | 0 | denied 100.0% (est. n=3) |
| nev | 2 | 2 | 0 | denied 100.0% (est. n=2) |
| ohio | 2 | 2 | 0 | denied 100.0% (est. n=2) |
| oklacrimapp | 2 | 2 | 0 | denied 50.0%, dismissed 50.0% (est. n=2) |
| ark | 1 | 1 | 0 | denied 100.0% (est. n=1) |
| ga | 1 | 1 | 0 | dismissed 100.0% (est. n=1) |
| idaho | 1 | 1 | 0 | denied 100.0% (est. n=1) |
| _… 4 more bucket(s) in the JSON_ | | | | |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. Relists are read off the stored distribution count, which holds the `dist-v2` reading; a parse change moves which entries count as a relist, not the tier labels, so the parse travels with the numbers. The count is an upper bound on true relists under either reading — a reschedule before first consideration also adds a distribution entry._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 36121 | 34928 | 1193 | denied 96.8%, dismissed 2.4%, granted 0.4%, gvr 0.4% (est. n=34928) |
| 1 | 6187 | 6123 | 64 | denied 91.9%, granted 3.7%, gvr 3.7%, dismissed 0.7% (est. n=6123) |
| 2 | 809 | 803 | 6 | denied 67.9%, granted 18.1%, gvr 13.2%, dismissed 0.9% (est. n=803) |
| 3+ | 797 | 792 | 5 | denied 68.3%, granted 16.5%, gvr 14.0%, dismissed 1.1% (est. n=792) |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 43741 | 42483 | 1258 | denied 95.1%, dismissed 2.1%, granted 1.4%, gvr 1.3% (est. n=42483) |
| cvsg | 173 | 163 | 10 | denied 62.0%, granted 29.4%, gvr 5.5%, dismissed 3.1% (est. n=163) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5581 | 5429 | 152 | denied 94.8%, granted 2.2%, dismissed 1.9%, gvr 1.1% (est. n=5429) |
| ca5 | 5284 | 5137 | 147 | denied 94.5%, gvr 2.1%, granted 1.7%, dismissed 1.6% (est. n=5137) |
| ca11 | 3629 | 3540 | 89 | denied 94.4%, dismissed 1.9%, gvr 1.9%, granted 1.7% (est. n=3540) |
| ca4 | 3432 | 3334 | 98 | denied 95.2%, dismissed 2.2%, granted 1.3%, gvr 1.3% (est. n=3334) |
| ca6 | 2943 | 2852 | 91 | denied 95.5%, dismissed 1.6%, granted 1.6%, gvr 1.4% (est. n=2852) |
| ca8 | 2074 | 2025 | 49 | denied 95.2%, dismissed 2.0%, gvr 1.5%, granted 1.3% (est. n=2025) |
| ca2 | 2044 | 1973 | 71 | denied 92.4%, dismissed 2.7%, granted 2.6%, gvr 2.3% (est. n=1973) |
| ca3 | 1940 | 1896 | 44 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 0.9% (est. n=1896) |
| ca7 | 1607 | 1573 | 34 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1573) |
| ca10 | 1424 | 1375 | 49 | denied 93.8%, granted 2.5%, dismissed 2.3%, gvr 1.4% (est. n=1375) |
| (none) | 1336 | 1275 | 61 | denied 99.2%, dismissed 0.8% (est. n=1275) |
| cafc | 909 | 878 | 31 | denied 92.3%, dismissed 3.2%, granted 3.1%, gvr 1.5% (est. n=878) |
| ca1 | 903 | 885 | 18 | denied 95.4%, granted 2.5%, dismissed 1.6%, gvr 0.6% (est. n=885) |
| cadc | 640 | 613 | 27 | denied 88.9%, granted 5.5%, dismissed 3.3%, gvr 2.3% (est. n=613) |
| Supreme Court of Florida | 446 | 436 | 10 | denied 96.8%, dismissed 3.2% (est. n=436) |
| Court of Appeal of California, Second Appellate District | 303 | 288 | 15 | denied 93.4%, dismissed 3.8%, gvr 2.4%, granted 0.3% (est. n=288) |
| Court of Criminal Appeals of Texas | 267 | 261 | 6 | denied 96.2%, dismissed 1.9%, gvr 1.5%, granted 0.4% (est. n=261) |
| Supreme Court of California | 243 | 235 | 8 | denied 95.7%, dismissed 4.3% (est. n=235) |
| Court of Criminal Appeals of Oklahoma | 238 | 238 | 0 | denied 89.5%, gvr 7.6%, granted 1.7%, dismissed 1.3% (est. n=238) |
| Court of Appeals of Michigan | 234 | 233 | 1 | denied 98.7%, dismissed 1.3% (est. n=233) |
| District Court of Appeal of Florida, Fourth District | 218 | 203 | 15 | denied 96.1%, dismissed 3.4%, granted 0.5% (est. n=203) |
| Appellate Court of Illinois, First District | 203 | 199 | 4 | denied 99.0%, dismissed 1.0% (est. n=199) |
| Supreme Court of Virginia | 195 | 184 | 11 | denied 97.3%, dismissed 1.6%, gvr 1.1% (est. n=184) |
| District Court of Appeal of Florida, First District | 192 | 192 | 0 | denied 97.4%, dismissed 2.6% (est. n=192) |
| Court of Appeals of Colorado | 169 | 165 | 4 | denied 97.6%, dismissed 1.2%, granted 1.2% (est. n=165) |
| _… 274 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 30072 | 29305 | 767 | denied 96.3%, dismissed 2.5%, gvr 0.9%, granted 0.3% (est. n=29305) |
| paid | 13842 | 13341 | 501 | denied 92.2%, granted 4.3%, gvr 2.3%, dismissed 1.2% (est. n=13341) |

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a row can sit outside the serial census — a petition whose docket number carries no serial the stream parser can read (a consolidated, prefixed, or dash-variant spelling), ingested under its Term but belonging to no stream's census — so `ingested` can exceed `filings`. `ingested` and `grants observed` are raw counts of rows on hand; the grant rate is the denial-reweighted estimate, and its `est. n` is the reweighted resolved count it divides by — which is why it too can exceed `ingested`. The plain `n` beside the pace to grant is different: that one is a raw count of the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate and is not a rate at all; the raw grant count is comparable to the weighted denominator only because a grant is always kept at weight 1 while denials are sampled. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | est. grant rate (weighted) | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2026 | 685 | 678 | 0.0% (est. n=5) | 0 | — | complete |
| 2025 | 4134 | 4134 | 2.6% (est. n=3539) | 92 | 154 (n=92) | complete |
| 2024 | 3858 | 1644 | 3.1% (est. n=3732) | 116 | 137 (n=116) | complete |
| 2023 | 4223 | 1742 | 3.4% (est. n=4082) | 138 | 152 (n=138) | complete |
| 2022 | 4159 | 1625 | 2.7% (est. n=4001) | 109 | 143 (n=109) | complete |
| 2021 | 4899 | 2035 | 3.2% (est. n=4744) | 152 | 159 (n=152) | complete |
| 2020 | 5306 | 2294 | 3.1% (est. n=5147) | 161 | 143 (n=161) | complete |
| 2019 | 5408 | 2009 | 3.0% (est. n=5213) | 155 | 146 (n=155) | complete |
| 2018 | 6440 | 2203 | 2.4% (est. n=6154) | 146 | 154 (n=146) | complete |
| 2017 | 6313 | 2303 | 2.7% (est. n=6029) | 163 | 167 (n=163) | complete |

_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding your clock, because later Terms post-date what you are allowed to know._

## Not yet included

- **The `granted` / `gvr` split is not comparable across Terms.** The `gvr` label is a forward convention: a resolution recorded before it existed keeps `granted`, and no post-hoc rule separates a merits GVR from a plenary grant without re-resolving the source. OT2023 and OT2024 were resolved into the corpus inside that window, so they carry **zero** GVRs against 30-59% of the grant family in every Term either side of them — ingestion history, not the Court changing behaviour. Read the grant family as one number — the JSON artifacts publish it per Term as `est_grant_family_rate` — because the split is safe within a Term and meaningless between them.
- **What the petitions are about.** The claim taxonomy for this cut exists — the `qp-topic-v0` vocabulary (`docs/qp-topic.md`) — but no labeler has run over the stored questions-presented texts, so the distribution is not yet computed. When it is, it carries that vocabulary's coverage caveat: QP presence is a document-fetch artifact, not a sample of the docket.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver latches only the vacatur-remand form (`gvr`); summary affirmance and dismissal for want of a substantial federal question are deliberate resolver misses that reach maintainer triage instead.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts; this corpus is docket-first and holds no per-justice vote record.
