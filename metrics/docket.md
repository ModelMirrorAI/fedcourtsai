# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2153052 case(s): 52516 resolved, 2100536 open, pulled through 2026-09-19. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 23135 case(s), 21549 resolved — matters read from the Court's own docket pages, the population the cert statistics below draw from. It also carries the interim application rows, which no cert statistic aggregates, so a cert denominator can sit below this count; 45741 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court, the population, and whether its counts are denial-reweighted. That reweighting matters. The historical walk ingests every decided petition except denials, which it samples on a committed frame, so a raw count would badly overstate the grant rate; a reweighted section counts each ingested petition for the number of petitions it stands in for. **Every section here is reweighted**, including the two overview cuts: nearly every labeled SCOTUS row is a sampled one, so a raw disposition split there would overstate the grant family several-fold, while a bulk-import circuit row carries weight 1 and is unchanged by it. So every count is a population **estimate** rather than rows on hand, and every denominator is written `est. n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**In the breakdown tables the estimate does not tell you** how many petitions were actually read to produce it. An `est. n=` of a few hundred rests on a raw row count several times smaller, and a breakdown row carries no raw view of its own — so treat a small reweighted cell as weaker evidence than its denominator suggests, and read a rate against the whole-population figures above it rather than on its own. The per-Term census is the exception and the place to calibrate that gap: it prints the observed `ingested (rows)` beside the reweighted estimate, so the ratio between them is legible for every Term.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — consolidated and prefixed spellings, and dash-variant numbers the Term cut folds and this one does not — land here. A display annotation is not among them: both parses strip it. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are denial-reweighted estimates._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 615273 | 46145 | 569128 | denied 91.0%, granted 5.2%, dismissed 2.0%, gvr 1.3%, other 0.5%, withdrawn 0.0% (est. n=46145) |
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
| (none) | 126777 | 267 | 126510 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (est. n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (est. n=13) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (est. n=12) |
| 2010s | 108561 | 18017 | 90544 | denied 95.5%, dismissed 1.9%, gvr 1.4%, granted 1.2% (est. n=18017) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (est. n=1) |
| 2020s | 47095 | 27832 | 19263 | denied 89.0%, granted 7.8%, dismissed 2.0%, gvr 1.2%, withdrawn 0.0% (est. n=27832) |
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
| denied | 41573 | 41573 | 0 | denied 100.0% (est. n=41573) |
| (open) | 1571 | 0 | 1571 | — |
| dismissed | 895 | 895 | 0 | dismissed 100.0% (est. n=895) |
| granted | 655 | 655 | 0 | granted 100.0% (est. n=655) |
| gvr | 577 | 577 | 0 | gvr 100.0% (est. n=577) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 11678 | 11204 | 474 | denied 96.5%, dismissed 2.1%, gvr 0.8%, granted 0.5% (est. n=11204) |
| ca9 | 5666 | 5474 | 192 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.1% (est. n=5474) |
| ca5 | 5465 | 5281 | 184 | denied 94.7%, gvr 2.1%, granted 1.6%, dismissed 1.6% (est. n=5281) |
| ca11 | 3719 | 3613 | 106 | denied 94.5%, dismissed 1.9%, gvr 1.9%, granted 1.7% (est. n=3613) |
| ca4 | 3482 | 3370 | 112 | denied 95.3%, dismissed 2.2%, granted 1.3%, gvr 1.2% (est. n=3370) |
| ca6 | 3035 | 2924 | 111 | denied 95.6%, dismissed 1.5%, granted 1.5%, gvr 1.3% (est. n=2924) |
| ca8 | 2151 | 2088 | 63 | denied 95.4%, dismissed 2.0%, gvr 1.4%, granted 1.2% (est. n=2088) |
| ca2 | 2060 | 1973 | 87 | denied 92.4%, dismissed 2.7%, granted 2.6%, gvr 2.3% (est. n=1973) |
| ca3 | 1946 | 1896 | 50 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 0.9% (est. n=1896) |
| ca7 | 1624 | 1582 | 42 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1582) |
| ca10 | 1457 | 1402 | 55 | denied 93.9%, granted 2.5%, dismissed 2.2%, gvr 1.4% (est. n=1402) |
| cafc | 918 | 878 | 40 | denied 92.3%, dismissed 3.2%, granted 3.1%, gvr 1.5% (est. n=878) |
| ca1 | 908 | 885 | 23 | denied 95.4%, granted 2.5%, dismissed 1.6%, gvr 0.6% (est. n=885) |
| cadc | 645 | 613 | 32 | denied 88.9%, granted 5.5%, dismissed 3.3%, gvr 2.3% (est. n=613) |
| fla | 232 | 232 | 0 | denied 99.6%, gvr 0.4% (est. n=232) |
| texcrimapp | 61 | 61 | 0 | denied 98.4%, gvr 1.6% (est. n=61) |
| alacrimapp | 50 | 50 | 0 | denied 100.0% (est. n=50) |
| cal | 41 | 41 | 0 | denied 97.6%, dismissed 2.4% (est. n=41) |
| ariz | 30 | 30 | 0 | denied 100.0% (est. n=30) |
| nev | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| ohio | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| oklacrimapp | 11 | 11 | 0 | denied 90.9%, dismissed 9.1% (est. n=11) |
| ark | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| idaho | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| kan | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| _… 4 more bucket(s) in the JSON_ | | | | |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. Relists are read off the stored distribution count, which holds the `dist-v2` reading; a parse change moves which entries count as a relist, not the tier labels, so the parse travels with the numbers. The count is an upper bound on true relists under either reading — a reschedule before first consideration also adds a distribution entry._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 37366 | 35883 | 1483 | denied 96.9%, dismissed 2.3%, granted 0.4%, gvr 0.4% (est. n=35883) |
| 1 | 6280 | 6204 | 76 | denied 92.0%, granted 3.7%, gvr 3.6%, dismissed 0.7% (est. n=6204) |
| 3+ | 816 | 810 | 6 | denied 69.0%, granted 16.2%, gvr 13.7%, dismissed 1.1% (est. n=810) |
| 2 | 809 | 803 | 6 | denied 67.9%, granted 18.1%, gvr 13.2%, dismissed 0.9% (est. n=803) |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 45098 | 43537 | 1561 | denied 95.3%, dismissed 2.0%, granted 1.4%, gvr 1.3% (est. n=43537) |
| cvsg | 173 | 163 | 10 | denied 62.0%, granted 29.4%, gvr 5.5%, dismissed 3.1% (est. n=163) |

