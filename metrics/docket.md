# Docket pack

Facts about the dockets themselves: what the Supreme Court is asked to take, from which court below, on which fee stream, after how many relists, and how it disposes of what it is asked. It carries **no claim about this project's predictions** — no accuracy, no model ranking, no measure of which petitions are worth predicting — so it is readable and citable without any interest in whether those models are any good.

**Corpus.** 2154026 case(s): 82044 resolved, 2071982 open, pulled through 2026-11-09. Most rows are an unlabeled bulk import, so the two overview sections below describe the **labeled subset only** — read `resolved` against `cases` before quoting one.

**Live/historical slice.** 52364 case(s), 51077 resolved — matters read from the Court's own docket pages, the population the cert statistics below draw from. It also carries the interim application rows, which no cert statistic aggregates, so a cert denominator can sit below this count; 37553 docketed filing(s) across the walked Terms.

**How to read the tables.** Each section states its own scope: the court, the population, and whether its counts are denial-reweighted. That reweighting matters. The historical walk ingests every decided petition except denials, which it samples on a committed frame, so a raw count would badly overstate the grant rate; a reweighted section counts each ingested petition for the number of petitions it stands in for. **Every section here is reweighted**, including the two overview cuts: nearly every labeled SCOTUS row is a sampled one, so a raw disposition split there would overstate the grant family several-fold, while a bulk-import circuit row carries weight 1 and is unchanged by it. So every count is a population **estimate** rather than rows on hand, and every denominator is written `est. n=`. In the breakdown tables that denominator is the `resolved` column beside the rate; the per-Term census states its own the same way.

**In the breakdown tables the estimate does not tell you** how many petitions were actually read to produce it. An `est. n=` of a few hundred rests on a raw row count several times smaller, and a breakdown row carries no raw view of its own — so treat a small reweighted cell as weaker evidence than its denominator suggests, and read a rate against the whole-population figures above it rather than on its own. The per-Term census is the exception and the place to calibrate that gap: it prints the observed `ingested (rows)` beside the reweighted estimate, so the ratio between them is legible for every Term.

**Where a value is missing** the row still appears rather than being dropped, so a coverage gap is never hidden inside a rate. A `(none)` bucket means *no value on that dimension*, and what that stands for differs by cut, so read it against the section rather than as one thing. On the circuit cut it is mostly **not** an unknown court below: it is the petitions whose court below is not a federal circuit — state supreme courts above all — and the section that follows names them. On the era cut it is the absence of any date signal. On the fee-class cut it is a parsing gap: fee class is read by a stricter serial parser than the one behind the Term cuts, so docket numbers it cannot read — consolidated and prefixed spellings, and dash-variant numbers the Term cut folds and this one does not — land here. A display annotation is not among them: both parses strip it. That bucket is therefore **not a random slice**, so read the paid/IFP table as a split of the petitions whose numbers parse cleanly rather than a partition of the whole docket. Where an `(unknown)` bucket appears — the relist and CVSG cuts, whose signal comes from parsed proceedings — it means *not yet parsed* rather than *did not happen*.

## Cases by court
_Scope: all courts; includes the frozen bulk import; counts are denial-reweighted estimates._

| court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| scotus | 599533 | 58987 | 540546 | denied 77.6%, granted 19.2%, dismissed 1.6%, gvr 1.1%, other 0.4%, withdrawn 0.1% (est. n=58987) |
| ca9 | 247638 | 1463 | 246175 | other 94.5%, dismissed 2.6%, denied 2.0%, granted 0.8%, withdrawn 0.1% (est. n=1463) |
| ca5 | 203464 | 1502 | 201962 | other 91.0%, dismissed 4.0%, denied 3.5%, granted 1.5% (est. n=1502) |
| ca4 | 187218 | 15593 | 171625 | other 63.2%, dismissed 36.2%, denied 0.4%, granted 0.2%, granted-in-part 0.0% (est. n=15593) |
| ca6 | 142307 | 1320 | 140987 | other 93.9%, dismissed 3.4%, denied 1.4%, granted 1.3% (est. n=1320) |
| ca2 | 120926 | 2510 | 118416 | other 92.1%, dismissed 4.3%, denied 2.5%, granted 1.0%, granted-in-part 0.0%, withdrawn 0.0% (est. n=2510) |
| ca3 | 112972 | 1279 | 111693 | other 93.2%, dismissed 4.5%, denied 1.2%, granted 1.1% (est. n=1279) |
| ca8 | 103363 | 2378 | 100985 | other 89.9%, dismissed 4.4%, denied 2.9%, granted 2.7%, withdrawn 0.0% (est. n=2378) |
| ca11 | 95619 | 45 | 95574 | other 95.6%, denied 2.2%, granted 2.2% (est. n=45) |
| ca7 | 92080 | 895 | 91185 | other 91.4%, dismissed 5.0%, denied 2.1%, granted 1.5% (est. n=895) |
| ca10 | 81534 | 34 | 81500 | other 88.2%, denied 11.8% (est. n=34) |
| cafc | 72586 | 11 | 72575 | other 100.0% (est. n=11) |
| cadc | 57037 | 3042 | 53995 | other 94.3%, dismissed 2.2%, denied 2.0%, granted 1.5% (est. n=3042) |
| ca1 | 45337 | 599 | 44738 | other 86.3%, dismissed 8.0%, denied 5.0%, granted 0.7% (est. n=599) |
| cand | 10 | 0 | 10 | — |
| flnd | 5 | 0 | 5 | — |
| nysd | 4 | 0 | 4 | — |
| ded | 2 | 0 | 2 | — |
| flmd | 1 | 0 | 1 | — |
| jpml | 1 | 0 | 1 | — |
| paed | 1 | 0 | 1 | — |
| tnmd | 1 | 0 | 1 | — |
| txed | 1 | 0 | 1 | — |

