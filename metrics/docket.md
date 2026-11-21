# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2154300 case(s): 89434 resolved, 2064866 open, pulled through 2026-11-20. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 59878 case(s), 58467 resolved — matters read from the Court's own docket pages, the population the cert statistics below draw from. It also carries the interim application rows, which no cert statistic aggregates, so a cert denominator can sit below this count; 46597 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court and the population. **Every count in the breakdown tables is a count of stored rows, each row counted once**: no row stands in for another, so a count describes the rows on hand and nothing beyond them. Every rate carries its denominator, written `n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**A rate is only as strong as its `n=`.** A small cell is weak evidence, so read its rate against the whole-population figures above it rather than on its own.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — consolidated and prefixed spellings, and dash-variant numbers the Term cut folds and this one does not — land here. A display annotation is not among them: both parses strip it. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are stored rows, each counted once._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 592190 | 58763 | 533427 | denied 77.4%, granted 19.3%, dismissed 1.7%, gvr 1.1%, other 0.4%, withdrawn 0.1% (n=58763) |
| ca9 | 247638 | 1463 | 246175 | other 94.5%, dismissed 2.6%, denied 2.0%, granted 0.8%, withdrawn 0.1% (n=1463) |
| ca5 | 203464 | 1502 | 201962 | other 91.0%, dismissed 4.0%, denied 3.5%, granted 1.5% (n=1502) |
| ca4 | 187218 | 15593 | 171625 | other 63.2%, dismissed 36.2%, denied 0.4%, granted 0.2%, granted-in-part 0.0% (n=15593) |
| ca6 | 142307 | 1320 | 140987 | other 93.9%, dismissed 3.4%, denied 1.4%, granted 1.3% (n=1320) |
| ca2 | 120926 | 2510 | 118416 | other 92.1%, dismissed 4.3%, denied 2.5%, granted 1.0%, granted-in-part 0.0%, withdrawn 0.0% (n=2510) |
| ca3 | 112972 | 1279 | 111693 | other 93.2%, dismissed 4.5%, denied 1.2%, granted 1.1% (n=1279) |
| ca8 | 103363 | 2378 | 100985 | other 89.9%, dismissed 4.4%, denied 2.9%, granted 2.7%, withdrawn 0.0% (n=2378) |
| ca11 | 95619 | 45 | 95574 | other 95.6%, denied 2.2%, granted 2.2% (n=45) |
| ca7 | 92080 | 895 | 91185 | other 91.4%, dismissed 5.0%, denied 2.1%, granted 1.5% (n=895) |
| ca10 | 81534 | 34 | 81500 | other 88.2%, denied 11.8% (n=34) |
| cafc | 72586 | 11 | 72575 | other 100.0% (n=11) |
| cadc | 57037 | 3042 | 53995 | other 94.3%, dismissed 2.2%, denied 2.0%, granted 1.5% (n=3042) |
| ca1 | 45337 | 599 | 44738 | other 86.3%, dismissed 8.0%, denied 5.0%, granted 0.7% (n=599) |
| cand | 10 | 0 | 10 | — |
| nysd | 7 | 0 | 7 | — |
| flnd | 5 | 0 | 5 | — |
| ded | 2 | 0 | 2 | — |
| flmd | 1 | 0 | 1 | — |
| jpml | 1 | 0 | 1 | — |
| paed | 1 | 0 | 1 | — |
| tnmd | 1 | 0 | 1 | — |
| txed | 1 | 0 | 1 | — |

## SCOTUS cases by era
_Scope: scotus; includes the frozen bulk import; counts are stored rows, each counted once._

| era | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 126118 | 267 | 125851 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (n=13) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (n=12) |
| 2010s | 97492 | 24091 | 73401 | denied 75.6%, granted 21.8%, dismissed 1.5%, gvr 1.0%, withdrawn 0.0% (n=24091) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (n=1) |
| 1970s | 36385 | 3 | 36382 | other 100.0% (n=3) |
| 2020s | 35740 | 34376 | 1364 | denied 79.3%, granted 17.8%, dismissed 1.7%, gvr 1.1%, withdrawn 0.1% (n=34376) |
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
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once._

