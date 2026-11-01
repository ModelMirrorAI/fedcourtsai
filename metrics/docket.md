# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2153861 case(s): 68159 resolved, 2085702 open, pulled through 2026-10-31. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 38375 case(s), 37192 resolved — matters read from the Court's own docket pages, the population the cert statistics below draw from. It also carries the interim application rows, which no cert statistic aggregates, so a cert denominator can sit below this count; 23602 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court, the population, and whether its counts are denial-reweighted. That reweighting matters. The historical walk ingests every decided petition except denials, which it samples on a committed frame, so a raw count would badly overstate the grant rate; a reweighted section counts each ingested petition for the number of petitions it stands in for. **Every section here is reweighted**, including the two overview cuts: nearly every labeled SCOTUS row is a sampled one, so a raw disposition split there would overstate the grant family several-fold, while a bulk-import circuit row carries weight 1 and is unchanged by it. So every count is a population **estimate** rather than rows on hand, and every denominator is written `est. n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**In the breakdown tables the estimate does not tell you** how many petitions were actually read to produce it. An `est. n=` of a few hundred rests on a raw row count several times smaller, and a breakdown row carries no raw view of its own — so treat a small reweighted cell as weaker evidence than its denominator suggests, and read a rate against the whole-population figures above it rather than on its own. The per-Term census is the exception and the place to calibrate that gap: it prints the observed `ingested (rows)` beside the reweighted estimate, so the ratio between them is legible for every Term.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — consolidated and prefixed spellings, and dash-variant numbers the Term cut folds and this one does not — land here. A display annotation is not among them: both parses strip it. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are denial-reweighted estimates._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 611168 | 56874 | 554294 | denied 78.6%, granted 18.2%, dismissed 1.7%, gvr 1.1%, other 0.4%, withdrawn 0.1% (est. n=56874) |
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
| (none) | 126247 | 267 | 125980 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (est. n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (est. n=13) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (est. n=12) |
| 2010s | 104895 | 22797 | 82098 | denied 78.6%, granted 18.8%, dismissed 1.5%, gvr 1.1%, withdrawn 0.0% (est. n=22797) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (est. n=1) |
| 2020s | 47186 | 33781 | 13405 | denied 79.3%, granted 17.9%, dismissed 1.7%, gvr 1.0%, withdrawn 0.1% (est. n=33781) |
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
| denied | 42577 | 42577 | 0 | denied 100.0% (est. n=42577) |
| (open) | 1133 | 0 | 1133 | — |
| dismissed | 919 | 919 | 0 | dismissed 100.0% (est. n=919) |
| granted | 671 | 671 | 0 | granted 100.0% (est. n=671) |
| gvr | 603 | 603 | 0 | gvr 100.0% (est. n=603) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 12087 | 11722 | 365 | denied 96.4%, dismissed 2.2%, gvr 0.8%, granted 0.6% (est. n=11722) |
| ca9 | 5602 | 5487 | 115 | denied 94.8%, granted 2.2%, dismissed 1.9%, gvr 1.1% (est. n=5487) |
| ca5 | 5599 | 5465 | 134 | denied 94.7%, gvr 2.1%, granted 1.7%, dismissed 1.6% (est. n=5465) |
| ca11 | 3791 | 3723 | 68 | denied 94.6%, gvr 2.0%, dismissed 1.9%, granted 1.5% (est. n=3723) |
| ca4 | 3496 | 3431 | 65 | denied 95.2%, dismissed 2.2%, gvr 1.3%, granted 1.3% (est. n=3431) |
| ca6 | 2987 | 2906 | 81 | denied 95.6%, dismissed 1.5%, granted 1.5%, gvr 1.4% (est. n=2906) |
| ca8 | 2194 | 2152 | 42 | denied 95.3%, dismissed 2.0%, gvr 1.5%, granted 1.2% (est. n=2152) |
| ca2 | 2173 | 2101 | 72 | denied 92.6%, granted 2.6%, dismissed 2.4%, gvr 2.3% (est. n=2101) |
| ca3 | 1980 | 1932 | 48 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0% (est. n=1932) |
| ca7 | 1655 | 1619 | 36 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1619) |
| ca10 | 1451 | 1416 | 35 | denied 94.1%, granted 2.3%, dismissed 2.2%, gvr 1.5% (est. n=1416) |
| cafc | 933 | 905 | 28 | denied 92.5%, dismissed 3.0%, granted 3.0%, gvr 1.5% (est. n=905) |
| ca1 | 903 | 883 | 20 | denied 95.2%, granted 2.6%, dismissed 1.6%, gvr 0.6% (est. n=883) |
| cadc | 668 | 644 | 24 | denied 88.7%, granted 6.1%, dismissed 3.1%, gvr 2.2% (est. n=644) |
| fla | 120 | 120 | 0 | denied 100.0% (est. n=120) |
| texcrimapp | 61 | 61 | 0 | denied 98.4%, gvr 1.6% (est. n=61) |
| alacrimapp | 50 | 50 | 0 | denied 100.0% (est. n=50) |
| cal | 31 | 31 | 0 | denied 96.8%, dismissed 3.2% (est. n=31) |
| ariz | 30 | 30 | 0 | denied 100.0% (est. n=30) |
| nev | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| ohio | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| oklacrimapp | 11 | 11 | 0 | denied 90.9%, dismissed 9.1% (est. n=11) |
| ark | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| idaho | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| neb | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| _… 2 more bucket(s) in the JSON_ | | | | |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. Relists are read off the stored distribution count, which holds the `dist-v2` reading; a parse change moves which entries count as a relist, not the tier labels, so the parse travels with the numbers. The count is an upper bound on true relists under either reading — a reschedule before first consideration also adds a distribution entry._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 37921 | 36866 | 1055 | denied 96.8%, dismissed 2.3%, granted 0.4%, gvr 0.4% (est. n=36866) |
| 1 | 6335 | 6288 | 47 | denied 91.9%, gvr 3.8%, granted 3.7%, dismissed 0.7% (est. n=6288) |
| 3+ | 834 | 825 | 9 | denied 69.2%, granted 16.4%, gvr 13.5%, dismissed 1.0% (est. n=825) |
| 2 | 804 | 791 | 13 | denied 66.4%, granted 19.1%, gvr 13.5%, dismissed 1.0% (est. n=791) |
| (unknown) | 9 | 0 | 9 | — |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 45714 | 44606 | 1108 | denied 95.2%, dismissed 2.1%, granted 1.4%, gvr 1.3% (est. n=44606) |
| cvsg | 180 | 164 | 16 | denied 62.8%, granted 29.3%, gvr 5.5%, dismissed 2.4% (est. n=164) |
| (unknown) | 9 | 0 | 9 | — |