## SCOTUS cases by era
_Scope: scotus; includes the frozen bulk import; counts are denial-reweighted estimates._

| era | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 126116 | 267 | 125849 | other 76.4%, dismissed 17.6%, denied 4.5%, granted 1.5% (est. n=267) |
| 2000s | 124840 | 13 | 124827 | other 100.0% (est. n=13) |
| 1990s | 109307 | 12 | 109295 | other 91.7%, denied 8.3% (est. n=12) |
| 2010s | 105025 | 24768 | 80257 | denied 76.3%, granted 21.2%, dismissed 1.4%, gvr 1.0%, withdrawn 0.0% (est. n=24768) |
| 1980s | 62149 | 1 | 62148 | other 100.0% (est. n=1) |
| 1970s | 36385 | 3 | 36382 | other 100.0% (est. n=3) |
| 2020s | 35552 | 33923 | 1629 | denied 79.2%, granted 17.8%, dismissed 1.7%, gvr 1.1%, withdrawn 0.1% (est. n=33923) |
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
| denied | 43342 | 43342 | 0 | denied 100.0% (est. n=43342) |
| (open) | 1245 | 0 | 1245 | — |
| dismissed | 919 | 919 | 0 | dismissed 100.0% (est. n=919) |
| granted | 639 | 639 | 0 | granted 100.0% (est. n=639) |
| gvr | 637 | 637 | 0 | gvr 100.0% (est. n=637) |

## Modern cert petitions by originating circuit
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| (none) | 12461 | 12077 | 384 | denied 96.5%, dismissed 2.2%, gvr 0.7%, granted 0.6% (est. n=12077) |
| ca9 | 5742 | 5615 | 127 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.2% (est. n=5615) |
| ca5 | 5565 | 5418 | 147 | denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6% (est. n=5418) |
| ca11 | 4029 | 3954 | 75 | denied 94.9%, gvr 2.1%, dismissed 1.8%, granted 1.2% (est. n=3954) |
| ca4 | 3496 | 3425 | 71 | denied 95.2%, dismissed 2.2%, gvr 1.4%, granted 1.2% (est. n=3425) |
| ca6 | 3104 | 3017 | 87 | denied 95.8%, dismissed 1.5%, gvr 1.4%, granted 1.3% (est. n=3017) |
| ca8 | 2261 | 2211 | 50 | denied 95.4%, dismissed 1.9%, gvr 1.6%, granted 1.0% (est. n=2211) |
| ca2 | 2160 | 2081 | 79 | denied 92.6%, granted 2.6%, dismissed 2.5%, gvr 2.4% (est. n=2081) |
| ca3 | 2044 | 1994 | 50 | denied 95.0%, dismissed 2.6%, granted 1.5%, gvr 1.0% (est. n=1994) |
| ca7 | 1637 | 1597 | 40 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1597) |
| ca10 | 1522 | 1482 | 40 | denied 94.3%, dismissed 2.1%, granted 1.9%, gvr 1.7% (est. n=1482) |
| ca1 | 935 | 914 | 21 | denied 95.4%, granted 2.5%, dismissed 1.5%, gvr 0.5% (est. n=914) |
| cafc | 904 | 874 | 30 | denied 92.2%, dismissed 3.1%, granted 3.1%, gvr 1.6% (est. n=874) |
| cadc | 693 | 666 | 27 | denied 89.0%, granted 5.9%, dismissed 3.0%, gvr 2.1% (est. n=666) |
| fla | 80 | 80 | 0 | denied 100.0% (est. n=80) |
| alacrimapp | 30 | 30 | 0 | denied 100.0% (est. n=30) |
| texcrimapp | 21 | 21 | 0 | denied 95.2%, gvr 4.8% (est. n=21) |
| cal | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| nev | 20 | 20 | 0 | denied 100.0% (est. n=20) |
| ariz | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| neb | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| ohio | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| sc | 10 | 10 | 0 | denied 100.0% (est. n=10) |
| fladistctapp4 | 5 | 0 | 5 | — |
| va | 3 | 0 | 3 | — |
| _… 10 more bucket(s) in the JSON_ | | | | |