| disposition | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| denied | 43037 | 43037 | 0 | denied 100.0% (n=43037) |
| (open) | 1365 | 0 | 1365 | — |
| dismissed | 924 | 924 | 0 | dismissed 100.0% (n=924) |
| granted | 642 | 642 | 0 | granted 100.0% (n=642) |
| gvr | 642 | 642 | 0 | gvr 100.0% (n=642) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 12722 | 12234 | 488 | denied 96.5%, dismissed 2.2%, gvr 0.8%, granted 0.6% (n=12234) |
| ca9 | 5805 | 5671 | 134 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.1% (n=5671) |
| ca5 | 5532 | 5394 | 138 | denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6% (n=5394) |
| ca11 | 3849 | 3769 | 80 | denied 94.7%, gvr 2.3%, dismissed 1.9%, granted 1.2% (n=3769) |
| ca4 | 3369 | 3287 | 82 | denied 94.9%, dismissed 2.3%, gvr 1.5%, granted 1.3% (n=3287) |
| ca6 | 3097 | 3031 | 66 | denied 95.8%, dismissed 1.5%, gvr 1.4%, granted 1.3% (n=3031) |
| ca2 | 2279 | 2208 | 71 | denied 92.9%, granted 2.5%, dismissed 2.4%, gvr 2.2% (n=2208) |
| ca8 | 2231 | 2182 | 49 | denied 95.4%, dismissed 2.0%, gvr 1.6%, granted 1.0% (n=2182) |
| ca3 | 1960 | 1906 | 54 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0% (n=1906) |
| ca7 | 1675 | 1623 | 52 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (n=1623) |
| ca10 | 1527 | 1492 | 35 | denied 94.3%, dismissed 2.1%, granted 1.9%, gvr 1.7% (n=1492) |
| cafc | 921 | 888 | 33 | denied 92.3%, dismissed 3.0%, granted 3.0%, gvr 1.6% (n=888) |
| ca1 | 910 | 889 | 21 | denied 95.3%, granted 2.6%, dismissed 1.6%, gvr 0.6% (n=889) |
| cadc | 710 | 671 | 39 | denied 89.0%, granted 6.0%, dismissed 3.0%, gvr 2.1% (n=671) |
| va | 3 | 0 | 3 | — |
| fladistctapp4 | 2 | 0 | 2 | — |
| nebctapp | 2 | 0 | 2 | — |
| alacivapp | 1 | 0 | 1 | — |
| cal | 1 | 0 | 1 | — |
| coloctapp | 1 | 0 | 1 | — |
| del | 1 | 0 | 1 | — |
| fla | 1 | 0 | 1 | — |
| fladistctapp1 | 1 | 0 | 1 | — |
| fladistctapp5 | 1 | 0 | 1 | — |
| gactapp | 1 | 0 | 1 | — |
| _… 8 more bucket(s) in the JSON_ | | | | |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once. Relists are read off the stored distribution count, which holds the `dist-v2` reading; a parse change moves which entries count as a relist, not the tier labels, so the parse travels with the numbers. The count is an upper bound on true relists under either reading — a reschedule before first consideration also adds a distribution entry._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 38554 | 37298 | 1256 | denied 96.9%, dismissed 2.3%, gvr 0.4%, granted 0.4% (n=37298) |
| 1 | 6412 | 6350 | 62 | denied 91.9%, gvr 3.9%, granted 3.5%, dismissed 0.6% (n=6350) |
| 3+ | 837 | 822 | 15 | denied 68.9%, granted 16.3%, gvr 13.9%, dismissed 1.0% (n=822) |
| 2 | 793 | 775 | 18 | denied 65.4%, granted 18.8%, gvr 14.7%, dismissed 1.0% (n=775) |
| (unknown) | 14 | 0 | 14 | — |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 46410 | 45079 | 1331 | denied 95.2%, dismissed 2.0%, gvr 1.4%, granted 1.3% (n=45079) |
| cvsg | 186 | 166 | 20 | denied 62.0%, granted 29.5%, gvr 6.0%, dismissed 2.4% (n=166) |
| (unknown) | 14 | 0 | 14 | — |