## Cert petitions by capital-case marking
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. The capital flag is latched from supremecourt.gov's own `bCapitalCase` payload field, OR-ed with the `*** CAPITAL CASE ***` annotation the same channel appends to the docket number — either alone under-reports, and no other channel serves either reading. So `last_live_polled` is the column's coverage sentinel: a row no live poll stamped buckets as `(unknown)` rather than as unmarked, and none appear here because this section is already scoped to the live slice, which is that stamp. Inside the slice the stamp records an attempted poll rather than an ingested payload, so `unmarked` means no channel that wrote the row read either signal — silence, not a denial. Read it as an upper bound: contamination runs one way, into `unmarked`, so it can only shrink the gap between these buckets, never widen it. The split is a marginal one — it describes what the two populations are, not what the marking adds over the cuts beside it._

| capital_case | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unmarked | 45267 | 44162 | 1105 | denied 95.1%, dismissed 2.1%, granted 1.5%, gvr 1.3% (est. n=44162) |
| capital | 636 | 608 | 28 | denied 93.3%, granted 3.5%, gvr 2.1%, dismissed 1.2% (est. n=608) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5602 | 5487 | 115 | denied 94.8%, granted 2.2%, dismissed 1.9%, gvr 1.1% (est. n=5487) |
| ca5 | 5599 | 5465 | 134 | denied 94.7%, gvr 2.1%, granted 1.7%, dismissed 1.6% (est. n=5465) |
| ca11 | 3791 | 3723 | 68 | denied 94.6%, gvr 2.0%, dismissed 1.9%, granted 1.5% (est. n=3723) |
| ca4 | 3496 | 3431 | 65 | denied 95.2%, dismissed 2.2%, gvr 1.3%, granted 1.3% (est. n=3431) |
| ca6 | 2987 | 2906 | 81 | denied 95.6%, dismissed 1.5%, granted 1.5%, gvr 1.4% (est. n=2906) |
| ca8 | 2194 | 2152 | 42 | denied 95.3%, dismissed 2.0%, gvr 1.5%, granted 1.2% (est. n=2152) |
| ca2 | 2173 | 2101 | 72 | denied 92.6%, granted 2.6%, dismissed 2.4%, gvr 2.3% (est. n=2101) |
| ca3 | 1980 | 1932 | 48 | denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0% (est. n=1932) |
| ca7 | 1655 | 1619 | 36 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1619) |
| ca10 | 1451 | 1416 | 35 | denied 94.1%, granted 2.3%, dismissed 2.2%, gvr 1.5% (est. n=1416) |
| (none) | 1435 | 1360 | 75 | denied 99.2%, dismissed 0.8% (est. n=1360) |
| cafc | 933 | 905 | 28 | denied 92.5%, dismissed 3.0%, granted 3.0%, gvr 1.5% (est. n=905) |
| ca1 | 903 | 883 | 20 | denied 95.2%, granted 2.6%, dismissed 1.6%, gvr 0.6% (est. n=883) |
| cadc | 668 | 644 | 24 | denied 88.7%, granted 6.1%, dismissed 3.1%, gvr 2.2% (est. n=644) |
| Supreme Court of Florida | 533 | 523 | 10 | denied 97.1%, dismissed 2.7%, gvr 0.2% (est. n=523) |
| Court of Appeal of California, Second Appellate District | 328 | 325 | 3 | denied 93.8%, dismissed 3.7%, gvr 2.2%, granted 0.3% (est. n=325) |
| Court of Criminal Appeals of Texas | 325 | 322 | 3 | denied 96.6%, dismissed 1.6%, gvr 1.2%, granted 0.6% (est. n=322) |
| Supreme Court of California | 287 | 282 | 5 | denied 96.5%, dismissed 3.5% (est. n=282) |
| Court of Appeals of Michigan | 245 | 240 | 5 | denied 98.8%, dismissed 1.2% (est. n=240) |
| District Court of Appeal of Florida, Fourth District | 229 | 203 | 26 | denied 96.1%, dismissed 3.4%, granted 0.5% (est. n=203) |
| Court of Criminal Appeals of Oklahoma | 217 | 215 | 2 | denied 87.9%, gvr 8.4%, dismissed 2.3%, granted 1.4% (est. n=215) |
| Supreme Court of Virginia | 217 | 209 | 8 | denied 97.6%, dismissed 1.4%, gvr 1.0% (est. n=209) |
| Appellate Court of Illinois, First District | 214 | 211 | 3 | denied 99.1%, dismissed 0.9% (est. n=211) |
| District Court of Appeal of Florida, First District | 199 | 195 | 4 | denied 97.4%, dismissed 2.6% (est. n=195) |
| District Court of Appeal of Florida, Second District | 164 | 155 | 9 | denied 98.1%, dismissed 1.9% (est. n=155) |
| _… 299 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 31729 | 31057 | 672 | denied 96.4%, dismissed 2.4%, gvr 0.9%, granted 0.2% (est. n=31057) |
| paid | 14166 | 13713 | 453 | denied 92.1%, granted 4.4%, gvr 2.3%, dismissed 1.3% (est. n=13713) |
| (none) | 8 | 0 | 8 | — |