## Cert petitions by relist count
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. Relists are read off the stored distribution count, which holds the `dist-v2` reading; a parse change moves which entries count as a relist, not the tier labels, so the parse travels with the numbers. The count is an upper bound on true relists under either reading — a reschedule before first consideration also adds a distribution entry._

| relist_bucket | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| 0 | 38667 | 37516 | 1151 | denied 96.9%, dismissed 2.3%, gvr 0.4%, granted 0.4% (est. n=37516) |
| 1 | 6480 | 6418 | 62 | denied 92.1%, gvr 3.9%, granted 3.4%, dismissed 0.6% (est. n=6418) |
| 3+ | 840 | 825 | 15 | denied 69.1%, granted 16.1%, gvr 13.8%, dismissed 1.0% (est. n=825) |
| 2 | 786 | 778 | 8 | denied 65.8%, granted 18.6%, gvr 14.5%, dismissed 1.0% (est. n=778) |
| (unknown) | 9 | 0 | 9 | — |

## Cert petitions by CVSG status
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| cvsg | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| none | 46593 | 45373 | 1220 | denied 95.3%, dismissed 2.0%, gvr 1.4%, granted 1.3% (est. n=45373) |
| cvsg | 180 | 164 | 16 | denied 62.8%, granted 29.3%, gvr 5.5%, dismissed 2.4% (est. n=164) |
| (unknown) | 9 | 0 | 9 | — |

## Cert petitions by capital-case marking
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. The capital flag is latched from supremecourt.gov's own `bCapitalCase` payload field, OR-ed with the `*** CAPITAL CASE ***` annotation the same channel appends to the docket number — either alone under-reports, and no other channel serves either reading. So `last_live_polled` is the column's coverage sentinel: a row no live poll stamped buckets as `(unknown)` rather than as unmarked, and none appear here because this section is already scoped to the live slice, which is that stamp. Inside the slice the stamp records an attempted poll rather than an ingested payload, so `unmarked` means no channel that wrote the row read either signal — silence, not a denial. Read it as an upper bound: contamination runs one way, into `unmarked`, so it can only shrink the gap between these buckets, never widen it. The split is a marginal one — it describes what the two populations are, not what the marking adds over the cuts beside it._

| capital_case | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unmarked | 45552 | 44337 | 1215 | denied 95.2%, dismissed 2.0%, gvr 1.4%, granted 1.4% (est. n=44337) |
| capital | 1230 | 1200 | 30 | denied 95.5%, granted 1.9%, gvr 1.3%, dismissed 1.2% (est. n=1200) |