## Cert petitions by capital-case marking
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once. The capital flag is latched from supremecourt.gov's own `bCapitalCase` payload field, OR-ed with the `*** CAPITAL CASE ***` annotation the same channel appends to the docket number — either alone under-reports, and no other channel serves either reading. So `last_live_polled` is the column's coverage sentinel: a row no live poll stamped buckets as `(unknown)` rather than as unmarked, and none appear here because this section is already scoped to the live slice, which is that stamp. Inside the slice the stamp records an attempted poll rather than an ingested payload, so `unmarked` means no channel that wrote the row read either signal — silence, not a denial. Read it as an upper bound: contamination runs one way, into `unmarked`, so it can only shrink the gap between these buckets, never widen it. The split is a marginal one — it describes what the two populations are, not what the marking adds over the cuts beside it._

| capital_case | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unmarked | 45000 | 43665 | 1335 | denied 95.1%, dismissed 2.1%, gvr 1.4%, granted 1.4% (n=43665) |
| capital | 1610 | 1580 | 30 | denied 96.5%, granted 1.5%, gvr 1.1%, dismissed 0.9% (n=1580) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5805 | 5671 | 134 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.1% (n=5671) |
| ca5 | 5532 | 5394 | 138 | denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6% (n=5394) |
| ca11 | 3849 | 3769 | 80 | denied 94.7%, gvr 2.3%, dismissed 1.9%, granted 1.2% (n=3769) |
| ca4 | 3369 | 3287 | 82 | denied 94.9%, dismissed 2.3%, gvr 1.5%, granted 1.3% (n=3287) |
| ca6 | 3097 | 3031 | 66 | denied 95.8%, dismissed 1.5%, gvr 1.4%, granted 1.3% (n=3031) |
| ca2 | 2279 | 2208 | 71 | denied 92.9%, granted 2.5%, dismissed 2.4%, gvr 2.2% (n=2208) |
| ca8 | 2231 | 2182 | 49 | denied 95.4%, dismissed 2.0%, gvr 1.6%, granted 1.0% (n=2182) |
| ca3 | 1960 | 1906 | 54 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0% (n=1906) |
| ca7 | 1675 | 1623 | 52 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (n=1623) |
| (none) | 1635 | 1407 | 228 | denied 99.2%, dismissed 0.8% (n=1407) |
| ca10 | 1527 | 1492 | 35 | denied 94.3%, dismissed 2.1%, granted 1.9%, gvr 1.7% (n=1492) |
| cafc | 921 | 888 | 33 | denied 92.3%, dismissed 3.0%, granted 3.0%, gvr 1.6% (n=888) |
| ca1 | 910 | 889 | 21 | denied 95.3%, granted 2.6%, dismissed 1.6%, gvr 0.6% (n=889) |
| cadc | 710 | 671 | 39 | denied 89.0%, granted 6.0%, dismissed 3.0%, gvr 2.1% (n=671) |
| Supreme Court of Florida | 619 | 612 | 7 | denied 97.5%, dismissed 2.3%, gvr 0.2% (n=612) |
| Court of Criminal Appeals of Texas | 389 | 386 | 3 | denied 96.9%, dismissed 1.3%, gvr 1.3%, granted 0.5% (n=386) |
| Court of Appeal of California, Second Appellate District | 320 | 311 | 9 | denied 93.6%, dismissed 3.9%, gvr 2.3%, granted 0.3% (n=311) |
| Supreme Court of Virginia | 305 | 299 | 6 | denied 98.3%, dismissed 1.0%, gvr 0.7% (n=299) |
| Supreme Court of California | 297 | 295 | 2 | denied 96.3%, dismissed 3.7% (n=295) |
| Court of Criminal Appeals of Oklahoma | 246 | 244 | 2 | denied 88.9%, gvr 7.4%, dismissed 2.5%, granted 1.2% (n=244) |
| District Court of Appeal of Florida, Fourth District | 225 | 195 | 30 | denied 95.9%, dismissed 3.6%, granted 0.5% (n=195) |
| Appellate Court of Illinois, First District | 222 | 219 | 3 | denied 99.1%, dismissed 0.9% (n=219) |
| Court of Appeals of Michigan | 217 | 215 | 2 | denied 98.6%, dismissed 1.4% (n=215) |
| District of Columbia Court of Appeals | 184 | 183 | 1 | denied 96.7%, dismissed 2.2%, granted 0.5%, gvr 0.5% (n=183) |
| District Court of Appeal of Florida, First District | 154 | 149 | 5 | denied 96.6%, dismissed 3.4% (n=149) |
| _… 350 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 32323 | 31405 | 918 | denied 96.4%, dismissed 2.4%, gvr 1.0%, granted 0.1% (n=31405) |
| paid | 14275 | 13840 | 435 | denied 92.1%, granted 4.3%, gvr 2.3%, dismissed 1.3% (n=13840) |
| (none) | 12 | 0 | 12 | — |