## Cert petitions by question-presented topic (`qp-topic-v0`)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. QP-bearing rows only — 8498 of 26517 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows; the bucket counts are denial-reweighted, and no reweighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 18019 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 10's extract sized the second: it counted 8502 QP-bearing row(s) in the frame it cut from, of which the artifact held 8502 labeled (100.0%). Both counts are batch 10's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 8145 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 10's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.0x — row for row, how much likelier a reference row was to be included than a drawn one when batch 10 landed: 353 carried in with certainty against 8149 drawn from the 8149 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| criminal-law | 4994 | 4987 | 7 | denied 96.5%, gvr 1.9%, granted 1.2%, dismissed 0.5% (est. n=4987) |
| civil-procedure | 2049 | 2033 | 16 | denied 94.7%, granted 2.3%, dismissed 2.3%, gvr 0.7% (est. n=2033) |
| habeas-and-postconviction | 1421 | 1421 | 0 | denied 96.3%, dismissed 1.9%, granted 1.2%, gvr 0.6% (est. n=1421) |
| constitutional-rights | 1402 | 1394 | 8 | denied 94.4%, dismissed 2.6%, granted 2.1%, gvr 0.9% (est. n=1394) |
| employment-and-antidiscrimination | 653 | 646 | 7 | denied 93.3%, granted 3.3%, dismissed 2.8%, gvr 0.6% (est. n=646) |
| business-and-financial-regulation | 587 | 575 | 12 | denied 87.0%, granted 5.9%, dismissed 3.8%, gvr 3.3% (est. n=575) |
| unclassifiable | 554 | 552 | 2 | denied 93.8%, dismissed 6.0%, granted 0.2% (est. n=552) |
| firearms | 539 | 536 | 3 | denied 92.0%, gvr 4.1%, granted 3.7%, dismissed 0.2% (est. n=536) |
| first-amendment | 485 | 475 | 10 | denied 92.6%, granted 5.1%, gvr 1.5%, dismissed 0.8% (est. n=475) |
| administrative-law-and-benefit-programs | 414 | 409 | 5 | denied 83.6%, granted 11.0%, gvr 4.4%, dismissed 1.0% (est. n=409) |
| sovereignty-and-foreign-relations | 253 | 252 | 1 | denied 82.9%, granted 10.3%, gvr 6.0%, dismissed 0.8% (est. n=252) |
| intellectual-property | 215 | 214 | 1 | denied 94.4%, granted 4.7%, gvr 0.9% (est. n=214) |
| election-law | 98 | 95 | 3 | denied 89.5%, granted 4.2%, dismissed 3.2%, gvr 3.2% (est. n=95) |
| tax | 94 | 94 | 0 | denied 94.7%, granted 5.3% (est. n=94) |
| environment-energy-and-property | 82 | 81 | 1 | denied 85.2%, granted 8.6%, gvr 6.2% (est. n=81) |
| immigration | 49 | 48 | 1 | denied 60.4%, granted 33.3%, gvr 4.2%, dismissed 2.1% (est. n=48) |