## Petitions by originating court (incl. state courts)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| originating_court | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ca9 | 5742 | 5615 | 127 | denied 94.9%, granted 2.1%, dismissed 1.9%, gvr 1.2% (est. n=5615) |
| ca5 | 5565 | 5418 | 147 | denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6% (est. n=5418) |
| ca11 | 4029 | 3954 | 75 | denied 94.9%, gvr 2.1%, dismissed 1.8%, granted 1.2% (est. n=3954) |
| ca4 | 3496 | 3425 | 71 | denied 95.2%, dismissed 2.2%, gvr 1.4%, granted 1.2% (est. n=3425) |
| ca6 | 3104 | 3017 | 87 | denied 95.8%, dismissed 1.5%, gvr 1.4%, granted 1.3% (est. n=3017) |
| ca8 | 2261 | 2211 | 50 | denied 95.4%, dismissed 1.9%, gvr 1.6%, granted 1.0% (est. n=2211) |
| ca2 | 2160 | 2081 | 79 | denied 92.6%, granted 2.6%, dismissed 2.5%, gvr 2.4% (est. n=2081) |
| ca3 | 2044 | 1994 | 50 | denied 95.0%, dismissed 2.6%, granted 1.5%, gvr 1.0% (est. n=1994) |
| ca7 | 1637 | 1597 | 40 | denied 95.1%, dismissed 2.4%, gvr 1.4%, granted 1.1% (est. n=1597) |
| ca10 | 1522 | 1482 | 40 | denied 94.3%, dismissed 2.1%, granted 1.9%, gvr 1.7% (est. n=1482) |
| (none) | 1516 | 1428 | 88 | denied 99.2%, dismissed 0.8% (est. n=1428) |
| ca1 | 935 | 914 | 21 | denied 95.4%, granted 2.5%, dismissed 1.5%, gvr 0.5% (est. n=914) |
| cafc | 904 | 874 | 30 | denied 92.2%, dismissed 3.1%, granted 3.1%, gvr 1.6% (est. n=874) |
| cadc | 693 | 666 | 27 | denied 89.0%, granted 5.9%, dismissed 3.0%, gvr 2.1% (est. n=666) |
| Supreme Court of Florida | 588 | 579 | 9 | denied 97.4%, dismissed 2.4%, gvr 0.2% (est. n=579) |
| Court of Criminal Appeals of Texas | 379 | 376 | 3 | denied 97.1%, dismissed 1.3%, gvr 1.1%, granted 0.5% (est. n=376) |
| Court of Appeal of California, Second Appellate District | 314 | 310 | 4 | denied 93.5%, dismissed 3.9%, gvr 2.3%, granted 0.3% (est. n=310) |
| Supreme Court of California | 265 | 260 | 5 | denied 95.8%, dismissed 4.2% (est. n=260) |
| Supreme Court of Virginia | 264 | 257 | 7 | denied 98.1%, dismissed 1.2%, gvr 0.8% (est. n=257) |
| Court of Appeals of Michigan | 257 | 252 | 5 | denied 98.8%, dismissed 1.2% (est. n=252) |
| Court of Criminal Appeals of Oklahoma | 255 | 252 | 3 | denied 89.3%, gvr 7.1%, dismissed 2.4%, granted 1.2% (est. n=252) |
| District Court of Appeal of Florida, Fourth District | 241 | 217 | 24 | denied 96.3%, dismissed 3.2%, granted 0.5% (est. n=217) |
| Appellate Court of Illinois, First District | 210 | 207 | 3 | denied 99.0%, dismissed 1.0% (est. n=207) |
| District Court of Appeal of Florida, First District | 168 | 164 | 4 | denied 97.0%, dismissed 3.0% (est. n=164) |
| District of Columbia Court of Appeals | 164 | 162 | 2 | denied 96.3%, dismissed 2.5%, granted 0.6%, gvr 0.6% (est. n=162) |
| _… 340 more bucket(s) in the JSON_ | | | | |

## Cert petitions by fee class (paid vs IFP)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates._

| fee_class | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| ifp | 32585 | 31823 | 762 | denied 96.5%, dismissed 2.3%, gvr 1.0%, granted 0.1% (est. n=31823) |
| paid | 14189 | 13714 | 475 | denied 92.1%, granted 4.4%, gvr 2.3%, dismissed 1.3% (est. n=13714) |
| (none) | 8 | 0 | 8 | — |

## Cert petitions by question-presented topic (`qp-topic-v0`)
_Scope: scotus, modern discretionary-cert dockets, live/historical slice; counts are denial-reweighted estimates. QP-bearing rows only — 9347 of 39168 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows; the bucket counts are denial-reweighted, and no reweighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 29821 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 11's extract sized the second: it counted 11871 QP-bearing row(s) in the frame it cut from, of which the artifact held 9351 labeled (78.8%). Both counts are batch 11's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 8994 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 11's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.3x — row for row, how much likelier a reference row was to be included than a drawn one when batch 11 landed: 353 carried in with certainty against 8998 drawn from the 11518 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| criminal-law | 2292 | 2281 | 11 | denied 92.2%, gvr 4.8%, granted 1.9%, dismissed 1.1% (est. n=2281) |
| civil-procedure | 1787 | 1767 | 20 | denied 93.7%, dismissed 2.7%, granted 2.6%, gvr 1.0% (est. n=1767) |
| constitutional-rights | 1217 | 1206 | 11 | denied 93.4%, dismissed 3.0%, granted 2.4%, gvr 1.2% (est. n=1206) |
| habeas-and-postconviction | 679 | 677 | 2 | denied 92.2%, dismissed 4.0%, granted 2.4%, gvr 1.5% (est. n=677) |
| employment-and-antidiscrimination | 545 | 537 | 8 | denied 92.0%, granted 3.9%, dismissed 3.4%, gvr 0.7% (est. n=537) |
| business-and-financial-regulation | 541 | 527 | 14 | denied 85.6%, granted 6.6%, dismissed 4.2%, gvr 3.6% (est. n=527) |
| first-amendment | 452 | 439 | 13 | denied 91.8%, granted 5.7%, gvr 1.6%, dismissed 0.9% (est. n=439) |
| firearms | 403 | 399 | 4 | denied 89.2%, gvr 8.0%, granted 2.5%, dismissed 0.3% (est. n=399) |
| administrative-law-and-benefit-programs | 367 | 360 | 7 | denied 81.1%, granted 12.8%, gvr 5.0%, dismissed 1.1% (est. n=360) |
| unclassifiable | 316 | 313 | 3 | denied 89.1%, dismissed 10.5%, granted 0.3% (est. n=313) |
| sovereignty-and-foreign-relations | 230 | 228 | 2 | denied 81.1%, granted 11.4%, gvr 6.6%, dismissed 0.9% (est. n=228) |
| intellectual-property | 209 | 208 | 1 | denied 94.2%, granted 4.8%, gvr 1.0% (est. n=208) |
| tax | 96 | 96 | 0 | denied 94.8%, granted 5.2% (est. n=96) |
| election-law | 86 | 81 | 5 | denied 84.0%, granted 7.4%, dismissed 4.9%, gvr 3.7% (est. n=81) |
| environment-energy-and-property | 84 | 83 | 1 | denied 85.5%, granted 8.4%, gvr 6.0% (est. n=83) |
| immigration | 43 | 41 | 2 | denied 53.7%, granted 36.6%, gvr 7.3%, dismissed 2.4% (est. n=41) |