## Cert petitions by question-presented topic (`qp-topic-v0`)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are stored rows, each counted once. QP-bearing rows only — 11894 of 46610 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows, and so are the bucket counts, each row counted once; no weighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 34716 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 14's extract sized the second: it counted 15930 QP-bearing row(s) in the frame it cut from, of which the artifact held 11898 labeled (74.7%). Both counts are batch 14's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 11541 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 14's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.3x — row for row, how much likelier a reference row was to be included than a drawn one when batch 14 landed: 353 carried in with certainty against 11545 drawn from the 15577 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| criminal-law | 3688 | 3675 | 13 | denied 95.1%, gvr 3.0%, granted 1.2%, dismissed 0.7% (n=3675) |
| civil-procedure | 2012 | 1993 | 19 | denied 94.2%, dismissed 2.6%, granted 2.4%, gvr 0.9% (n=1993) |
| constitutional-rights | 1369 | 1359 | 10 | denied 94.0%, dismissed 2.6%, granted 2.1%, gvr 1.2% (n=1359) |
| habeas-and-postconviction | 1098 | 1095 | 3 | denied 95.2%, dismissed 2.5%, granted 1.5%, gvr 0.9% (n=1095) |
| employment-and-antidiscrimination | 584 | 577 | 7 | denied 92.5%, granted 3.6%, dismissed 3.1%, gvr 0.7% (n=577) |
| business-and-financial-regulation | 572 | 556 | 16 | denied 85.6%, granted 6.5%, dismissed 4.3%, gvr 3.6% (n=556) |
| firearms | 510 | 506 | 4 | denied 91.5%, gvr 6.3%, granted 2.0%, dismissed 0.2% (n=506) |
| first-amendment | 486 | 473 | 13 | denied 92.2%, granted 5.3%, gvr 1.7%, dismissed 0.8% (n=473) |
| administrative-law-and-benefit-programs | 394 | 384 | 10 | denied 81.5%, granted 12.5%, gvr 4.9%, dismissed 1.0% (n=384) |
| unclassifiable | 385 | 382 | 3 | denied 90.8%, dismissed 8.9%, granted 0.3% (n=382) |
| sovereignty-and-foreign-relations | 246 | 241 | 5 | denied 82.2%, granted 10.8%, gvr 6.2%, dismissed 0.8% (n=241) |
| intellectual-property | 214 | 211 | 3 | denied 94.3%, granted 4.7%, gvr 0.9% (n=211) |
| tax | 106 | 106 | 0 | denied 95.3%, granted 4.7% (n=106) |
| environment-energy-and-property | 91 | 90 | 1 | denied 84.4%, granted 10.0%, gvr 5.6% (n=90) |
| election-law | 90 | 84 | 6 | denied 82.1%, granted 7.1%, dismissed 6.0%, gvr 4.8% (n=84) |
| immigration | 49 | 47 | 2 | denied 55.3%, granted 36.2%, gvr 6.4%, dismissed 2.1% (n=47) |