_Accrued over 10 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-fable-5, whose primaries matched the `qp-topic-v0` reference rater on 324 of 353 reference case(s) (91.8%), against the 22.9% a constant labeler scores on the same entries — **agreement, not accuracy**: the reference raters were agent sessions too, so rater error and labeler error cannot be separated, and the reference frame is grant-enriched, so the figure certifies the grant stream only. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 0 reference entr(ies) went uncovered. 8498 of 8502 labeled case(s) joined a row in this section's population; a gap is expected across batches, which span corpus vintages, and a large one reads as labels produced against another vintage rather than as thin coverage._

_Per-label agreement is **unmeasured in v0** for `election-law`, `environment-energy-and-property`, `immigration`, `intellectual-property`, `tax` — fewer reference examples than the support floor, where one entry moves the ratio by tens of points. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets, ordered by rows rather than by the table's reweighted count — the raw view the reweighted `est. n=` above does not give: `criminal-law` 1871 [81], `civil-procedure` 1680 [55], `constitutional-rights` 1177 [36], `habeas-and-postconviction` 557 [14], `business-and-financial-regulation` 533 [21], `employment-and-antidiscrimination` 527 [18], `first-amendment` 440 [13], `administrative-law-and-benefit-programs` 360 [29], `firearms` 332 [35], `unclassifiable` 293 [14], `sovereignty-and-foreign-relations` 226 [13], `intellectual-property` 206 [5], `tax` 94 [3], `environment-energy-and-property` 82 [6], `election-law` 80 [5], `immigration` 40 [5]. A bucket's `est. n=` is an estimate of the population its rows stand for, so it runs above the rows read; the reference share is not uniform across buckets, and the block holds every QP-bearing grant it could reach, so it inflates the grant-heavy topics most._