_Accrued over 11 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-opus-5-5, whose primaries matched the `qp-topic-v0` reference rater on 313 of 351 reference case(s) (89.2%), against the 23.1% a constant labeler scores on the same entries — **agreement, not accuracy**: the reference raters were agent sessions too, so rater error and labeler error cannot be separated, and the reference frame is grant-enriched, so the figure certifies the grant stream only. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 2 reference entr(ies) went uncovered. 9347 of 9351 labeled case(s) joined a row in this section's population; a gap is expected across batches, which span corpus vintages, and a large one reads as labels produced against another vintage rather than as thin coverage._

_Per-label agreement is **unmeasured in v0** for `election-law`, `environment-energy-and-property`, `immigration`, `intellectual-property`, `tax` — fewer reference examples than the support floor, where one entry moves the ratio by tens of points. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets, ordered by rows rather than by the table's reweighted count — the raw view the reweighted `est. n=` above does not give: `criminal-law` 2292 [81], `civil-procedure` 1787 [55], `constitutional-rights` 1217 [36], `habeas-and-postconviction` 679 [14], `employment-and-antidiscrimination` 545 [18], `business-and-financial-regulation` 541 [21], `first-amendment` 452 [13], `firearms` 403 [35], `administrative-law-and-benefit-programs` 367 [29], `unclassifiable` 316 [14], `sovereignty-and-foreign-relations` 230 [13], `intellectual-property` 209 [5], `tax` 96 [3], `election-law` 86 [5], `environment-energy-and-property` 84 [6], `immigration` 43 [5]. A bucket's `est. n=` is an estimate of the population its rows stand for, so it runs above the rows read; the reference share is not uniform across buckets, and the block holds every QP-bearing grant it could reach, so it inflates the grant-heavy topics most._

## Emergency applications by topic (`qp-topic-v1`)
_Scope: scotus, live/historical slice; counts are denial-reweighted estimates. Labeled applications only — 2029 of 2234 in-frame live-slice applications labeled, 1993 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are reweighted like every section here. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 4's extract counted 2029 application(s) in the frame it cut from, of which the artifact held 2029 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 1788 drawn from the 1788 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 1788 were drawn._