_Accrued over 14 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-opus-5-5, whose primaries matched the `qp-topic-v0` reference rater on 314 of 351 reference case(s) (89.5%), against the 23.1% a constant labeler scores on the same entries — **agreement, not accuracy**: the reference raters were agent sessions too, so rater error and labeler error cannot be separated, and the reference frame is grant-enriched, so the figure certifies the grant stream only. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 2 reference entr(ies) went uncovered. 11894 of 11898 labeled case(s) joined a row in this section's population; a gap is expected across batches, which span corpus vintages, and a large one reads as labels produced against another vintage rather than as thin coverage._

_Per-label agreement is **unmeasured in v0** for `election-law`, `environment-energy-and-property`, `immigration`, `intellectual-property`, `tax` — fewer reference examples than the support floor, where one entry moves the ratio by tens of points. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets: `criminal-law` 3688 [81], `civil-procedure` 2012 [55], `constitutional-rights` 1369 [36], `habeas-and-postconviction` 1098 [14], `employment-and-antidiscrimination` 584 [18], `business-and-financial-regulation` 572 [21], `firearms` 510 [35], `first-amendment` 486 [13], `administrative-law-and-benefit-programs` 394 [29], `unclassifiable` 385 [14], `sovereignty-and-foreign-relations` 246 [13], `intellectual-property` 214 [5], `tax` 106 [3], `environment-energy-and-property` 91 [6], `election-law` 90 [5], `immigration` 49 [5]. A bucket's `n=` above counts only its resolved rows; the reference share is not uniform across buckets, and the block holds every QP-bearing grant it could reach, so it inflates the grant-heavy topics most._

## Emergency applications by topic (`qp-topic-v1`)
_Scope: scotus, live/historical slice; counts are stored rows, each counted once. Labeled applications only — 2242 of 2251 in-frame live-slice applications labeled, 2200 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are rows too, each counted once. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 6's extract counted 2242 application(s) in the frame it cut from, of which the artifact held 2242 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 2001 drawn from the 2001 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 2001 were drawn._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unclassifiable | 977 | 970 | 7 | denied 83.7%, granted 14.8%, withdrawn 1.3%, dismissed 0.1% (n=970) |
| habeas-and-postconviction | 555 | 546 | 9 | denied 90.1%, granted 8.4%, withdrawn 1.3%, dismissed 0.2% (n=546) |
| criminal-law | 191 | 188 | 3 | denied 92.6%, granted 5.9%, withdrawn 1.6% (n=188) |
| civil-procedure | 134 | 132 | 2 | denied 89.4%, granted 9.8%, withdrawn 0.8% (n=132) |
| election-law | 91 | 89 | 2 | denied 71.9%, granted 27.0%, withdrawn 1.1% (n=89) |
| immigration | 90 | 88 | 2 | denied 76.1%, granted 20.5%, withdrawn 3.4% (n=88) |
| administrative-law-and-benefit-programs | 40 | 39 | 1 | granted 79.5%, denied 20.5% (n=39) |
| environment-energy-and-property | 35 | 35 | 0 | denied 71.4%, granted 28.6% (n=35) |
| first-amendment | 34 | 34 | 0 | denied 67.6%, granted 29.4%, withdrawn 2.9% (n=34) |
| employment-and-antidiscrimination | 33 | 32 | 1 | denied 90.6%, granted 9.4% (n=32) |
| business-and-financial-regulation | 23 | 22 | 1 | denied 72.7%, granted 27.3% (n=22) |
| constitutional-rights | 13 | 12 | 1 | denied 66.7%, withdrawn 25.0%, granted 8.3% (n=12) |
| sovereignty-and-foreign-relations | 13 | 13 | 0 | denied 76.9%, granted 23.1% (n=13) |
| firearms | 6 | 6 | 0 | denied 83.3%, granted 16.7% (n=6) |
| intellectual-property | 4 | 4 | 0 | denied 100.0% (n=4) |
| tax | 3 | 3 | 0 | denied 100.0% (n=3) |

_Accrued over 6 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-opus-5-5, whose primaries matched the application reference block's adjudicated labels on 214 of 241 reference case(s) (88.8%), against the 38.2% a constant labeler scores on the same entries — **agreement, not accuracy**, and **not yet quotable**: the block's labels are the majority of three blind raters that are instances of the labeler's own model, so their errors and the labeler's are correlated, and the held-out check behind them held no row with stored application text; an independent rater is owed before an application agreement figure is quoted. It is the publication gate's reading, printed so the gate can be audited. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 0 reference entr(ies) went uncovered. 2242 of 2242 labeled application(s) joined a row in this section's population._