## Emergency applications by topic (`qp-topic-v1`)
_Scope: scotus, live/historical slice; counts are denial-reweighted estimates. Labeled applications only — 2027 of 2032 in-frame live-slice applications labeled, 1991 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are reweighted like every section here. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 2's extract counted 2027 application(s) in the frame it cut from, of which the artifact held 2027 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 1786 drawn from the 1786 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 1786 were drawn._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unclassifiable | 893 | 883 | 10 | denied 83.6%, granted 14.8%, withdrawn 1.5%, dismissed 0.1% (est. n=883) |
| habeas-and-postconviction | 481 | 474 | 7 | denied 89.5%, granted 9.3%, withdrawn 1.3% (est. n=474) |
| criminal-law | 171 | 168 | 3 | denied 92.3%, granted 6.0%, withdrawn 1.8% (est. n=168) |
| civil-procedure | 125 | 122 | 3 | denied 89.3%, granted 9.8%, withdrawn 0.8% (est. n=122) |
| election-law | 85 | 83 | 2 | denied 69.9%, granted 28.9%, withdrawn 1.2% (est. n=83) |
| immigration | 85 | 82 | 3 | denied 74.4%, granted 22.0%, withdrawn 3.7% (est. n=82) |
| administrative-law-and-benefit-programs | 40 | 38 | 2 | granted 78.9%, denied 21.1% (est. n=38) |
| first-amendment | 34 | 34 | 0 | denied 67.6%, granted 29.4%, withdrawn 2.9% (est. n=34) |
| employment-and-antidiscrimination | 30 | 28 | 2 | denied 89.3%, granted 10.7% (est. n=28) |
| environment-energy-and-property | 29 | 29 | 0 | denied 82.8%, granted 17.2% (est. n=29) |
| business-and-financial-regulation | 21 | 20 | 1 | denied 70.0%, granted 30.0% (est. n=20) |
| constitutional-rights | 12 | 11 | 1 | denied 63.6%, withdrawn 27.3%, granted 9.1% (est. n=11) |
| sovereignty-and-foreign-relations | 10 | 10 | 0 | denied 70.0%, granted 30.0% (est. n=10) |
| firearms | 6 | 6 | 0 | denied 83.3%, granted 16.7% (est. n=6) |
| intellectual-property | 3 | 3 | 0 | denied 100.0% (est. n=3) |
| tax | 2 | 2 | 0 | denied 100.0% (est. n=2) |

_Accrued over 2 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-opus-5-5, whose primaries matched the application reference block's adjudicated labels on 225 of 241 reference case(s) (93.4%), against the 38.2% a constant labeler scores on the same entries — **agreement, not accuracy**, and **not yet quotable**: the block's labels are the majority of three blind raters that are instances of the labeler's own model, so their errors and the labeler's are correlated, and the held-out check behind them held no row with stored application text; an independent rater is owed before an application agreement figure is quoted. It is the publication gate's reading, printed so the gate can be audited. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 0 reference entr(ies) went uncovered. 2027 of 2027 labeled application(s) joined a row in this section's population._