| qp_topic | cases | resolved | open | base rate (resolved) |
| --- | --: | --: | --: | --- |
| unclassifiable | 894 | 888 | 6 | denied 83.7%, granted 14.8%, withdrawn 1.5%, dismissed 0.1% (est. n=888) |
| habeas-and-postconviction | 482 | 475 | 7 | denied 89.5%, granted 9.3%, withdrawn 1.3% (est. n=475) |
| criminal-law | 171 | 169 | 2 | denied 92.3%, granted 5.9%, withdrawn 1.8% (est. n=169) |
| civil-procedure | 125 | 123 | 2 | denied 89.4%, granted 9.8%, withdrawn 0.8% (est. n=123) |
| election-law | 85 | 83 | 2 | denied 69.9%, granted 28.9%, withdrawn 1.2% (est. n=83) |
| immigration | 85 | 83 | 2 | denied 74.7%, granted 21.7%, withdrawn 3.6% (est. n=83) |
| administrative-law-and-benefit-programs | 40 | 38 | 2 | granted 78.9%, denied 21.1% (est. n=38) |
| first-amendment | 34 | 34 | 0 | denied 67.6%, granted 29.4%, withdrawn 2.9% (est. n=34) |
| employment-and-antidiscrimination | 30 | 29 | 1 | denied 89.7%, granted 10.3% (est. n=29) |
| environment-energy-and-property | 29 | 29 | 0 | denied 82.8%, granted 17.2% (est. n=29) |
| business-and-financial-regulation | 21 | 20 | 1 | denied 70.0%, granted 30.0% (est. n=20) |
| constitutional-rights | 12 | 11 | 1 | denied 63.6%, withdrawn 27.3%, granted 9.1% (est. n=11) |
| sovereignty-and-foreign-relations | 10 | 10 | 0 | denied 70.0%, granted 30.0% (est. n=10) |
| firearms | 6 | 6 | 0 | denied 83.3%, granted 16.7% (est. n=6) |
| intellectual-property | 3 | 3 | 0 | denied 100.0% (est. n=3) |
| tax | 2 | 2 | 0 | denied 100.0% (est. n=2) |

_Accrued over 4 labeling batches, whose labelers may differ. The most recent was labeled by claude-code/claude-opus-5-5, whose primaries matched the application reference block's adjudicated labels on 222 of 241 reference case(s) (92.1%), against the 38.2% a constant labeler scores on the same entries — **agreement, not accuracy**, and **not yet quotable**: the block's labels are the majority of three blind raters that are instances of the labeler's own model, so their errors and the labeler's are correlated, and the held-out check behind them held no row with stored application text; an independent rater is owed before an application agreement figure is quoted. It is the publication gate's reading, printed so the gate can be audited. That rate certifies the batch that produced it, not every row in the table above; the per-batch figures are in the labels artifact. 0 reference entr(ies) went uncovered. 2029 of 2029 labeled application(s) joined a row in this section's population._

_Per-label agreement is **unmeasured** for `administrative-law-and-benefit-programs`, `business-and-financial-regulation`, `constitutional-rights`, `employment-and-antidiscrimination`, `environment-energy-and-property`, `firearms`, `first-amendment`, `intellectual-property`, `tax` — fewer reference examples than the support floor. The figure above certifies none of those rows._

_Rows on hand behind each bucket, reference-sourced in brackets: `unclassifiable` 894 [92], `habeas-and-postconviction` 482 [43], `criminal-law` 171 [24], `civil-procedure` 125 [24], `election-law` 85 [13], `immigration` 85 [10], `administrative-law-and-benefit-programs` 40 [9], `first-amendment` 34 [4], `employment-and-antidiscrimination` 30 [6], `environment-energy-and-property` 29 [4], `business-and-financial-regulation` 21 [2], `constitutional-rights` 12 [7], `sovereignty-and-foreign-relations` 10 [0], `firearms` 6 [1], `intellectual-property` 3 [1], `tax` 2 [1]._

## Topic mix by stage
_The share of each stage's **labeled** cases under each primary topic, read off the topic cuts above: cert is every labeled cert-form petition, merits the labeled petitions granted plenary review, interim every labeled emergency application. Each column is a share of its own stage, never of the docket, and carries the scope string under the table. The columns are **not stages of one funnel**: cert is a denial-reweighted share of a grant-enriched set, merits a share of the labeled grants, and interim another frame read from other inputs, so a difference between columns is not a grant propensity — the petition topic section's base-rate column is where that is read._

| topic | cert (n=9347) | merits (n=342) | interim (n=2029) | interim, subject-bearing only |
| --- | --: | --: | --: | --: |
| criminal-law | 24.5% (2292) | 12.9% (44) | 8.4% (171) | 15.1% |
| civil-procedure | 19.1% (1787) | 13.5% (46) | 6.2% (125) | 11.0% |
| constitutional-rights | 13.0% (1217) | 8.5% (29) | 0.6% (12) | 1.1% |
| habeas-and-postconviction | 7.3% (679) | 4.7% (16) | 23.8% (482) | 42.5% |
| employment-and-antidiscrimination | 5.8% (545) | 6.1% (21) | 1.5% (30) | 2.6% |
| business-and-financial-regulation | 5.8% (541) | 10.2% (35) | 1.0% (21) | 1.9% |
| first-amendment | 4.8% (452) | 7.3% (25) | 1.7% (34) | 3.0% |
| firearms | 4.3% (403) | 2.9% (10) | 0.3% (6) | 0.5% |
| administrative-law-and-benefit-programs | 3.9% (367) | 13.5% (46) | 2.0% (40) | 3.5% |
| unclassifiable | 3.4% (316) | 0.3% (1) | 44.1% (894) | — |
| sovereignty-and-foreign-relations | 2.5% (230) | 7.6% (26) | 0.5% (10) | 0.9% |
| intellectual-property | 2.2% (209) | 2.9% (10) | 0.1% (3) | 0.3% |
| tax | 1.0% (96) | 1.5% (5) | 0.1% (2) | 0.2% |
| election-law | 0.9% (86) | 1.8% (6) | 4.2% (85) | 7.5% |
| environment-energy-and-property | 0.9% (84) | 2.0% (7) | 1.4% (29) | 2.6% |
| immigration | 0.5% (43) | 4.4% (15) | 4.2% (85) | 7.5% |