_Per-label agreement is **unmeasured** for `administrative-law-and-benefit-programs`, `business-and-financial-regulation`, `constitutional-rights`, `employment-and-antidiscrimination`, `environment-energy-and-property`, `firearms`, `first-amendment`, `intellectual-property`, `tax` — fewer reference examples than the support floor. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets: `unclassifiable` 977 [92], `habeas-and-postconviction` 555 [43], `criminal-law` 191 [24], `civil-procedure` 134 [24], `election-law` 91 [13], `immigration` 90 [10], `administrative-law-and-benefit-programs` 40 [9], `environment-energy-and-property` 35 [4], `first-amendment` 34 [4], `employment-and-antidiscrimination` 33 [6], `business-and-financial-regulation` 23 [2], `constitutional-rights` 13 [7], `sovereignty-and-foreign-relations` 13 [0], `firearms` 6 [1], `intellectual-property` 4 [1], `tax` 3 [1]._

## Topic mix by stage
_The share of each stage's **labeled** cases under each primary topic, read off the topic cuts above: cert is every labeled cert-form petition, merits the labeled petitions granted plenary review, interim every labeled emergency application. Each column is a share of its own stage, never of the docket, and carries the scope string under the table. The columns are **not stages of one funnel**: cert is a share of a grant-enriched set, merits a share of the labeled grants, and interim another frame read from other inputs, so a difference between columns is not a grant propensity — the petition topic section's base-rate column is where that is read._

| topic | cert (n=11894) | merits (n=350) | interim (n=2242) | interim, subject-bearing only |
| --- | --: | --: | --: | --: |
| criminal-law | 31.0% (3688) | 12.6% (44) | 8.5% (191) | 15.1% |
| civil-procedure | 16.9% (2012) | 13.4% (47) | 6.0% (134) | 10.6% |
| constitutional-rights | 11.5% (1369) | 8.3% (29) | 0.6% (13) | 1.0% |
| habeas-and-postconviction | 9.2% (1098) | 4.6% (16) | 24.8% (555) | 43.9% |
| employment-and-antidiscrimination | 4.9% (584) | 6.0% (21) | 1.5% (33) | 2.6% |
| business-and-financial-regulation | 4.8% (572) | 10.3% (36) | 1.0% (23) | 1.8% |
| firearms | 4.3% (510) | 2.9% (10) | 0.3% (6) | 0.5% |
| first-amendment | 4.1% (486) | 7.1% (25) | 1.5% (34) | 2.7% |
| administrative-law-and-benefit-programs | 3.3% (394) | 13.7% (48) | 1.8% (40) | 3.2% |
| unclassifiable | 3.2% (385) | 0.3% (1) | 43.6% (977) | — |
| sovereignty-and-foreign-relations | 2.1% (246) | 7.4% (26) | 0.6% (13) | 1.0% |
| intellectual-property | 1.8% (214) | 2.9% (10) | 0.2% (4) | 0.3% |
| tax | 0.9% (106) | 1.4% (5) | 0.1% (3) | 0.2% |
| environment-energy-and-property | 0.8% (91) | 2.6% (9) | 1.6% (35) | 2.8% |
| election-law | 0.8% (90) | 1.7% (6) | 4.1% (91) | 7.2% |
| immigration | 0.4% (49) | 4.9% (17) | 4.0% (90) | 7.1% |

_Rows on hand in parentheses; each header's count is the stage's count as its section publishes it, a count of rows with each row counted once._

_The subject-bearing column divides the interim counts by the applications outside `unclassifiable`. It sits beside the full share, never in place of it: whether a row names a subject at all depends on whether the labeler read a stored application or only the docket, so this column is no closer to what the applications are about than the full one._