_Per-label agreement is **unmeasured** for `administrative-law-and-benefit-programs`, `business-and-financial-regulation`, `constitutional-rights`, `employment-and-antidiscrimination`, `environment-energy-and-property`, `firearms`, `first-amendment`, `intellectual-property`, `tax` — fewer reference examples than the support floor. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets: `unclassifiable` 893 [92], `habeas-and-postconviction` 481 [43], `criminal-law` 171 [24], `civil-procedure` 125 [24], `election-law` 85 [13], `immigration` 85 [10], `administrative-law-and-benefit-programs` 40 [9], `first-amendment` 34 [4], `employment-and-antidiscrimination` 30 [6], `environment-energy-and-property` 29 [4], `business-and-financial-regulation` 21 [2], `constitutional-rights` 12 [7], `sovereignty-and-foreign-relations` 10 [0], `firearms` 6 [1], `intellectual-property` 3 [1], `tax` 2 [1]._

## Topic mix by stage
_The share of each stage's **labeled** cases under each primary topic, read off the topic cuts above: cert is every labeled cert-form petition, merits the labeled petitions granted plenary review, interim every labeled emergency application. Each column is a share of its own stage, never of the docket, and carries the scope string under the table. The columns are **not stages of one funnel**: cert is a denial-reweighted share of a grant-enriched set, merits a share of the labeled grants, and interim another frame read from other inputs, so a difference between columns is not a grant propensity — the petition topic section's base-rate column is where that is read._

| topic | cert (est. n=13889; 8498 rows) | merits (n=364) | interim (n=2027) | interim, subject-bearing only |
| --- | --: | --: | --: | --: |
| criminal-law | 36.0% (1871) | 15.9% (58) | 8.4% (171) | 15.1% |
| civil-procedure | 14.8% (1680) | 12.9% (47) | 6.2% (125) | 11.0% |
| habeas-and-postconviction | 10.2% (557) | 4.7% (17) | 23.7% (481) | 42.4% |
| constitutional-rights | 10.1% (1177) | 8.0% (29) | 0.6% (12) | 1.1% |
| employment-and-antidiscrimination | 4.7% (527) | 5.8% (21) | 1.5% (30) | 2.6% |
| business-and-financial-regulation | 4.2% (533) | 9.3% (34) | 1.0% (21) | 1.9% |
| unclassifiable | 4.0% (293) | 0.3% (1) | 44.1% (893) | — |
| firearms | 3.9% (332) | 5.5% (20) | 0.3% (6) | 0.5% |
| first-amendment | 3.5% (440) | 6.6% (24) | 1.7% (34) | 3.0% |
| administrative-law-and-benefit-programs | 3.0% (360) | 12.4% (45) | 2.0% (40) | 3.5% |
| sovereignty-and-foreign-relations | 1.8% (226) | 7.1% (26) | 0.5% (10) | 0.9% |
| intellectual-property | 1.5% (206) | 2.7% (10) | 0.1% (3) | 0.3% |
| election-law | 0.7% (80) | 1.1% (4) | 4.2% (85) | 7.5% |
| tax | 0.7% (94) | 1.4% (5) | 0.1% (2) | 0.2% |
| environment-energy-and-property | 0.6% (82) | 1.9% (7) | 1.4% (29) | 2.6% |
| immigration | 0.4% (40) | 4.4% (16) | 4.2% (85) | 7.5% |

_Rows on hand in parentheses; each header's count is the stage's count as its section publishes it, `est. n=` where that section reweights._

_The subject-bearing column divides the interim counts by the applications outside `unclassifiable`. It sits beside the full share, never in place of it: whether a row names a subject at all depends on whether the labeler read a stored application or only the docket, so this column is no closer to what the applications are about than the full one._

_cert: QP-bearing rows only — 8498 of 26517 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows; the bucket counts are denial-reweighted, and no reweighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 18019 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 10's extract sized the second: it counted 8502 QP-bearing row(s) in the frame it cut from, of which the artifact held 8502 labeled (100.0%). Both counts are batch 10's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 8145 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 10's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.0x — row for row, how much likelier a reference row was to be included than a drawn one when batch 10 landed: 353 carried in with certainty against 8149 drawn from the 8149 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