## Cert petitions by capital-case marking
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. The capital flag is latched from supremecourt.gov's own `bCapitalCase` payload field, OR-ed with the `*** CAPITAL CASE ***` annotation the same channel appends to the docket number — either alone under-reports, and no other channel serves either reading. So `last_live_polled` is the column's coverage sentinel: a row no live poll stamped buckets as `(unknown)` rather than as unmarked, and none appear here because this section is already scoped to the live slice, which is that stamp. Inside the slice the stamp records an attempted poll rather than an ingested payload, so `unmarked` means no channel that wrote the row read either signal — silence, not a denial. Read it as an upper bound: contamination runs one way, into `unmarked`, so it can only shrink the gap between these buckets, never widen it. The split is a marginal one — it describes what the two populations are, not what the marking adds over the cuts beside it._

| capital_case | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unmarked | 44955 | 43412 | 1543 | denied 95.2%, dismissed 2.1%, granted 1.4%, gvr 1.3% (est. n=43412) |
| capital | 316 | 288 | 28 | denied 86.8%, granted 9.0%, gvr 3.5%, dismissed 0.7% (est. n=288) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5666 | 5474 | 192 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.1% (est. n=5474) |
| ca5 | 5465 | 5281 | 184 | denied 94.7%, gvr 2.1%, granted 1.6%, dismissed 1.6% (est. n=5281) |
| ca11 | 3719 | 3613 | 106 | denied 94.5%, dismissed 1.9%, gvr 1.9%, granted 1.7% (est. n=3613) |
| ca4 | 3482 | 3370 | 112 | denied 95.3%, dismissed 2.2%, granted 1.3%, gvr 1.2% (est. n=3370) |
| ca6 | 3035 | 2924 | 111 | denied 95.6%, dismissed 1.5%, granted 1.5%, gvr 1.3% (est. n=2924) |
| ca8 | 2151 | 2088 | 63 | denied 95.4%, dismissed 2.0%, gvr 1.4%, granted 1.2% (est. n=2088) |
| ca2 | 2060 | 1973 | 87 | denied 92.4%, dismissed 2.7%, granted 2.6%, gvr 2.3% (est. n=1973) |
| ca3 | 1946 | 1896 | 50 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 0.9% (est. n=1896) |
| ca7 | 1624 | 1582 | 42 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1582) |
| ca10 | 1457 | 1402 | 55 | denied 93.9%, granted 2.5%, dismissed 2.2%, gvr 1.4% (est. n=1402) |
| (none) | 1411 | 1338 | 73 | denied 99.3%, dismissed 0.7% (est. n=1338) |
| cafc | 918 | 878 | 40 | denied 92.3%, dismissed 3.2%, granted 3.1%, gvr 1.5% (est. n=878) |
| ca1 | 908 | 885 | 23 | denied 95.4%, granted 2.5%, dismissed 1.6%, gvr 0.6% (est. n=885) |
| cadc | 645 | 613 | 32 | denied 88.9%, granted 5.5%, dismissed 3.3%, gvr 2.3% (est. n=613) |
| Supreme Court of Florida | 449 | 436 | 13 | denied 96.8%, dismissed 3.2% (est. n=436) |
| Court of Appeal of California, Second Appellate District | 304 | 288 | 16 | denied 93.4%, dismissed 3.8%, gvr 2.4%, granted 0.3% (est. n=288) |
| Court of Criminal Appeals of Texas | 270 | 261 | 9 | denied 96.2%, dismissed 1.9%, gvr 1.5%, granted 0.4% (est. n=261) |
| Supreme Court of California | 246 | 235 | 11 | denied 95.7%, dismissed 4.3% (est. n=235) |
| Court of Criminal Appeals of Oklahoma | 239 | 238 | 1 | denied 89.5%, gvr 7.6%, granted 1.7%, dismissed 1.3% (est. n=238) |
| Court of Appeals of Michigan | 238 | 233 | 5 | denied 98.7%, dismissed 1.3% (est. n=233) |
| fla | 232 | 232 | 0 | denied 99.6%, gvr 0.4% (est. n=232) |
| District Court of Appeal of Florida, Fourth District | 224 | 203 | 21 | denied 96.1%, dismissed 3.4%, granted 0.5% (est. n=203) |
| Appellate Court of Illinois, First District | 205 | 199 | 6 | denied 99.0%, dismissed 1.0% (est. n=199) |
| Supreme Court of Virginia | 197 | 184 | 13 | denied 97.3%, dismissed 1.6%, gvr 1.1% (est. n=184) |
| District Court of Appeal of Florida, First District | 193 | 192 | 1 | denied 97.4%, dismissed 2.6% (est. n=192) |
| _… 278 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 31316 | 30359 | 957 | denied 96.4%, dismissed 2.4%, gvr 0.9%, granted 0.3% (est. n=30359) |
| paid | 13955 | 13341 | 614 | denied 92.2%, granted 4.3%, gvr 2.3%, dismissed 1.2% (est. n=13341) |