_cert: QP-bearing rows only — 11894 of 46610 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows, and so are the bucket counts, each row counted once; no weighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 34716 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 14's extract sized the second: it counted 15930 QP-bearing row(s) in the frame it cut from, of which the artifact held 11898 labeled (74.7%). Both counts are batch 14's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 11541 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 14's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.3x — row for row, how much likelier a reference row was to be included than a drawn one when batch 14 landed: 353 carried in with certainty against 11545 drawn from the 15577 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

_merits: Granted QP-bearing petitions only — 350 labeled grant(s) of the 642 plenary grant(s) in the cert scope; primaries only; not docket-representative. Plenary review here is the `granted` disposition, which takes in probable jurisdiction noted on a direct appeal and leaves out GVRs recorded as such (a few older merits GVRs still carry `granted`). The petition frame is still being labeled, so the missing grants are both those with no stored questions-presented text and those whose batch has not come up; reference-set grants are in every batch, so they are over-represented until it clears. Questions-presented coverage is zero before Term 2023 and uneven after, so this mix is weighted toward the Terms with stored texts and is not the merits docket's._

_interim: Labeled applications only — 2242 of 2251 in-frame live-slice applications labeled, 2200 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are rows too, each counted once. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 6's extract counted 2242 application(s) in the frame it cut from, of which the artifact held 2242 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 2001 drawn from the 2001 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 2001 were drawn._

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a row can sit outside the serial census — a petition whose docket number carries no serial the stream parser can read (a consolidated, prefixed, or dash-variant spelling), ingested under its Term but belonging to no stream's census — so `ingested` can exceed `filings`. `ingested` and `grants observed` are counts of rows on hand; the grant rate is over the resolved rows among them, each counted once, and its `n` is that resolved count. The `n` beside the pace to grant is a different count: the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate, because `ingested` includes rows not yet resolved. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | grant rate | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2026 | 1857 | 1857 | 1.2% (n=968) | 12 | 71 (n=12) | complete |
| 2025 | 4134 | 4134 | 2.8% (n=4021) | 111 | 154 (n=111) | complete |
| 2024 | 3858 | 3859 | 3.2% (n=3809) | 120 | 137 (n=119) | complete |
| 2023 | 4223 | 4223 | 3.3% (n=4166) | 139 | 152 (n=139) | complete |
| 2022 | 4159 | 4159 | 2.6% (n=4117) | 109 | 143 (n=109) | complete |
| 2021 | 4899 | 4900 | 3.1% (n=4861) | 151 | 163 (n=151) | complete |
| 2020 | 5306 | 5306 | 3.1% (n=5276) | 162 | 144 (n=162) | complete |
| 2019 | 5408 | 5411 | 3.0% (n=5369) | 159 | 146 (n=159) | complete |
| 2018 | 6440 | 6445 | 2.4% (n=6389) | 151 | 152 (n=151) | complete |
| 2017 | 6313 | 6316 | 2.7% (n=6269) | 170 | 164 (n=170) | complete |

_Replay/backtest cells: this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding `record/context.json`'s `decided_before`, an October Term, because later Terms post-date what you are allowed to know. These rows are keyed on the **docket-number** Term, so your own Term's row already contains your case._

## Not yet included

- **The `granted` / `gvr` split is not comparable across Terms.** The `gvr` label is a forward convention: a resolution recorded before it existed keeps `granted`, and no post-hoc rule separates a merits GVR from a plenary grant without re-resolving the source. OT2023 and OT2024 were resolved into the corpus inside that window, so they carry **zero** GVRs against 30-59% of the grant family in every Term either side of them — ingestion history, not the Court changing behaviour. Read the grant family as one number — the JSON artifacts publish it per Term as `est_grant_family_rate` — because the split is safe within a Term and meaningless between them.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver reads both sides: the vacatur-remand form (`gvr`) and probable jurisdiction noted or postponed to the merits (`granted`), and a summary affirmance (`denied`) or a dismissal for want of a substantial federal question, for want of jurisdiction or as moot (`dismissed`). A split order (affirmed in part and reversed in part, or dismissed in part and affirmed in part) is read on neither side and leaves the docket unresolved.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts this docket pack does not carry; the statpack's authorship section rolls up the per-opinion record instead.