_merits: Granted QP-bearing petitions only — 364 labeled grant(s) of the 671 plenary grant(s) in the cert scope; primaries only; not docket-representative. Plenary review here is the `granted` disposition, which takes in probable jurisdiction noted on a direct appeal and leaves out GVRs recorded as such (a few older merits GVRs still carry `granted`). The labeling frame was fully labeled when its newest batch landed, so the missing grants are those with no stored questions-presented text. Questions-presented coverage is zero before Term 2023 and uneven after, so this mix is weighted toward the Terms with stored texts and is not the merits docket's._

_interim: Labeled applications only — 2027 of 2032 in-frame live-slice applications labeled, 1991 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are reweighted like every section here. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 2's extract counted 2027 application(s) in the frame it cut from, of which the artifact held 2027 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 1786 drawn from the 1786 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 1786 were drawn._

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a row can sit outside the serial census — a petition whose docket number carries no serial the stream parser can read (a consolidated, prefixed, or dash-variant spelling), ingested under its Term but belonging to no stream's census — so `ingested` can exceed `filings`. `ingested` and `grants observed` are raw counts of rows on hand; the grant rate is the denial-reweighted estimate, and its `est. n` is the reweighted resolved count it divides by — which is why it too can exceed `ingested`. The plain `n` beside the pace to grant is different: that one is a raw count of the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate and is not a rate at all; the raw grant count is comparable to the weighted denominator only because a grant is always kept at weight 1 while denials are sampled. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | est. grant rate (weighted) | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2026 | 1589 | 1558 | 1.5% (est. n=609) | 9 | 71 (n=9) | complete |
| 2025 | 4134 | 4134 | 2.6% (est. n=4002) | 106 | 153 (n=106) | complete |
| 2024 | 2428 | 2576 | 3.2% (est. n=3782) | 120 | 137 (n=119) | partial |
| 2023 | 1375 | 1742 | 3.3% (est. n=4154) | 138 | 152 (n=138) | complete |
| 2022 | 1252 | 1629 | 2.7% (est. n=4050) | 109 | 143 (n=109) | complete |
| 2021 | 1611 | 2033 | 3.1% (est. n=4877) | 151 | 163 (n=151) | complete |
| 2020 | 1829 | 2293 | 3.1% (est. n=5263) | 162 | 144 (n=162) | complete |
| 2019 | 1478 | 2008 | 2.9% (est. n=5356) | 158 | 141 (n=158) | complete |
| 2018 | 1593 | 2228 | 2.4% (est. n=6408) | 151 | 152 (n=151) | complete |
| 2017 | 6313 | 6316 | 2.7% (est. n=6269) | 170 | 164 (n=170) | complete |

_Replay/backtest cells: this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding `record/context.json`'s `decided_before`, an October Term, because later Terms post-date what you are allowed to know. These rows are keyed on the **docket-number** Term, so your own Term's row already contains your case._

## Not yet included

- **The `granted` / `gvr` split is not comparable across Terms.** The `gvr` label is a forward convention: a resolution recorded before it existed keeps `granted`, and no post-hoc rule separates a merits GVR from a plenary grant without re-resolving the source. OT2023 and OT2024 were resolved into the corpus inside that window, so they carry **zero** GVRs against 30-59% of the grant family in every Term either side of them — ingestion history, not the Court changing behaviour. Read the grant family as one number — the JSON artifacts publish it per Term as `est_grant_family_rate` — because the split is safe within a Term and meaningless between them.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver reads both sides: the vacatur-remand form (`gvr`) and probable jurisdiction noted or postponed to the merits (`granted`), and a summary affirmance (`denied`) or a dismissal for want of a substantial federal question, for want of jurisdiction or as moot (`dismissed`). A split order (affirmed in part and reversed in part, or dismissed in part and affirmed in part) is read on neither side and leaves the docket unresolved.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts this docket pack does not carry; the statpack's authorship section rolls up the per-opinion record instead.