_Rows on hand in parentheses; each header's count is the stage's count as its section publishes it, `est. n=` where that section reweights._

_The subject-bearing column divides the interim counts by the applications outside `unclassifiable`. It sits beside the full share, never in place of it: whether a row names a subject at all depends on whether the labeler read a stored application or only the docket, so this column is no closer to what the applications are about than the full one._

_cert: QP-bearing rows only — 9347 of 39168 in-scope ingested rows labeled; grant-enriched; primaries only; not docket-representative. Those two counts are raw rows; the bucket counts are denial-reweighted, and no reweighting recovers the docket — QP presence is itself outcome- and stream-correlated, so this stays a share of QP-bearing rows. Coverage is uneven across Terms and zero on the earliest of them, so the mix is not the whole slice's; the base-rate column is over a grant-enriched population and is not comparable to the sections above. The 29821 unlabeled row(s) span two gaps at once — rows carrying no stored questions-presented text, which no labeling batch can reach, and QP-bearing rows whose batch has not come up — and batch 11's extract sized the second: it counted 11871 QP-bearing row(s) in the frame it cut from, of which the artifact held 9351 labeled (78.8%). Both counts are batch 11's, taken at its own corpus vintage rather than this pack's: the frame grows with every pull while the labeled count moves only when a batch lands, so read that share as a ceiling on the share of the frame as it now stands, not as a reading of this blob. Labeling accrues in batches, so the labeled rows are two populations on different terms: 353 hand reference-set members, carried in every batch and so included with certainty, and 8994 drawn over this blob by a Term x fee-class-stratified, seeded-hash order from the QP-bearing frame batch 11's extract counted. Both count once here, so the reference block — grant-enriched by design and carrying no sampling weights — is over-represented by at least about 1.3x — row for row, how much likelier a reference row was to be included than a drawn one when batch 11 landed: 353 carried in with certainty against 8998 drawn from the 11518 QP-bearing row(s) outside the block that batch's extract counted. Measured against that frame rather than bounded over rows no batch could reach — and a floor rather than a ceiling at this pack's vintage, since the frame grows with every pull while the drawn count waits for the next batch. It closes to 1.0x as the frame is labeled, which a bound over unreachable rows never does, and this mix is not the frame's until every QP-bearing row is labeled. A naive share partly counts coordinated filing campaigns rather than subjects; no de-duplicated companion is published._

_merits: Granted QP-bearing petitions only — 342 labeled grant(s) of the 639 plenary grant(s) in the cert scope; primaries only; not docket-representative. Plenary review here is the `granted` disposition, which takes in probable jurisdiction noted on a direct appeal and leaves out GVRs recorded as such (a few older merits GVRs still carry `granted`). The petition frame is still being labeled, so the missing grants are both those with no stored questions-presented text and those whose batch has not come up; reference-set grants are in every batch, so they are over-represented until it clears. Questions-presented coverage is zero before Term 2023 and uneven after, so this mix is weighted toward the Terms with stored texts and is not the merits docket's._

_interim: Labeled applications only — 2029 of 2234 in-frame live-slice applications labeled, 1993 of the labeled read from the docket alone; primaries only; not docket-representative. Those counts are raw rows (the second includes the few duplicate rows the labeling frame folds into one per docket number); the bucket counts are reweighted like every section here. The frame is the live slice's non-extension application dockets, substantive asks and asks whose kind was never read alike, read from different inputs than the petition cut, so the two are never pooled. A docket-only row whose caption and entries name no subject is `unclassifiable` by rule, so that bucket tracks how thin the dockets are as much as what the applications are about. Batch 4's extract counted 2029 application(s) in the frame it cut from, of which the artifact held 2029 labeled (100.0%); read that share as a ceiling on the share of the frame as it now stands, since the frame grows with every pull. The reference block rides in every batch, so its 241 row(s) are over-represented against the 1788 drawn from the 1788 outside it by no factor — the frame was fully labeled when that batch landed, and this mix is not the frame's until every application is labeled. Of the labeled rows here, 241 are reference-block members and 1788 were drawn._

