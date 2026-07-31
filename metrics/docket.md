# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2151873 case(s): 40294 resolved, 2111579 open, pulled through 2026-07-28. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 9924 case(s), 9327 resolved — petitions read from the Court's own docket pages, the population behind every cert statistic below; 44740 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court, the population, and whether its counts are denial-reweighted. That reweighting matters. The historical walk ingests every decided petition except denials, which it samples on a committed frame, so a raw count would badly overstate the grant rate; a reweighted section counts each ingested petition for the number of petitions it stands in for. **Every section here is reweighted**, including the two overview cuts: nearly every labeled SCOTUS row is a sampled one, so a raw disposition split there would overstate the grant family several-fold, while a bulk-import circuit row carries weight 1 and is unchanged by it. So every count is a population **estimate** rather than rows on hand, and every denominator is written `est. n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**In the breakdown tables the estimate does not tell you** how many petitions were actually read to produce it. An `est. n=` of a few hundred rests on a raw row count several times smaller, and a breakdown row carries no raw view of its own — so treat a small reweighted cell as weaker evidence than its denominator suggests, and read a rate against the whole-population figures above it rather than on its own. The per-Term census is the exception and the place to calibrate that gap: it prints the observed `ingested (rows)` beside the reweighted estimate, so the ratio between them is legible for every Term.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — annotated ones such as a capital-case marker most visibly, but also consolidated and prefixed spellings — land here. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are denial-reweighted estimates._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 624237 | 44066 | 580171 | denied 94.5%, dismissed 2.1%, granted 1.7%, gvr 1.1%, other 0.5% (est. n=44066) |
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
| (none) | 126873 | 267 | 126606 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (est. n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (est. n=13) |
| 2010s | 112650 | 18037 | 94613 | denied 95.5%, dismissed 1.9%, gvr 1.4%, granted 1.2% (est. n=18037) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (est. n=12) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (est. n=1) |
| 2020s | 51874 | 25733 | 26141 | denied 94.9%, dismissed 2.1%, granted 2.0%, gvr 0.9% (est. n=25733) |
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
| denied | 41647 | 41647 | 0 | denied 100.0% (est. n=41647) |
| dismissed | 889 | 889 | 0 | dismissed 100.0% (est. n=889) |
| granted | 745 | 745 | 0 | granted 100.0% (est. n=745) |
| (open) | 597 | 0 | 597 | — |
| gvr | 489 | 489 | 0 | gvr 100.0% (est. n=489) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 11849 | 11667 | 182 | denied 96.6%, dismissed 2.1%, gvr 0.7%, granted 0.6% (est. n=11667) |
| ca9 | 5599 | 5525 | 74 | denied 94.9%, granted 2.3%, dismissed 1.9%, gvr 1.0% (est. n=5525) |
| ca5 | 5348 | 5290 | 58 | denied 94.7%, granted 2.0%, gvr 1.8%, dismissed 1.6% (est. n=5290) |
| ca11 | 3718 | 3673 | 45 | denied 94.6%, dismissed 1.9%, granted 1.8%, gvr 1.7% (est. n=3673) |
| ca4 | 3492 | 3444 | 48 | denied 95.4%, dismissed 2.1%, granted 1.5%, gvr 1.0% (est. n=3444) |
| ca6 | 2937 | 2899 | 38 | denied 95.6%, granted 1.7%, dismissed 1.6%, gvr 1.2% (est. n=2899) |
| ca8 | 2206 | 2182 | 24 | denied 95.6%, dismissed 1.9%, granted 1.6%, gvr 1.0% (est. n=2182) |
| ca2 | 2057 | 2029 | 28 | denied 92.7%, granted 2.8%, dismissed 2.5%, gvr 2.0% (est. n=2029) |
| ca3 | 1861 | 1837 | 24 | denied 94.6%, dismissed 2.8%, granted 1.9%, gvr 0.7% (est. n=1837) |
| ca7 | 1578 | 1559 | 19 | denied 95.0%, dismissed 2.4%, gvr 1.4%, granted 1.2% (est. n=1559) |
| ca10 | 1354 | 1333 | 21 | denied 93.7%, granted 2.9%, dismissed 2.3%, gvr 1.1% (est. n=1333) |
| cafc | 935 | 923 | 12 | denied 92.5%, granted 3.4%, dismissed 2.9%, gvr 1.2% (est. n=923) |
| ca1 | 847 | 839 | 8 | denied 95.1%, granted 2.7%, dismissed 1.7%, gvr 0.5% (est. n=839) |
| cadc | 586 | 570 | 16 | denied 88.4%, granted 6.8%, dismissed 3.5%, gvr 1.2% (est. n=570) |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 36076 | 35537 | 539 | denied 97.3%, dismissed 2.0%, granted 0.4%, gvr 0.3% (est. n=35537) |
| 1 | 6619 | 6572 | 47 | denied 90.4%, granted 4.1%, gvr 2.8%, dismissed 2.6% (est. n=6572) |
| 2 | 867 | 861 | 6 | denied 69.2%, granted 20.3%, gvr 9.5%, dismissed 0.9% (est. n=861) |
| 3+ | 805 | 800 | 5 | denied 68.2%, granted 18.2%, gvr 12.2%, dismissed 1.2% (est. n=800) |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 44193 | 43606 | 587 | denied 95.3%, dismissed 2.0%, granted 1.6%, gvr 1.1% (est. n=43606) |
| cvsg | 174 | 164 | 10 | denied 62.2%, granted 31.1%, gvr 4.3%, dismissed 2.4% (est. n=164) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5599 | 5525 | 74 | denied 94.9%, granted 2.3%, dismissed 1.9%, gvr 1.0% (est. n=5525) |
| ca5 | 5348 | 5290 | 58 | denied 94.7%, granted 2.0%, gvr 1.8%, dismissed 1.6% (est. n=5290) |
| ca11 | 3718 | 3673 | 45 | denied 94.6%, dismissed 1.9%, granted 1.8%, gvr 1.7% (est. n=3673) |
| ca4 | 3492 | 3444 | 48 | denied 95.4%, dismissed 2.1%, granted 1.5%, gvr 1.0% (est. n=3444) |
| ca6 | 2937 | 2899 | 38 | denied 95.6%, granted 1.7%, dismissed 1.6%, gvr 1.2% (est. n=2899) |
| ca8 | 2206 | 2182 | 24 | denied 95.6%, dismissed 1.9%, granted 1.6%, gvr 1.0% (est. n=2182) |
| ca2 | 2057 | 2029 | 28 | denied 92.7%, granted 2.8%, dismissed 2.5%, gvr 2.0% (est. n=2029) |
| ca3 | 1861 | 1837 | 24 | denied 94.6%, dismissed 2.8%, granted 1.9%, gvr 0.7% (est. n=1837) |
| ca7 | 1578 | 1559 | 19 | denied 95.0%, dismissed 2.4%, gvr 1.4%, granted 1.2% (est. n=1559) |
| (none) | 1395 | 1359 | 36 | denied 99.3%, dismissed 0.7% (est. n=1359) |
| ca10 | 1354 | 1333 | 21 | denied 93.7%, granted 2.9%, dismissed 2.3%, gvr 1.1% (est. n=1333) |
| cafc | 935 | 923 | 12 | denied 92.5%, granted 3.4%, dismissed 2.9%, gvr 1.2% (est. n=923) |
| ca1 | 847 | 839 | 8 | denied 95.1%, granted 2.7%, dismissed 1.7%, gvr 0.5% (est. n=839) |
| Supreme Court of Florida | 708 | 705 | 3 | denied 97.6%, dismissed 2.1%, granted 0.1%, gvr 0.1% (est. n=705) |
| cadc | 586 | 570 | 16 | denied 88.4%, granted 6.8%, dismissed 3.5%, gvr 1.2% (est. n=570) |
| Court of Criminal Appeals of Texas | 348 | 347 | 1 | denied 96.8%, dismissed 1.4%, gvr 1.4%, granted 0.3% (est. n=347) |
| Supreme Court of California | 307 | 302 | 5 | denied 96.0%, dismissed 3.6%, granted 0.3% (est. n=302) |
| Court of Appeal of California, Second Appellate District | 287 | 280 | 7 | denied 93.2%, dismissed 3.9%, gvr 2.1%, granted 0.7% (est. n=280) |
| Court of Appeals of Michigan | 226 | 226 | 0 | denied 98.7%, dismissed 1.3% (est. n=226) |
| Court of Criminal Appeals of Oklahoma | 219 | 219 | 0 | denied 88.1%, gvr 8.2%, dismissed 1.8%, granted 1.8% (est. n=219) |
| Appellate Court of Illinois, First District | 208 | 206 | 2 | denied 99.0%, dismissed 1.0% (est. n=206) |
| District Court of Appeal of Florida, Fourth District | 200 | 194 | 6 | denied 95.9%, dismissed 3.6%, granted 0.5% (est. n=194) |
| District Court of Appeal of Florida, First District | 183 | 183 | 0 | denied 96.7%, dismissed 2.7%, granted 0.5% (est. n=183) |
| Supreme Court of Virginia | 163 | 161 | 2 | denied 96.9%, dismissed 1.9%, gvr 1.2% (est. n=161) |
| Court of Appeal of California, Third Appellate District | 158 | 154 | 4 | denied 96.8%, dismissed 1.3%, gvr 1.3%, granted 0.6% (est. n=154) |
| _… 209 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 29405 | 29059 | 346 | denied 96.3%, dismissed 2.5%, gvr 0.9%, granted 0.3% (est. n=29059) |
| paid | 13375 | 13135 | 240 | denied 92.3%, granted 4.9%, gvr 1.6%, dismissed 1.1% (est. n=13135) |
| (none) | 1587 | 1576 | 11 | denied 96.6%, granted 1.7%, dismissed 0.9%, gvr 0.8% (est. n=1576) |

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a petition whose docket number carries an annotation the serial parser cannot read (a capital-case marker, say) is ingested under its Term but belongs to no stream's serial census, so `ingested` can exceed `filings`. Within a stream it never does. `ingested` and `grants observed` are raw counts of rows on hand; the grant rate is the denial-reweighted estimate, and its `est. n` is the reweighted resolved count it divides by — which is why it too can exceed `ingested`. The plain `n` beside the pace to grant is different: that one is a raw count of the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate and is not a rate at all; the raw grant count is comparable to the weighted denominator only because a grant is always kept at weight 1 while denials are sampled. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | est. grant rate (weighted) | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2025 | 4134 | 4156 | 2.6% (est. n=3658) | 94 | 154 (n=94) | complete |
| 2024 | 3858 | 548 | 3.0% (est. n=3788) | 115 | 138 (n=115) | complete |
| 2023 | 4223 | 608 | 3.3% (est. n=4109) | 137 | 152 (n=137) | complete |
| 2022 | 4159 | 596 | 2.7% (est. n=4052) | 109 | 143 (n=109) | complete |
| 2021 | 4899 | 706 | 3.0% (est. n=4918) | 147 | 163 (n=147) | complete |
| 2020 | 5306 | 780 | 3.1% (est. n=5208) | 163 | 144 (n=163) | complete |
| 2019 | 5408 | 774 | 3.0% (est. n=5355) | 160 | 140 (n=160) | complete |
| 2018 | 6440 | 878 | 2.3% (est. n=6422) | 145 | 154 (n=145) | complete |
| 2017 | 6313 | 878 | 2.6% (est. n=6260) | 164 | 166 (n=164) | complete |

_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding your clock, because later Terms post-date what you are allowed to know._

## Not yet included

- **What the petitions are about.** A distribution of the questions presented by subject matter needs a claim taxonomy to classify them against, and no such taxonomy is built. Inventing one for this artifact alone would publish a categorization nothing else in the project shares, and that no later work could reproduce.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver latches only the vacatur-remand form (`gvr`); summary affirmance and dismissal for want of a substantial federal question are deliberate resolver misses that reach maintainer triage instead.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts; this corpus is docket-first and holds no per-justice vote record.
