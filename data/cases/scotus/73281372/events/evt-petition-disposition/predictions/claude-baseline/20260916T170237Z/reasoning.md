# Rationale for the numbers — Fairfield Sentry v. Citibank NA London (25-1089)

**P(grant) = 0.12; predicted disposition: denied.**

## Inputs read

- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, no CVSG, Term 2025, `signals_observable: true`.
- `record/snapshots/2026-09-15.json`: paid docket 25-1089 from the Second
  Circuit (147 F.4th 136, decided Aug. 5, 2025; rehearing denied Oct. 16,
  2025). Two extensions, petition filed Mar. 13, 2026, response extended to
  May 28, two amicus briefs in support (five former bankruptcy judges; a
  group of investor-creditors), BIO filed May 28, reply June 9, distributed
  June 17 for the Conference of September 28, 2026. Counsel of record: Paul
  Clement for petitioners; Kannon Shanmugam (Citibank respondents) and
  Cleary Gottlieb (HSBC respondents).
- `record/documents/`: `questions-presented.txt`, `petition.txt` (345 pages,
  `truncated: true` — I read the statement and the reasons for granting in
  full; the truncation cut the appendix, not the argument), and
  `brief-in-opposition.txt` (31 pages, complete). Neither had `empty_text`.
- `metrics/statpack.md`: modern-cert disposition table, circuit cut, relist
  and CVSG cuts, and the sal-v4 per-Term band table.

## Anchor

The scored yardstick is the `baseline` band's bracketed `reached` rate over
Terms strictly before OT2025. Pooling the eight prior Term rows the table
renders (OT2017–OT2024) weighted by their `n` gives roughly **5.1%**
(individual Terms run 4.5%–5.9%). The salience version matches
(`sal-v4` in both the context and the table heading), so no fallback was
needed. For context, the relist-count cut puts a once-distributed paid
petition's terminal rate at about 1.7% grant-family for the relist-0 bucket
and about 13% for relist-1, and the CVSG cut at about 35% grant-family
conditional on a CVSG; the Second Circuit's modern-cert grant family is
about 4.9%.

## Adjustments up from ~5%

1. **Petition quality and signalling.** Repeat Supreme Court advocate as
   counsel of record, a 35-page merits-grade petition, two supporting amicus
   briefs including five former SDNY/other bankruptcy judges, and
   respondents who retained top-tier counsel and took a six-week extension
   to answer. Petitions with this profile grant several times more often
   than the baseline band's average, which is dominated by weak paid
   petitions.
2. **Subject matter the Court engages with.** Extraterritoriality is a
   canon the Court has policed repeatedly (Morrison, RJR Nabisco, Nestlé,
   Abitron), often against the Second Circuit specifically; and the Court
   granted Merit Management on the §546(e) safe harbor in 2017.
3. **A plausible error below.** The Second Circuit held that §546(e)
   directly bars common-law claims without discussing Merit Management,
   and reached the §544(b) theory on a ground respondents had not pressed.
   The BIO's answer — that Frost and Grede reached the same bottom line by
   preemption — is a "no outcome-level split" argument, which is fair, but
   the reasoning divergence is real and petitioners' point that preemption
   cannot displace foreign law gives the divergence practical bite in
   Chapter 15 cases.
4. **Stakes.** About $6 billion in claims, and a holding that affects how
   every foreign liquidator uses Chapter 15 in the Second Circuit.

## Adjustments back down

1. **No clean split.** On the extraterritoriality question the Second
   Circuit is the first court of appeals to construe §561(d); Condor (CA5)
   did not address §546(e) or §561(d). On the common-law question the CA7
   and CA8 decisions barred the common-law claims too, just via implied
   preemption. The Court generally waits for a real conflict on a statute
   construed for the first time.
2. **Vehicle problems the BIO documents credibly.** Roughly 300
   consolidated adversary proceedings and 400-plus parties; a district
   court alternative holding that the application here is *domestic* under
   step two of Abitron, which the petition does not squarely engage; BVI
   statutory claims already rejected in the BVI courts; and the
   forum-shopping optics of pressing BVI claims in New York after losing
   at home. The QP as drafted merges two distinct questions, which the
   Court dislikes.
3. **Track record.** The Court has denied every prior Madoff safe-harbor
   petition I am aware of (the Ida Fishman petition in 2015 and the later
   Picard petitions), and in Tribune it called for the SG's views on
   §546(e) and then denied. This is general legal knowledge about other
   decided cases, not information about this petition's outcome.
4. **Long-conference discount.** A first distribution to the September
   conference competes with the summer's backlog; grants from that
   conference are a small fraction of the petitions considered.

## Arithmetic behind 0.12

Decomposed by CVSG path: P(CVSG) ≈ 0.22 with P(grant | CVSG) ≈ 0.35 (the
statpack's CVSG-cut grant family, tempered by the SG's historic support for
the safe harbor); P(no CVSG) ≈ 0.78 with P(grant | no CVSG) ≈ 0.07. That
yields ≈ 0.077 + 0.055 ≈ 0.13; I shade to **0.12** for the vehicle problems.
This is more than double the band anchor, which is the size of adjustment I
think the counsel/amici/subject-matter signals justify without a split.

## Other claims

- `relist-increment` 0.40: sum of the CVSG path (~0.22, since a CVSG
  produces a later redistribution) and an ordinary relist without a CVSG
  (~0.18). Higher than the population's roughly one-in-four chance of any
  relist because the petition is one a Justice may want to look at twice.
- `cvsg-increment` 0.22: see above; the Model Law / Executive-interest
  angle and the Tribune precedent for inviting the SG on §546(e) push it
  well above the docket's ~1% CVSG incidence, but there is no federal party
  and the Court has not invited the SG on prior Madoff petitions.
- `summary-disposition-route` 0.05 (conditional on grant): no intervening
  decision to GVR against; too complex for a per curiam.
- `dissent-from-denial` 0.05 (conditional on denial): commercial
  bankruptcy denials very rarely draw a noted dissent or statement.
- `big_case_score` 0.45: high dollar stakes and real doctrinal importance
  for cross-border insolvency, but a technical dispute with limited
  general-public salience.

## Where to discount me

- My read that the common-law-claims holding is the stronger hook rests on
  the parties' characterizations of the Second Circuit opinion; I did not
  read the opinion itself (the citation lookup on CourtListener returned no
  opinion text, and the petition appendix was outside the truncated text).
- The CVSG number is the softest input: it drives much of the grant
  probability and rests on analogy (Tribune; Model Law interest) rather
  than on any signal in this docket.
- I carry no knowledge of this petition's disposition; the docket is
  pending (CourtListener's docket record shows no termination date, and
  the snapshot ends at the June 17 distribution). Nothing outcome-revealing
  surfaced in retrieval.
- The `fedcourts query` citation lookup returned no priors (the citation
  column is sparse), so corpus priors contributed nothing beyond the
  statpack.