## Cert petitions by question-presented topic (`qp-topic-v0`)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. QP-bearing rows only — 2047 of 20971 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows; the bucket counts are denial-reweighted, and no reweighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 18924 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 2's extract sized the second: it counted 8498 QP-bearing row(s) in the frame it cut from, of which the artifact held 2047 labeled (24.1%). Both counts are batch 2's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 1694 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 2's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 4.8x — row for row, how much likelier a reference row was to be included than a drawn one when batch 2 landed: 353 carried in with certainty against 1694 drawn from the 8145 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| criminal-law | 1260 | 1249 | 11 | denied 94.7%, granted 2.6%, gvr 2.6%, dismissed 0.2% (est. n=1249) |
| civil-procedure | 462 | 449 | 13 | denied 90.2%, granted 5.1%, dismissed 3.1%, gvr 1.6% (est. n=449) |
| constitutional-rights | 336 | 329 | 7 | denied 89.7%, dismissed 4.3%, granted 4.3%, gvr 1.8% (est. n=329) |
| habeas-and-postconviction | 331 | 330 | 1 | denied 94.2%, dismissed 3.3%, granted 1.8%, gvr 0.6% (est. n=330) |
| firearms | 164 | 163 | 1 | denied 81.0%, granted 13.5%, gvr 4.9%, dismissed 0.6% (est. n=163) |
| employment-and-antidiscrimination | 154 | 153 | 1 | denied 90.2%, granted 6.5%, dismissed 2.0%, gvr 1.3% (est. n=153) |
| unclassifiable | 140 | 137 | 3 | denied 93.4%, dismissed 5.8%, granted 0.7% (est. n=137) |
| business-and-financial-regulation | 132 | 130 | 2 | denied 79.2%, granted 10.8%, gvr 5.4%, dismissed 4.6% (est. n=130) |
| first-amendment | 100 | 96 | 4 | denied 81.2%, granted 12.5%, gvr 4.2%, dismissed 2.1% (est. n=96) |
| administrative-law-and-benefit-programs | 97 | 95 | 2 | denied 68.4%, granted 21.1%, gvr 9.5%, dismissed 1.1% (est. n=95) |
| sovereignty-and-foreign-relations | 56 | 55 | 1 | denied 72.7%, granted 21.8%, dismissed 3.6%, gvr 1.8% (est. n=55) |
| intellectual-property | 47 | 47 | 0 | denied 91.5%, granted 8.5% (est. n=47) |
| tax | 29 | 29 | 0 | denied 89.7%, granted 10.3% (est. n=29) |
| election-law | 28 | 26 | 2 | denied 84.6%, granted 11.5%, dismissed 3.8% (est. n=26) |
| environment-energy-and-property | 24 | 24 | 0 | denied 70.8%, granted 20.8%, gvr 8.3% (est. n=24) |
| immigration | 19 | 19 | 0 | denied 63.2%, granted 36.8% (est. n=19) |