## SCOTUS cert petitions by Term
_Live/historical slice. `filings` is the count of docketed serials across the paid and IFP streams, read from the discovery cursors — exact for docketed numbers, a slight upper bound on real petitions since withheld serials still count. **The two columns are not nested**: `ingested` counts rows on hand, and a row can sit outside the serial census — a petition whose docket number carries no serial the stream parser can read (a consolidated, prefixed, or dash-variant spelling), ingested under its Term but belonging to no stream's census — so `ingested` can exceed `filings`. `ingested` and `grants observed` are raw counts of rows on hand; the grant rate is the denial-reweighted estimate, and its `est. n` is the reweighted resolved count it divides by — which is why it too can exceed `ingested`. The plain `n` beside the pace to grant is different: that one is a raw count of the granted petitions carrying both dates. Dividing `grants observed` by `ingested` does **not** reproduce the rate and is not a rate at all; the raw grant count is comparable to the weighted denominator only because a grant is always kept at weight 1 while denials are sampled. The rate pools the paid and IFP streams, whose own grant rates differ several-fold, so a Term-over-Term move can be a shift in that mix rather than in the Court's appetite. A Term reads `complete` only once every probed stream was walked to its observed end; until then its figures describe the walked prefix, and for a Term still in progress that end moves as the Court dockets more petitions, so `complete` there means current, not final. Every Term the walk has touched is listed, most recent first._

| Term | filings | ingested (rows) | est. grant rate (weighted) | grants observed (rows) | median days to grant | census |
| --- | --: | --: | --- | --: | --- | --- |
| 2026 | 1694 | 1658 | 1.5% (est. n=610) | 9 | 71 (n=9) | complete |
| 2025 | 4134 | 4134 | 2.7% (est. n=4003) | 107 | 153 (n=107) | complete |
| 2024 | 3858 | 3809 | 3.2% (est. n=3809) | 120 | 137 (n=119) | complete |
| 2023 | 4223 | 4166 | 3.3% (est. n=4166) | 139 | 152 (n=139) | complete |
| 2022 | 4159 | 4117 | 2.6% (est. n=4117) | 109 | 143 (n=109) | complete |
| 2021 | 4899 | 4861 | 3.1% (est. n=4861) | 151 | 163 (n=151) | complete |
| 2020 | 5202 | 5186 | 3.1% (est. n=5267) | 162 | 144 (n=162) | partial |
| 2019 | 1478 | 2008 | 2.9% (est. n=5356) | 158 | 141 (n=158) | complete |
| 2018 | 1593 | 2913 | 2.1% (est. n=7079) | 151 | 152 (n=151) | complete |
| 2017 | 6313 | 6316 | 2.7% (est. n=6269) | 170 | 164 (n=170) | complete |

_Replay/backtest cells: this document sits in the same checkout as the statpack and the same rule applies — anchor only on Term rows strictly preceding `record/context.json`'s `decided_before`, an October Term, because later Terms post-date what you are allowed to know. These rows are keyed on the **docket-number** Term, so your own Term's row already contains your case._

## Not yet included

- **The `granted` / `gvr` split is not comparable across Terms.** The `gvr` label is a forward convention: a resolution recorded before it existed keeps `granted`, and no post-hoc rule separates a merits GVR from a plenary grant without re-resolving the source. OT2023 and OT2024 were resolved into the corpus inside that window, so they carry **zero** GVRs against 30-59% of the grant family in every Term either side of them — ingestion history, not the Court changing behaviour. Read the grant family as one number — the JSON artifacts publish it per Term as `est_grant_family_rate` — because the split is safe within a Term and meaningless between them.
- **Summary reversals are not broken out.** The disposition vocabulary carries a label for them, but no resolver rule reads one off an order, so none is produced and a summary reversal is counted inside the grant family above rather than being missing from it. On mandatory-jurisdiction direct appeals the outcome resolver reads both sides: the vacatur-remand form (`gvr`) and probable jurisdiction noted or postponed to the merits (`granted`), and a summary affirmance (`denied`) or a dismissal for want of a substantial federal question, for want of jurisdiction or as moot (`dismissed`). A split order (affirmed in part and reversed in part, or dismissed in part and affirmed in part) is read on neither side and leaves the docket unresolved.
- **Justice-level statistics.** Vote frequencies, agreement matrices, and opinion authorship are per-justice facts this docket pack does not carry; the statpack's authorship section rolls up the per-opinion record instead.