_Accrued over 2 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-fable-5, whose primaries matched the `qp-topic-v0` reference rater on 323 of 353 reference case(s) (91.5%), against the 22.9% a constant labeler scores on the same entries — **agreement, not accuracy**: the reference raters were agent sessions too, so rater error and labeler error cannot be separated, and the reference frame is grant-enriched, so the figure certifies the grant stream only. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 0 reference entr(ies) went uncovered. 2047 of 2047 labeled case(s) joined a row in this section's population; a gap is expected across batches, which span corpus vintages, and a large one reads as labels produced against another vintage rather than as thin coverage._

_Per-label agreement is **unmeasured in v0** for `election-law`, `environment-energy-and-property`, `immigration`, `intellectual-property`, `tax` — fewer reference examples than the support floor, where one entry moves the ratio by tens of points. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets, ordered by rows rather than by the table's reweighted count — the raw view the reweighted `est. n=` above does not give: `criminal-law` 450 [81], `civil-procedure` 390 [55], `constitutional-rights` 264 [36], `habeas-and-postconviction` 142 [14], `employment-and-antidiscrimination` 127 [18], `business-and-financial-regulation` 114 [21], `firearms` 101 [35], `first-amendment` 100 [13], `administrative-law-and-benefit-programs` 97 [29], `unclassifiable` 77 [14], `intellectual-property` 47 [5], `sovereignty-and-foreign-relations` 47 [13], `tax` 29 [3], `election-law` 28 [5], `environment-energy-and-property` 24 [6], `immigration` 10 [5]. A bucket's `est. n=` is an estimate of the population its rows stand for, so it runs above the rows read; the reference share is not uniform across buckets, and the block holds every QP-bearing grant it could reach, so it inflates the grant-heavy topics most._

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a row can sit outside the serial census — a petition whose docket number carries no serial the stream parser can read (a consolidated, prefixed, or dash-variant spelling), ingested under its Term but belonging to no stream's census — so `ingested` can exceed `filings`. `ingested` and `grants observed` are raw counts of rows on hand; the grant rate is the denial-reweighted estimate, and its `est. n` is the reweighted resolved count it divides by — which is why it too can exceed `ingested`. The plain `n` beside the pace to grant is different: that one is a raw count of the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate and is not a rate at all; the raw grant count is comparable to the weighted denominator only because a grant is always kept at weight 1 while denials are sampled. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | est. grant rate (weighted) | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2026 | 1001 | 982 | 0.0% (est. n=6) | 0 | — | complete |
| 2025 | 4134 | 4134 | 2.6% (est. n=3539) | 92 | 154 (n=92) | complete |
| 2024 | 3858 | 1644 | 3.1% (est. n=3795) | 116 | 137 (n=116) | complete |
| 2023 | 4223 | 1742 | 3.3% (est. n=4154) | 138 | 152 (n=138) | complete |
| 2022 | 4159 | 1625 | 2.7% (est. n=4046) | 109 | 143 (n=109) | complete |
| 2021 | 4899 | 2035 | 3.1% (est. n=4879) | 152 | 159 (n=152) | complete |
| 2020 | 5306 | 2294 | 3.1% (est. n=5264) | 161 | 143 (n=161) | complete |
| 2019 | 5408 | 2009 | 2.9% (est. n=5357) | 155 | 146 (n=155) | complete |
| 2018 | 6440 | 2203 | 2.3% (est. n=6388) | 146 | 154 (n=146) | complete |
| 2017 | 6313 | 2303 | 2.6% (est. n=6272) | 163 | 167 (n=163) | complete |

_Replay/backtest cells (a `DECIDED_BEFORE` clock in `record/context.json`): this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding your clock, because later Terms post-date what you are allowed to know._

## Not yet included

- **The `granted` / `gvr` split is not comparable across Terms.** The `gvr` label is a forward convention: a resolution recorded before it existed keeps `granted`, and no post-hoc rule separates a merits GVR from a plenary grant without re-resolving the source. OT2023 and OT2024 were resolved into the corpus inside that window, so they carry **zero** GVRs against 30-59% of the grant family in every Term either side of them — ingestion history, not the Court changing behaviour. Read the grant family as one number — the JSON artifacts publish it per Term as `est_grant_family_rate` — because the split is safe within a Term and meaningless between them.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver latches only the vacatur-remand form (`gvr`); summary affirmance and dismissal for want of a substantial federal question are deliberate resolver misses that reach maintainer triage instead.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts; this corpus is docket-first and holds no per-justice vote record.
